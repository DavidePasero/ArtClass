import random
import string
from random import randint
from Comments import find_match_quotes

IMAGE_SIZE = 128
WHITE = 255
BLACK = 0

def format_file(lang, header, path, black_white_img):
    with open(lang.output_file_name + lang.file_name, "r") as input_file:
        with open(path + "out_" + lang.file_name, "w") as out_file:
            #if the heaser is not empty then writes it onto the output file
            if header: _write_header(header, out_file)
            tokens_to_write = _image_text(black_white_img, input_file, out_file, lang)
            _final_text(input_file, out_file, tokens_to_write, lang)

def _write_header(header, out_file):
    for line in header:
        out_file.write(line + '\n')

def _image_text(black_white_img, input_file, out_file, lang):
    '''
    image_text is the function which writes to out_file the code with the image shape
    Returns the rest of the tokens (if any) and the number of characters of these remaining tokens.
    '''
    tokens_to_write = []

    for row_img in range(IMAGE_SIZE):
        out_string = ""

        # Divides the image in black and white segments (and retrieve the raw number of black, writable pixels)
        n_black_pixels, black_segments, white_segments = _separate_img(black_white_img, row_img)
        # Get a bunch of atomic tokens (names of variables, functions, operators and so on)
        # This list of tokens will have a grand number of characters >= n_chars_to_write
        tokens_to_write = _get_tokens_row(input_file, tokens_to_write, n_black_pixels, lang)
        counter_white_segment = 0

        # If the first segment is white, we write the white segment as a sequence of white spaces
        if black_white_img[row_img][0] == WHITE:
            out_string += ' ' * white_segments[counter_white_segment]
            counter_white_segment += 1

        for segment in black_segments:
            # retrieves the number of tokens that will be written in the current segment and the number of blank spaces (that could not be filled)
            token_counter, char_to_write_this_segment = _get_tokens_segment(segment, tokens_to_write, lang)
            out_string += _format_out_string(segment - char_to_write_this_segment, token_counter, char_to_write_this_segment, tokens_to_write)

        
            # We remove from tokens_to_write all the tokens we will write onto the file
            tokens_to_write = tokens_to_write[token_counter:]
            
            # We add all the white spaces after the current black segment
            if counter_white_segment < len(white_segments):
                out_string += ' ' * white_segments[counter_white_segment]
                counter_white_segment += 1

        # We write onto the file the generated string
        out_file.write(out_string + '\n')
        
        # next row img
    return tokens_to_write # returns possible remaining tokens

def _get_tokens_row(input_file, tokens_to_write, n_black_pixels, lang):
    '''
    Reads lines from input_file until the number of read characters is greater or equal to the number of black pixels in this row
    returns (tokens_to_write, end_of_file_reached)
    '''

    #Calculate the number of characters left in tokens_to_write. If it's greater than n_black_pixels we don't read the next line and return
    num_chars_to_write = sum([len(token) for token in tokens_to_write])
    if num_chars_to_write >= n_black_pixels:
        return tokens_to_write

    while True:
        try:
            # Reads the next line in input_file
            line = next(input_file)

            # Separates the line that has just been read in atomic tokens
            tokens, num_chars = _handle_line(line, lang)

            # if tokens isn't empty then we append tokens to tokens_to_write.
            # if the total number of characters in tokens_to_write is greater or equal than n_black_pixels then return
            if tokens: 
                tokens_to_write += tokens
                if num_chars_to_write + num_chars >= n_black_pixels:
                    return tokens_to_write
                else:
                    num_chars_to_write += num_chars
        # If a StopIteration has been raised then return with the eof flag set to True
        except StopIteration:
            return tokens_to_write

def _get_tokens_segment(segment, tokens_to_write, lang):
    '''
    Given a (black) segment, it returns the number of tokens to write and the number of blank spaces (to be filled with comments or spaces)
    '''

    token_counter = 0
    char_per_segment = 0

    #Remove a possible leading white space
    if len(tokens_to_write) > 0 and tokens_to_write[0][0] == ' ':
        tokens_to_write[0] = tokens_to_write[0][1: ]
        if not tokens_to_write[0]:
            tokens_to_write[1: ]

    # if token_counter is in bounds and the chars counter + the length of the next token in less than segment, then we can
    # increment these two counters and pass to the next one
    while (token_counter < len(tokens_to_write)) and (char_per_segment + len(tokens_to_write[token_counter]) <= segment):
        char_per_segment += len(tokens_to_write[token_counter])
        token_counter += 1

    # If we couldn't fill all the black pixels and we have a string at the ending, we can modify the string
    # so that maybe it can fit in the remaining spaces
    # we put segment -1 because this trick requires at least two spaces to like so: ""
    if token_counter < len(tokens_to_write) and char_per_segment < segment - 1 and tokens_to_write[token_counter][0] == '\"':
        tokenized_string = _handle_strings(tokens_to_write[token_counter], (char_per_segment + len(tokens_to_write[token_counter]) - segment), lang)
        char_per_segment += len(tokenized_string[0])
        # we divide the string in to two strings
        tokens_to_write[token_counter : token_counter + 1] = tokenized_string
        token_counter += 1

    #Remove a possible trailing space
    if token_counter > 0 and tokens_to_write[token_counter - 1][-1] == ' ':
        tokens_to_write[token_counter - 1] = tokens_to_write[token_counter - 1][: -1]
        #if we have generated an empty string as token we remove it
        if not tokens_to_write[token_counter - 1]:
            tokens_to_write = tokens_to_write[: token_counter - 1] + tokens_to_write[token_counter: ]
            token_counter -= 1
        char_per_segment -= 1

    return (token_counter, char_per_segment)

