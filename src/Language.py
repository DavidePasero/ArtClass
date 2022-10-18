from abc import abstractmethod
import TempFiles
import RefactorCode
import Format
import Util

class Language:

    UNDEFINED_SYMBOL = ""

    def __init__(self):
        pass

    # This variable will indicate the file which Format.py will open in read mode
    @property
    @abstractmethod
    def output_file_name(self):
        pass

    # It will be overloaded with a list containing the operators for that language
    # They have to be listed in order of length, from the longest to the shortest
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

    # It will be overloaded with the symbol that the language uses to represent the beginning and ending of a string
    @property
    @abstractmethod
    def string_literal_symbol(self):
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
    
    # It will be overloaded with the symbol that the language uses to represent the beginning of a multiline string
    @property
    @abstractmethod
    def multiline_string_opening_symbol(self):
        pass

    # It will be overloaded with the symbol that the language uses to represent the ending of a multiline string
    @property
    @abstractmethod
    def multiline_string_closing_symbol(self):
        pass

    # It will be overloaded with the symbol that the language uses to represent an escape sequence;
    # e.g.: In C, inside a string literal, we can include the " character if we write \". \ is the escape symbol 
    @property
    @abstractmethod
    def escape_symbol(self):
        pass

    # It will be overloaded with the symbol that the language uses for the line continuation (if any);
    # e.g.: In C, in order to have a line continuation (it means that the following newline char shall not be interpreted as a newline from the compiler)
    # we use the backslash character, in fact, we can have multiline strings by having:
    # str = "hel\
    # lo" 
    @property
    @abstractmethod
    def line_continuation_symbol(self):
        pass
    
    # Multiline strings are different among different languages: some of them use concatenation,
    # others, like cpp, use the following syntax: "...str..." "...str2..."
    # and other use the triple quotes: """ ... ... ... """
    @abstractmethod
    def separate_in_multiline_strings(self, str: str)->list:
        pass
    
    # This is the method that actually formats the file: 
    # it executes all the necessary operations that are needed for the files written in the current language
    @abstractmethod
    def format(self):
        pass

class C(Language):
    output_file_name = TempFiles.NO_PREPROCESSOR

    operators = [
    '<<=', '>>=',
    '==', '!=', '++', '--', '+=', '-=', '*=', '/=', '%=', '>>', '>=', '<<', '<=', '||', '|=', '&&', '&=', '^=', '~=',
    '=', '!', '+', '-', '*', '/', '%', '>', '<', '|', '&', '^', ':', ' ', '(', ')', '[', ']', '{', '}', ';', ',', '?'
    ]

    keywords = [
        "auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else", "enum", "extern", "float", "for", "goto", "if", "int", 
        "long", "register", "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while"
        ]

    format_specifiers = ['c', 's', 'd', 'i', 'o', 'x', 'X', 'u', 'f', 'F', 'e', 'E', 'a', 'A', 'g', 'G', 'n', 'p']

    string_literal_symbol = ['\"']
    inline_comment_symbol = ['//']
    multiline_comment_opening_symbol = ['/*']
    multiline_comment_closing_symbol = ['*/']
    multiline_string_opening_symbol = Language.UNDEFINED_SYMBOL
    multiline_string_closing_symbol = Language.UNDEFINED_SYMBOL
    escape_symbol = "\\"
    line_continuation_symbol = "\\"

    def __init__(self, file_name):
        self.file_name = file_name        
    
    def format(self, path, bw_img):

        # Removes comments and put preprocessor instructions at the beginning of the file
        with open(path + self.file_name, "r") as input:
            with open(TempFiles.PREPARATION_FILE + self.file_name, "w+") as prep:
                RefactorCode.strip_file(input, prep)
                prep.seek(0)
                RefactorCode.refactor(self, prep, prep)

        # Handles preprocessor instructions
        with open(TempFiles.PREPARATION_FILE + self.file_name, mode = 'r') as input:
            with open(TempFiles.NO_PREPROCESSOR + self.file_name, mode = 'w') as output:
                prepr_instructions = RefactorCode.retrieve_preprocessor_directives(self, input, output)
        
        # Finally ready to format the file
        Format.format_file(self, prepr_instructions, path, bw_img)

    def separate_in_multiline_strings(self, str, string_tokens, len_first_string):
        # We will possibly divide the string into two strings
        # len_first_string represents the length that the first string (the one we will immediately write onto the file)
        # has to have.
        token_counter = 0
        char_counter = 0

        # Until string_tokens isn't finished and the number of the chars of the tokens that has been read + the length of the next (atomic) token
        # is less than length_first_string-1 (-1 because we need to add a " to complete the string)
        while (token_counter < len(string_tokens)) and char_counter + len(string_tokens[token_counter]) <= len_first_string - 1:
            char_counter += len(string_tokens[token_counter])
            token_counter += 1
    
        # Return the string divided in two tokens: the first one, which will be written in the current segment, 
        # and the second one which will be written later
        return [str[: char_counter] + '\"', '\"' + str[char_counter: ]]

