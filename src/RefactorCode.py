import math

# Deletes comment and joins multiline instructions, but only the one created
# with a line_continuation_symbol
def refactor(lang, in_file, out_file):
    in_string = in_file.read()
    
    index_start = 0

    while(True):
        (index_s, symbol_s), (index_mc, symbol_mc), index_c, index_l = _find_indices(lang, index_start, in_string)

        # If they are all math.inf that means none of the indices has been found: exit the loop
        if index_s == math.inf and index_mc == math.inf and index_c == math.inf and index_l == math.inf:
            break

        # We get the first of the four
        index_start_codeforming = min(index_s, index_mc, index_c, index_l)
        index_closing = index_start_codeforming + 1

        # We select the case we're in.
        # String literal
        if index_s == index_start_codeforming:
            while(True):
                index_closing = in_string.find(lang.string_literal_symbol[symbol_s], index_closing)

                # If we don't find the matching symbol there is an error in the source code
                if(index_closing == -1):
                    raise Exception("ERROR. NO CLOSING STRING SYMBOL")

                # If the found symbol is not an escape sequence we consider it valid
                if(in_string[index_closing - 1] != lang.escape_symbol):
                    break
                # Else we skip the symbol and try to find it later in the string
                index_closing += 1
            # Start over from the next character after the closing quote
            index_start = index_closing + 1
            # No computation is needed with an inline string, we need the closing symbol so that we look for comments
            # after the string, we just add 1 to index_closing so that we can start from the next char in the next iteration
            pass

        # Multiline comment
        elif index_mc == index_start_codeforming:
            # The first multiline_comment_closing_symbol that appears is considered valid
            index_closing = in_string.find(lang.multiline_comment_closing_symbol[symbol_mc], index_closing)

            if(index_closing == -1):
                raise Exception("ERROR. NO CLOSING COMMENT")
            
            index_closing += len(lang.multiline_comment_closing_symbol[0])
            # Cut the comment, but inserts a space between the two valid parts
            in_string = in_string[: index_start_codeforming] + " " + in_string[index_closing: ]
            # Start over from the index where we started codeforming
            index_start = index_start_codeforming

        # Inline comment
        elif index_c == index_start_codeforming:
            # The first \n that appears ends the inline comment.
            index_closing = in_string.find("\n", index_closing)

            # It's not an error if we don't have a \n for example in the last line of the document
            if(index_closing == -1):
                index_closing = len(in_string)

            # Skips the \n
            index_closing += 1
            # Cuts the comment
            in_string = in_string[: index_start_codeforming] + " " + in_string[index_closing: ]
            # Start over from the index where we started codeforming
            index_start = index_start_codeforming
            
        # Line continuation
        else:
            # Skip the \ and the \n (that's the reason of the number 2)
            in_string = in_string[: index_start_codeforming] + in_string[index_start_codeforming + 2: ]
            index_start = index_start_codeforming
    
    # We want to update the file, so we come back to the beginning and write there
    out_file.seek(0)
    # Finally we write on file
    out_file.write(in_string)
    # Need to truncate or else there would be the data from the previous code manipulation
    out_file.truncate()


def _set_negative_to_inf(number):
    return number if number >= 0 else math.inf

# Finds the indices
def _find_indices(lang, index_start, in_string):
    # The following three long lines of code means:
    # Find which is the first symbol among the list defined in Language.py for the specified syntax element
    # We will store both the index of said symbol in the in_string and the index in the list in Language.py
    # Inline string
    index_s, index_symbol_s = min([(in_string.find(symbol, index_start), i) for i, symbol in enumerate(lang.string_literal_symbol)], key = lambda index_symbol: index_symbol[0])
    # Multiline comment
    index_mc, index_symbol_mc = min([(in_string.find(symbol, index_start), i) for i, symbol in enumerate(lang.multiline_comment_opening_symbol)], key = lambda index_symbol: index_symbol[0])
    # Inline comment, we will not use index_symbol_c because whatever the symbol for the comment is, it will end with the first \n
    index_c, _ = min([(in_string.find(symbol, index_start), i) for i, symbol in enumerate(lang.inline_comment_symbol)], key = lambda index_symbol: index_symbol[0])
    # Line continuation symbol
    index_l = in_string.find(lang.line_continuation_symbol + "\n", index_start)
    
    # We make the -1 to become inf so that calculations of min are easier
    index_s = _set_negative_to_inf(index_s)
    index_mc = _set_negative_to_inf(index_mc)
    index_c = _set_negative_to_inf(index_c)
    index_l = _set_negative_to_inf(index_l)

    return (index_s, index_symbol_s), (index_mc, index_symbol_mc), index_c, index_l


# Strips file: removes blank lines and both trailing and leading white spaces
def strip_file(input, output):
    final_string = ""
    for line in input:
        line = line.strip()
        final_string += line + "\n" if line else ""
        
    output.write(final_string)


# Given the file name, it creates a new file inside the temp_files directory
# where there are no preprocessor instructions: all of them are put inside
# a list called preprocessor_directives and returned: it will be written as header inside the out_file
# in Format.py
def retrieve_preprocessor_directives(lang, in_file, out_file):
    preprocessor_directives = []
    multiline_preprocessor = False

    for line in in_file:
        line = line.strip()

        if line:
            #If the line starts with an hash then it's a preprocessor directive
            if line[0] == '#': # Temporary hardcoded symbol
                preprocessor_directives.append(line)
                #we've found a multiline preprocessore directive
                if(line[-1] == lang.escape_symbol):
                    multiline_preprocessor = True
            elif multiline_preprocessor:
                preprocessor_directives.append(line)
                #multiline preprocessor directive finished
                if(line[-1] != lang.escape_symbol):
                    multiline_preprocessor = False
            else:
                out_file.write(line + '\n')

    return preprocessor_directives