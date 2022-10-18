import random
import string
from random import randint
import Util

IMAGE_SIZE = 128
WHITE = 255
BLACK = 0

def format_file(lang, header, path, black_white_img):
    with open(lang.output_file_name + lang.file_name, "r") as input_file:
        with open(path + "out_" + lang.file_name, "w") as out_file:
            #if the header is not empty then writes it onto the output file
            if header: _write_header(header, out_file)
            tokens_to_write = _image_text(lang, black_white_img, input_file, out_file)
            _final_text(lang, out_file, tokens_to_write)


def _write_header(header, out_file):
    for line in header:
        out_file.write(line + '\n')


def _image_text(lang, black_white_img, input_file, out_file):
    '''
    image_text is the function which writes to out_file the code with the image shape
    Returns the rest of the tokens (if any) and the number of characters of these remaining tokens.
    '''
    tokens_to_write = _get_tokens_file(lang, input_file)

    for row_img in range(IMAGE_SIZE):
        out_string = ""

        # Divides the image in black and white segments (and retrieve the raw number of black, writable pixels)
        black_segments, white_segments = _separate_img(black_white_img, row_img)
        # Get a bunch of atomic tokens (names of variables, functions, operators and so on)
        # This list of tokens will have a grand number of characters >= n_chars_to_write
        counter_white_segment = 0

        # If the first segment is white, we write the white segment as a sequence of white spaces
        if black_white_img[row_img][0] == WHITE:
            out_string += ' ' * white_segments[counter_white_segment]
            counter_white_segment += 1

        for segment in black_segments:
            # retrieves the number of tokens that will be written in the current segment and the number of blank spaces (that could not be filled)
            token_counter, char_to_write_this_segment = _get_tokens_segment(lang, segment, tokens_to_write)
            out_string += _format_out_string(lang, segment - char_to_write_this_segment, token_counter, char_to_write_this_segment, tokens_to_write)

        
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


def _get_tokens_file(lang, input_file):
    '''
    Reads all the lines in the file and returns the tokens
    '''

    tokens_to_write = []
    lines = input_file.read().split("\n")

    for line in lines:
        # Separates the line that has just been read in atomic tokens
        if line:
            tokens_to_write += _handle_line(lang, line)
    
    return tokens_to_write


def _get_tokens_segment(lang, segment, tokens_to_write):
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

    # Remove a possible trailing space
    if token_counter > 0 and tokens_to_write[token_counter - 1][-1] == ' ':
        tokens_to_write[token_counter - 1] = tokens_to_write[token_counter - 1][: -1]
        #if we have generated an empty string as token we remove it
        if not tokens_to_write[token_counter - 1]:
            tokens_to_write = tokens_to_write[: token_counter - 1] + tokens_to_write[token_counter: ]
            token_counter -= 1
        char_per_segment -= 1

    return (token_counter, char_per_segment)


def _final_text(lang, out_file, tokens_to_write):
    '''
    final_text writes to out_file the final part of input_file that couldn't fit "inside the image" part
    it prints the text as a rectangle of width = DIMENSIONE_IMMAGINE
    '''
    while tokens_to_write:
        out_string = ""

        #Puts all the possible tokens inside out_string until IMAGE_SIZE characters are reached, at that point we put a \n
        token_counter, char_to_write_this_segment = _get_tokens_segment(lang, IMAGE_SIZE, tokens_to_write)
        out_string += _format_out_string(lang, IMAGE_SIZE - char_to_write_this_segment, token_counter, char_to_write_this_segment, tokens_to_write)

        #Remove the tokens that are gonna be written onto the file in this iteration
        tokens_to_write = tokens_to_write[token_counter:]

        #Writes out_string on to the output file
        out_file.write(out_string + '\n')


def _handle_line(lang, line):
    # Sobstitute the '\n' at the end of the string with a space if the last characters represent a keyword to avoid the concatenation of 
    # what should be different tokens
    if any([keyword == line.split()[-1] for keyword in lang.keywords]):
        line += ' '

    # Delete trailing spaces and \n
    line = line.strip('\n')

    # Separate line in atomic tokens
    tokens = _separate_line(lang, line)

    # Returns the atomic tokens
    return tokens