def _final_text(input_file, out_file, tokens_to_write, lang):
    '''
    final_text writes to out_file the final part of input_file that couldn't fit "inside the image" part
    it prints the text as a rectangle of width = DIMENSIONE_IMMAGINE
    '''
    while True:
        out_string = ""
        #Gets all the possible tokens from input_file until we reach IMAGE_SIZE characters or the end of file
        tokens_to_write = _get_tokens_row(input_file, tokens_to_write, IMAGE_SIZE, lang)
        
        #se siamo arrivati alla fine del file usciamo
        if not tokens_to_write: break

        #Puts all the possible tokens inside out_string until IMAGE_SIZE characters are reached, at that point we put a \n
        token_counter, char_to_write_this_segment = _get_tokens_segment(IMAGE_SIZE, tokens_to_write, lang)
        out_string += _format_out_string(IMAGE_SIZE - char_to_write_this_segment, token_counter, char_to_write_this_segment, tokens_to_write)

        #Remove the tokens that are gonna be written onto the file in this iteration
        tokens_to_write = tokens_to_write[token_counter:]

        #Writes out_string on to the output file
        out_file.write(out_string + '\n')

def _handle_line(line, lang):
    # Sobstitute the '\n' at the end of the string witha space if the last characters represent a keyword to avoid the concatenation of 
    # what should be different tokens
    # THIS HAS TO BE MODIFIED BECAUSE IF THE LAST CHARACTERS ARE INSIDE OF A STRING (IT HAS TO BE A MULTILINE STRING NECESSARILY) THEN IT SHOULD
    # NOT ADD A SPACE
    if any([keyword + '\n' in line for keyword in lang.keywords]):
        line[-1] = ' '

    #Delete trailing spaces and \n
    line = line.strip('\n')

    #Separate line in atomic c++ tokens
    tokens = _separate_line(line, lang)

    #Returns the atomic tokens and the total number of characters
    return tokens, sum([len(token) for token in tokens])

def _separate_line(line, lang):
    tokens = []
    
    while line:
        first_char = line[0]

        # If we're dealing with a string
        if first_char == '\"':
            index_closed_quote = find_match_quotes(line, 0)
            tokens.append(line[: index_closed_quote + 1])
            line = line[index_closed_quote + 1: ]

        # Verify if this blank space is useful or not (it's useless if it's before an operator or another space). If it's useless, delete it
        elif first_char == ' ' and len(line) > 1 and line[1] in (lang.operators + [' ']):
            line = line[1: ]

        # Handle operators of all length
        elif first_char in lang.operators:
            counter_char = 1
            # Until counter_char is less than the length of the line and
            # the characters until counter_char are an operator char we move on to the next char
            while counter_char < len(line) and line[counter_char] in lang.operators:
                counter_char += 1
            
            # Goes back until we find an actual operator
            while counter_char > 1 and line[: counter_char] not in lang.operators:
                counter_char -= 1
            
            tokens.append(line[: counter_char])
            line = line[counter_char: ]

            #Remove possible white space after an operator
            if len(line) > 0 and line[0] == ' ':
                line = line[1: ]
        #if it's a symbol we have to scan every single character until we arrive to the end of the string or to another operator (or space)
        else:
            counter_char = 0
            while counter_char < len(line) and line[counter_char] not in (lang.operators + [' ']):
                counter_char += 1

            # Join the white space with the token to avoid having three spaces straight in the out file
            # (this can happen when we add the white spaces between tokens when we format the out string)
            if counter_char < len(line) and line[counter_char] == ' ':
                counter_char += 1
            
            tokens.append(line[: counter_char])
            line = line[counter_char: ]

    return tokens

