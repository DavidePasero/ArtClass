from abc import ABC, abstractmethod
import string
import Temp_Files
import Comments
import Preprocessor
import Format

class Language:

    def __init__(self):
        pass

    # This variable will indicate the file which Format.py will open in read mode
    @property
    @abstractmethod
    def output_file_name(self):
        pass

    # It will be overloaded with a list containing the operators for that language
    @property
    @abstractmethod
    def operators(self):
        pass
    
    # All the keywords of the various languages
    @property
    @abstractmethod
    def keywords(self):
        pass

    # It will be overloaded with a list containing the format specifiers for strings for that language
    @property
    @abstractmethod
    def format_specifiers(self):
        pass

    # It will be overloaded with the symbol that the language uses to represent an inline comment
    @property
    @abstractmethod
    def inline_comment_symbol(self):
        pass

    # It will be overloaded with the symbol that the language uses to represent the beginning of a multiline comment
    @property
    @abstractmethod
    def multiline_comment_opening_symbol(self):
        pass
    
    # It will be overloaded with the symbol that the language uses to represent the ending of a multiline comment
    @property
    @abstractmethod
    def multiline_comment_closing_symbol(self):
        pass

    # Self explaining name: in C++, for example, you only need to add the two "" to create a multiline string:
    # for example if you have: "hello" you can write "hel"   "lo" which is exactly the same
    @property
    @abstractmethod
    def num_chars_to_add_to_multiline_strings(self):
        pass
    
    # Multiline strings are different among different languages: some of them use concatenation,
    # others, like cpp, use the following syntax: "...str..." "...str2..."
    # and other use the triple quotes: """ ... ... ... """
    @abstractmethod
    def handle_multiline_strings(self, str: string)->list:
        pass
    
    # Method that actually performs all the operation are needed
    @abstractmethod
    def format(self):
        pass

class Cpp(Language):

    output_file_name = Temp_Files.NO_PREPROCESSOR

    operators = [
    '<=>', '<<=', '>>=', '->*',
    '==', '!=', '++', '--', '+=', '-=', '*=', '/=', '%=', '>>', '>=', '<<', '<=', '||', '|=', '&&', '&=', '^=', '~=', '::', '.*'
    '=', '!', '+', '-', '*', '/', '%', '>', '<', '|', '&', '^', ':', ' ', '(', ')', '[', ']', '{', '}', ';', ',', '?']

    keywords = ["auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else", "enum", "extern", "float", "for", "goto", "if", "int", 
                "long", "register", "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while", # C keywords"asm", "dynamic_cast", "namespace", "reinterpret_cast", "bool", "explicit", "new", "static_cast", "false", "catch"
                "operator", "template", "friend", "private", "class", "this", "inline", "public", "throw", "const_cast"
                "delete", "mutable", "protected", "true", "try", "typeid", "typename", "using", "virtual", "wchar_t"
                ]

    format_specifiers = ['c', 's', 'd', 'i', 'o', 'x', 'X', 'u', 'f', 'F', 'e', 'E', 'a', 'A', 'g', 'G', 'n', 'p']

    inline_comment_symbol = '//'

    multiline_comment_opening_symbol = '/*'

    multiline_comment_closing_symbol = '*/'

    # In C++, to create multiline strings we only need to add the closing and opening quotes between a string:
    # Example: "Hello" is equal to "Hel"   "lo".
    # The numbers of chars to add is 2 because of the 2 opening and closing quotes
    num_chars_to_add_to_multiline_strings = 2

    def __init__(self, file_name):
        self.file_name = file_name

    def handle_multiline_strings(self, str, string_tokens, len_first_string):
        token_counter = 0
        char_counter = 0

        # Until string_tokens isn't finished and the number of the chars of the tokens that has been read + the length of the next (atomic) token
        # is less than the length of the whole string - n_exceeding_chars - the number of chars that you need to add to create a multiline string
        while (token_counter < len(string_tokens)) and char_counter + len(string_tokens[token_counter]) < len_first_string - self.num_chars_to_add_to_multiline_strings:
            char_counter += len(string_tokens[token_counter])
            token_counter += 1
    
        # Return the string divided in two tokens: the first one, which will be written in the current segment, 
        # and the second one which will be written later
        return [str[: char_counter] + '\"', '\"' + str[char_counter: ]]
    
    def format(self, path, bw_img) -> list:
        Comments.delete_comments(self, path)
        prepr_instructions = Preprocessor.retrieve_preprocessor_directives(self)
        Format.format_file(self, prepr_instructions, path, bw_img)