def _separate_line(lang, line):

    # Remove possible white spaces. Has to be called after an operator or after another space
    def remove_possible_whitespaces(line):
        while line:
            if line[0] == ' ':
                line = line[1: ]
            else:
                break
        return line

    tokens = []
    
    while line:
        first_char = line[0]

        # If we're dealing with a string
        if any([first_char == symbol for symbol in lang.string_literal_symbol]):
            # Finds the index of the string literal symbol that we're using now
            index_symbol = lang.string_literal_symbol.index(first_char)
            # Finds the correspondent closing symbol
            index_closed_quote = Util.index_ending_inline_string(lang, lang.string_literal_symbol[index_symbol], line, 0)
            # Adds the entire string
            tokens.append(line[: index_closed_quote + 1])
            # Updates line
            line = line[index_closed_quote + 1: ]

        # Verify if this blank space is useful or not (it's useless if it's before an operator or another space). If it's useless, delete it
        elif first_char == ' ' and len(line) > 1 and line[1] in (lang.operators):
            line = line[1: ]

        # Handle operators of all length
        elif first_char in lang.operators:
            counter_char = 1
            # Until counter_char is less than the length of the line and
            # the characters until counter_char are an operator char we move on to the next char
            while counter_char < len(line) and line[: counter_char + 1] in lang.operators:
                counter_char += 1
            
            tokens += (line[: counter_char])
            line = line[counter_char: ]

            # Removes the possible whitespaces after an operator
            line = remove_possible_whitespaces(line)

        # if it's a symbol we have to scan every single character until we arrive to the end of the string or to another operator (or space)
        else:
            counter_char = 0
            while counter_char < len(line) and line[counter_char] not in (lang.operators):
                counter_char += 1

            # Join the white space with the token to avoid having three spaces straight in the out file
            # (this can happen when we add the white spaces between tokens when we format the out string)
            if counter_char < len(line) and line[counter_char] == ' ':
                counter_char += 1

            # Removes possible whitespaces after the whitespace included in the token before
            line = remove_possible_whitespaces(line)
            
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

    return (black_list, white_list)


def _format_out_string(lang, not_filled_spaces, num_token_segment, tot_chars_to_write, tokens_to_write):

    '''
    Returns the formatted string of the current segment with the possible comments
    '''

    out_string = ""

    # if num_token_segment = 0 then we generate one single comment
    if num_token_segment == 0:
        out_string = _fill_gaps(lang, not_filled_spaces)

    # else if the number of characters to write is less than the number of not filled spaces we put a leading and a trailing comment
    elif tot_chars_to_write < not_filled_spaces or num_token_segment == 1:
        len_leading_comment = not_filled_spaces // 2
        # add leading
        out_string = _fill_gaps(lang, len_leading_comment)
        # add tokens
        for token in range(num_token_segment):
            out_string += tokens_to_write[token]
        # add trailing
        out_string += _fill_gaps(lang, not_filled_spaces - len_leading_comment)

    # else it generates n (= num_token_segment - 1) comments (or spaces) that it will randomly distribute starting from the beginning token or from the ending one
    # This case covers the case where not_filled_spaces < num_token_segment where we should just generate n = not_filled_spaces blank spaces to be put between tokens
    else:
        min_length_comment = not_filled_spaces // (num_token_segment - 1)
        remainder = not_filled_spaces % (num_token_segment - 1)
        # It generates the gaps: the number of gaps will be num_token_segment - 1 if not_filled_spaces // (num_token_segment - 1) > 0, else the number of gaps is n = not_filled_spaces 
        gaps = [lang, _fill_gaps(min_length_comment + (1 if i in range(remainder) else 0)) for i in range(num_token_segment - 1 if min_length_comment != 0 else not_filled_spaces)]

        # It randomly choose the starting index to put the gaps
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
def _fill_gaps(lang, n_chars) -> str:
    if n_chars < 4:
        return ' ' * n_chars
    else:
        ret_string = lang.multiline_comment_opening_symbol
        for _ in range(n_chars - 4):
            ret_string += random.choice(string.ascii_letters)
        ret_string += lang.multiline_comment_closing_symbol
        return ret_string


def _handle_strings(str, n_exceeding_chars, lang):
    # Separate string in atomic tokens: single chars, escape sequences and format specifiers
    string_tokens = _tokenize_string(str, lang)
    return lang.separate_in_multiline_strings(str, string_tokens, len(str) - n_exceeding_chars)


# Separate a string into atomic tokens: characters, format specifiers and escaping sequences
def _tokenize_string(str, lang):
    '''
    given a string str, it divides the string in atomic tokens that can be used like the following 
    example in C++: '"' 'h' 'e' 'l' 'l' 'o' '\\n' '"' which is equal to "hello\\n"
    '''
    string_tokens = []

    while str:
        token_char_counter = 1
        #Check if we have a format specifier
        if str[0] == '%':
            while(str[token_char_counter] in lang.format_specifiers):
                token_char_counter += 1
        #Check if we have an escape sequence
        elif str[0] == '\\':
            token_char_counter = 2

        #Otherwise we have a normal character that can be appended as a single token; token_char_counter already equals 1
        string_tokens.append(str[ :token_char_counter])
        str = str[token_char_counter:]

    return string_tokens