def _separate_img(img, row):
    black_list = []
    white_list = []

    black_counter = 0
    white_counter = 0

    for j in range(IMAGE_SIZE):
        # If the following is a black pixel...
        if img[row][j] == BLACK:
            black_counter += 1 # increment the counter
            if white_counter > 0: # If white_counter > 0 (there are white pixels before the black ones), append white_counter to white list
                white_list.append(white_counter)
                white_counter = 0
        # Same thing as the black one
        else:
            white_counter += 1
            if black_counter > 0:
                black_list.append(black_counter)
                black_counter = 0
    
    # We add them only if they're not 0
    if black_counter != 0: black_list.append(black_counter)
    if white_counter != 0: white_list.append(white_counter)

    #Total number of black pixels in this row
    n_of_black_pixels = sum(black_list)

    return (n_of_black_pixels, black_list, white_list)

#Sometimes it happens that when we have an else statement with only one instruction we write code like the following:
#else
#   statement ...
#This can lead to an error in the output code, where we have: elsestatement...
#To avoid this, we put a blank space after the else
#def _handle_keywords(line):
    # DA MODIFICARE: VISITA DAL FONDO DELLA STRINGA E CERCO IN KEYWORDS
#    if "else\n" in line:
#        idx = line.index("else")
#        line = line[ :idx + 4] + ' ' + line[idx + 4: ]
#    return line

def _format_out_string(not_filled_spaces, num_token_segment, tot_chars_to_write, tokens_to_write):

    '''
    Returns the formatted string of the current segment with the possible comments
    '''

    out_string = ""

    #if num_token_segment = 0 then we generate one single comment
    if num_token_segment == 0:
        out_string = _fill_gaps(not_filled_spaces)
    #else if the number of characters to write is less than the number of not filled spaces we put a leading and a trailing comment
    elif tot_chars_to_write < not_filled_spaces or num_token_segment == 1:
        len_leading_comment = not_filled_spaces // 2
        #add leading
        out_string = _fill_gaps(len_leading_comment)
        #add tokens
        for token in range(num_token_segment):
            out_string += tokens_to_write[token]
        #add trailing
        out_string += _fill_gaps(not_filled_spaces - len_leading_comment)
    #else we generate n (= num_token_segment - 1) comments (or spaces) that we will randomly distribute starting from the beginning token or from the ending one
    #This else cover the case where not_filled_spaces < num_token_segment where we should just generate n = not_filled_spaces blank spaces to be put between tokens
    else:
        min_length_comment = not_filled_spaces // (num_token_segment - 1)
        remainder = not_filled_spaces % (num_token_segment - 1)
        #we generate the gaps: the number of gaps will be num_token_segment - 1 if not_filled_spaces // (num_token_segment - 1) > 0, else the number of gaps is n = not_filled_spaces 
        gaps = [_fill_gaps(min_length_comment + (1 if i in range(remainder) else 0)) for i in range(num_token_segment - 1 if min_length_comment != 0 else not_filled_spaces)]

        #we randomly choose the starting index to put the gaps
        comments_starting_index = randint(0, num_token_segment - len(gaps) - 1)
        for n_token in range(num_token_segment):
            out_string += tokens_to_write[n_token]
            
            #add the gap after the token
            if n_token >= comments_starting_index and n_token - comments_starting_index < len(gaps):
                out_string += gaps[n_token - comments_starting_index]

    return out_string

# When printing the line, it can be that not all the black spaces are covered by the characters
# This can generate not only inconsistence inside the segment, but also in the next segments in the same row
# To solve this we generate comment of at least 4 chars /**/ to fill the gaps
# If it's less than 4 chars, we only generate n spaces
def _fill_gaps(n_chars) -> string:
    if n_chars < 4:
        return ' ' * n_chars
    else:
        ret_string = "/*"
        for _ in range(n_chars - 4):
            ret_string += random.choice(string.ascii_letters)
        ret_string += "*/"
        return ret_string

def _handle_strings(str, n_exceeding_chars, lang):
    # Separate string in atomic tokens: single chars, escape sequences and format specifiers
    string_tokens = _tokenize_string(str, lang)
    return lang.handle_multiline_strings(str, string_tokens, len(str) - n_exceeding_chars)

# Separate a string into atomic tokens: characters, format specifiers and escaping sequences
def _tokenize_string(str, lang):
    '''
    given a string str, it divides the string in atomic tokens that can be used like the following: '"' 'h' 'e' 'l' 'l' 'o' '\\n' '"' which is equal to "hello\\n"
    '''
    string_tokens = []

    while str:
        token_char_counter = 1
        #Check if we have a format specifier
        if str[0] == '%':
            while(str[counter_char] in lang.format_specifiers):
                counter_char += 1
        #Check if we have an escape sequence
        elif str[0] == '\\':
            token_char_counter = 2

        #Otherwise we have a normal character that can be appended as a single token; token_char_counter already equals 1
        string_tokens.append(str[ :token_char_counter])
        str = str[token_char_counter:]

    return string_tokens