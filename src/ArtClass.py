import Image_Handler
import Language

import sys
import platform

def main(complete_path, img_file_name):
    black_white_img = Image_Handler.black_and_white(img_file_name)
    path, file_name = separate_path_from_filename(complete_path)
    lang = get_lang(file_name)
    lang.format(path, black_white_img)

def separate_path_from_filename(path):
    '''
    Returns (path, file_name)
    '''
    try:
        if platform.system() == 'Windows':
            last_slash_index = path.rindex('\\')
        else:
            last_slash_index = path.rindex('/')
        return (path[: last_slash_index + 1], path[last_slash_index + 1: ])
    except ValueError:
        print("You're not allowed to specify a relative path")
        sys.exit()


def get_lang(file_name) -> Language:
    try:
        last_point_index = file_name.rindex('.')
        extension = file_name[last_point_index + 1: ]
        if extension == 'cpp':
            return Language.Cpp(file_name)
        elif extension == 'c':
            return Language.C(file_name)
        # To complete
        else:
            print("This language is not yet supported, but this project is open source, you can see the details in the github page")
            sys.exit()
    except ValueError:
        print("You specified a file with no extension")
        sys.exit()

if __name__ == '__main__':
    if len(sys.argv) > 2:
        main(cpp_path = sys.argv[1], img_file_name = sys.argv[2])
    else:
        cpp_path = input("Specify the source file to modify: ")
        img_file_name = input("Specify the image file: ")
        main(cpp_path, img_file_name)
