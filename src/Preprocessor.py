# Given the file name, it creates a new file inside the temp_files directory
# called noprepr where there are no preprocessor instructions: all of them are put inside
# a list called preprocessor_directives and returned: hey will be written as header inside the out_file
# in Format.py
from typing import List
import os

def retrieve_preprocessor_directives(file_name)->List:
    with open("temp_files/nc_" + file_name, mode = 'r') as input:
        with open("temp_files/noprepr_" + file_name, mode = 'w') as output:
            preprocessor_directives = []
            multiline_preprocessor = False

            for line in input:
                line = line.strip()

                #If the line starts with an hash then it's a preprocessor directive
                if line[0] == '#':
                    preprocessor_directives.append(line)
                    #we've found a multiline preprocessore directive
                    if(line[-1] == '\\'):
                        multiline_preprocessor = True
                elif multiline_preprocessor:
                    preprocessor_directives.append(line)
                    #multiline preprocessor directive finished
                    if(line[-1] != '\\'):
                        multiline_preprocessor = False
                else:
                    output.write(line + '\n')

    os.remove("temp_files/nc_" + file_name)
    return preprocessor_directives
