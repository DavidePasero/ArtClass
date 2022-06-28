import string
import os
import Temp_Files

def delete_comments(lang, path):
    with open(path + lang.file_name, "r") as file_input:
        # Creates the temp_files/ dir if it doesn't exist
        try:
            os.mkdir("temp_files/")
        except FileExistsError:
            pass

        with open(Temp_Files.NO_COMMENTS + lang.file_name, "w") as output:

            multiline_comment = False

            for line in file_input:
                line = line.strip()
                #Delete comments
                multiline_comment, line = _delete_multiline_comment(line, multiline_comment, lang)
                line = _delete_inline_comment(line, lang)
                #if line is not empty we write it onto the file
                if line:
                    output.write(line + '\n')

def _delete_inline_comment(line, lang) -> string:
    '''
    Deeletes an inline comment introduced by // and returns the decommented string
    '''

    if lang.inline_comment_symbol in line:
        comment_index = line.index(lang.inline_comment_symbol)
        #inside è un booleano e indica se il commento è dentro le virgolette o no
        (inside, index_closedquotes) = _is_inside_string(line, comment_index, lang)

        #If it's not inside quotes then we simply delete the comment
        if not inside:
            line = line[: comment_index]
        #If it's inside quotes then the '//' that we found is not a comment, but there can be another comment in this line
        else:
            line = line[: index_closedquotes + 1] + _delete_inline_comment(line[index_closedquotes + 1: ], lang)
        
    return line

#Returns (multiline_comment, line_without_comment)
def _delete_multiline_comment(line, multiline_comment, lang) -> tuple:
    '''
    Deletes a commented part of the line in a multiline comment context
    '''
    
    #multiline_comment is a boolean variable that tells us if we are inside a multiline comment
    #that means that if in the line before there was a /* without a closing */ multiline_comment = True
    if multiline_comment:
        # If there is a closing comment */ in this line we delete all the chars until line[line.index("*/") + 1]
        if lang.multiline_comment_closing_symbol in line:
            line = line[line.index(lang.multiline_comment_closing_symbol) + 2:]
            multiline_comment = False
        # else, if there is no closing comment expression: */ we delete the whole line
        else:
            line = ""
    else:
        # If we havent't found a /* yet (multiline_comment = false) we see if there is a /* in the current line
        if lang.multiline_comment_opening_symbol in line:
            comment_index = line.index(lang.multiline_comment_opening_symbol)
            
            # We see whether the /* which we found is inside double quotes or not
            (inside, index_closedquotes) = _is_inside_string(line, comment_index, lang)

            # If it is inside we still have to check the rest of the line:
            # maybe there is a multiline comment later in the line
            if inside:
                # we call delete_multiline_comment recoursively from the index of the closing quotes + 1 until the end of the line
                multiline_comment, rest = _delete_multiline_comment(line[index_closedquotes + 1: ], False, lang)
                line = line[ : index_closedquotes + 1] + rest
            else:
                # If the /* expression that we found is not inside a string ("/*" <-- like this) we still have to check
                # wheteher or not it is inside an inline comment (//.../*... <-- like this), in this case, it doesn't represent
                # a multiline comment
                #
                # In order to know if our /* expression is inside an inline comment we call the delete_inline_comment() function
                # from the start index (0) to the /* expression index of our variable line.
                # If the returned line is modified our /* is inside an inline comment, hence /* does not represent a comment
                # and we're sure that there won't be anymore /* in the rest of the line (because we know that this was the first
                # and it's already inside an inline comment)
                #
                # After this call of delete_multiline_comment there will be a call to delete_inline_comment which will delete
                # the inline comment (we don't have to do it know), that's why there's no else clause
                #
                # If our /* is not inside an inline comment, we have to verify if it closes in the same line (/*.....*/ <-- like this)
                # (so multiline_comment will still be False) or if it actually is a multiline comment.
                if line[: comment_index] == _delete_inline_comment(line[: comment_index], lang):
                    try:
                        closing_comment_index = line[comment_index: ].index(lang.multiline_comment_closing_symbol)
                        # We remove the comment "inline" /*...*/ comment, but maybe later in the line there is a multiline comment
                        # We call delete_multiline_comment recoursively giving as parameter the same "line" but without the inline /*...*/ comment
                        # that we've just deleted 
                        # +2 means we include (to delete) the comment expression characters
                        line = line[: comment_index] + line[comment_index + closing_comment_index + 2: ]
                        return _delete_multiline_comment(line, False, lang)
                    except ValueError:
                        #if there's no */ inside this line we have a multiline_comment, we just delete everything after and included /*
                        return (True, line[: comment_index])
        else:
            # There's not a /* inside this line, multiline_comment = False and we return the same line
            return (False, line)


    return (multiline_comment, line)

# Returns (result, match)
def _is_inside_string(line, index, lang) -> tuple:
    '''
    Returns if specified index is inside a string, if True, returns index_match
    '''

    if '\"' in line:
        index_quotes = line.index('\"')

        # If the \" we've found is a single independent quote, like: \" we skip
        # and try to see if there are other strings later in the line where index could be or not inside
        if index_quotes != 0 and line[index_quotes - 1] == lang.inline_comment_symbol:
            return _is_inside_string(line[index_quotes + 1: ], index - (index_quotes + 1), lang)

        index_match = find_match_quotes(line, index_quotes)

        # If index is before index_quotes then it certainly isn't inside a string
        # If index_quotes < index < index_match then it's inside a string: it's not a real comment, just a part of a string
        # else, if index > index_match we don't know anything, maybe, later in the line, index is inside another string
        # and we have to check for that by calling this same function recoursively
        if index < index_quotes:
            return (False, 0)
        elif index > index_quotes and index < index_match:
            return (True, index_match)
        else:
            len_first_substring  = index_match + 1
            (result, match) = _is_inside_string(line[index_match + 1 : ], index - len_first_substring, lang)
            return (result, match + len_first_substring)
    else:
        return (False, 0)
    

def find_match_quotes(line, index_quotes) -> int:
    for idx, c in enumerate(line):
        # if idx != index_quotes (they're not the same double quotes) and before this double quotes at index idx doesn't have
        # a backslash before (\" <-- like this) then we've found the match
        if c == '\"' and idx != index_quotes and line[idx - 1] != '\\':
            return idx
    
    # If we've explored the whole line and we haven't found a closing quote, then that quote at index index_quotes
    # was a single independet quote like \"
    return -1