class Cpp(C):

    output_file_name = TempFiles.NO_PREPROCESSOR

    operators = [
    '<=>', '<<=', '>>=', '->*',
    '==', '!=', '++', '--', '+=', '-=', '*=', '/=', '%=', '>>', '>=', '<<', '<=', '||', '|=', '&&', '&=', '^=', '~=', '::', '.*'
    '=', '!', '+', '-', '*', '/', '%', '>', '<', '|', '&', '^', ':', ' ', '(', ')', '[', ']', '{', '}', ';', ',', '?'
    ]

    keywords = ["auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else", "enum", "extern", "float", "for", "goto", "if", "int", 
                "long", "register", "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while",
                "operator", "template", "friend", "private", "class", "this", "inline", "public", "throw", "const_cast"
                "delete", "mutable", "protected", "true", "try", "typeid", "typename", "using", "virtual", "wchar_t"
                ]

class Javascript(Language):
    output_file_name = TempFiles.NO_COMMENTS

    operators = [
                '>>>=',
                '===', '!==', '**=', '??=', '||=', '&&=', '>>>', '<<=', '>>=',
                '==', '!=', '++', '**', '--', '+=', '-=', '*=', '/=', '%=', '>>', '>=', '<<', '<=', '||', '|=', '&&', '&=', '^=', '~=', '::', '??'
                '=', '!', '+', '-', '*', '/', '%', '>', '<', '|', '&', '^', ':', ' ', '(', ')', '[', ']', '{', '}', ';', ',', '?'
                ]

    keywords =  [
                "await", "break", "case", "catch", "class", "const", "continue", "debugger", "default", "delete", "do", "else", "enum", "export", "extends", "false", "finally", 
                "for", "function", "if", "implements", "import", "in", "instanceof", "interface", "let", "new", "null", "package", "private", "protected", "public",
                "return", "super", "switch", "static", "this", "throw", "try", "true", "typeof", "var", "void", "while", "with", "yield"
                ]

    string_literal_symbol = ["\"", "\'"]
    inline_comment_symbol = ['//']
    multiline_comment_opening_symbol = ['/*']
    multiline_comment_closing_symbol = ['*/']
    multiline_string_opening_symbol = "`"
    multiline_string_closing_symbol = "`"
    escape_symbol = "\\"
    line_continuation_symbol = Language.UNDEFINED_SYMBOL

    def format(self, path, bw_img):
        # Removes comments
        with open(TempFiles.NO_MULTILINE_INTRUCTIONS + self.file_name, "r") as input:
            with open(TempFiles.NO_COMMENTS + self.file_name, "w") as output:
                RefactorCode.refactor(self, input, output)

        Format.format_file(self, "", path, bw_img)

    # uses concatenation instead of the backticks
    def separate_in_multiline_strings(self, str, string_tokens, len_first_string):
        token_counter = 0
        char_counter = 0

        while (token_counter < len(string_tokens)) and char_counter + len(string_tokens[token_counter]) <= len_first_string - 1:
            char_counter += len(string_tokens[token_counter])
            token_counter += 1
    
        # Return the string divided into three tokens: the first string, which will be written in the current segment, 
        # the + symbol, which allows us to separate the strings and possibly have a multiline string
        # and the second string which will be written later
        return [str[: char_counter] + '\"', '+', '\"' + str[char_counter: ]]