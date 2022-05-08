import cv2

IMG_SIZE = 128

def black_and_white(img_filename):
    originalImage = cv2.imread(img_filename)
    #Resize the height to half of the width
    originalImage = cv2.resize(originalImage, (IMG_SIZE, IMG_SIZE // 2), interpolation = cv2.INTER_AREA)
    #convert it to gray scale
    grayImage = cv2.cvtColor(originalImage, cv2.COLOR_BGR2GRAY)
    
    #convert it to black and white
    (_, blackAndWhiteImage) = cv2.threshold(grayImage, 127, 255, cv2.THRESH_BINARY)
    
    ret_img = []

    #Instead of the img we return ret_img which is a 128x128 matrix of 0s (blacks) and 255s (whites)
    for i in range(IMG_SIZE):
        ret_img.append([])
        for j in range(IMG_SIZE):
            #since we resized the height to half of the width, we have generated a lot of blank spaces
            #we want to put the image in the middle, so every row 32 < row <= 92 will be white
            if i < 32 or i >= 96:
                ret_img[-1].append(255)
            else:
                ret_img[-1].append(blackAndWhiteImage.item(i - 32, j))
    
    return ret_img