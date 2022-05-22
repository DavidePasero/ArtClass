import Image_Handler
import Language

import sys

def main(cpp_path = "test.cpp", img_file_name = "test.png"):
    black_white_img = Image_Handler.black_and_white(img_file_name)
    path, cpp_file_name = separate_path_from_filename(cpp_path)
    lang = Language.Cpp(cpp_file_name)
    lang.format(path, black_white_img)

def separate_path_from_filename(cpp_path):
    '''
    Returns (path, file_name)
    '''
    try:
        last_slash_index = cpp_path.rindex('/')
        return (cpp_path[: last_slash_index + 1], cpp_path[last_slash_index + 1: ])
    except ValueError:
        print("You're not allowed to specify a relative path")
        sys.exit()

if __name__ == '__main__':
    if len(sys.argv) > 2:
        main(cpp_path = sys.argv[1], img_file_name = sys.argv[2])
    else:
        cpp_path = input("Specify the .cpp file to modify: ")
        img_file_name = input("Specify the image file: ")
        main(cpp_path, img_file_name)