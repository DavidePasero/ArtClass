# ArtClass
ArtClass is the most lethal weapon ever created in the history of programming.
It is a tool written in Python 3 that allows you to format your source code in a very artistic way.
Basically, you execute ArtClass.py specifying an error-free source code file of a supported language and a square-black-and-white image and the program will output the same code formatted in a way that resembles the input image.
Of course, the outputted source code will still be error-free.

## How to execute ArtClass
Since it's a python3 program, you can execute ArtClass with the following command:
python3 ArtClass.py

If you want, you can specify the source code file and the image file as parameters in the execution command, like in the following example:
python3 ArtClass.py path_to_source_code_file/test.cpp path_to_img/test.png

Otherwise, when you start the program you'll be asked to provide these two files. Remember to always specify the absolute path.
The outputted file will be created in the folder where the source code file is stored.

## Known problems
Multiline strings are not yet supported. This is due to the differences of implementation in the various languages: Java, for example, has text blocks which
have the feature that they can be indented with the code, but at compile time this indentation is removed. Python (which will never be supported for obvious
reasons), instead, has a different multiline string implementation where the indentation is kept inside the string literal.
Maybe in the future I'll think of an elegant way to handle this.
The solution, for now, is to keep multiline string literals in a different file and import from it.

Raw strings are not supported for obvious reasons: everything that needs white spaces or tabulations or carriage returns to keep their semantic can't work
with ArtClass, although there should be a way to convert a raw string to a multiline string and then a multiline string to an inline string.

## Supported languages
C
C++
JavaScript
Other C-like languages are supported, beware that sintactic elements that require spacing or tabulations cannot work with this program. For example, Raw multiline strings in Java do not work with ArtClass, but other than that everything else in Java works.

## Youtube video
https://youtu.be/R-6Mh_cz--U
