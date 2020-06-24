#! /usr/bin/python3
''' 
    Steg.py v1.1

    Author: CPunch
    Description:
        This small python script will encode/decode files in PNG Images. This will NOT work on any lossy-compressed image file format (such as 
        JPEG) as that would alter the RGB color values.

    Tech. Description:
        The file will be encoded into the first few pixels in the image in binary. The binary will be represented on whether the
        RGB color values (R, G, or B) are odd or even. Even = 1; Odd = 0; The first color value of 0 marks the end of the file. 
        
        This means that a 512x512 image has a limit of ((512*512)*3)/8 = 98304 bytes. Thats 98kb of data, 
        however the limit for the encoded data will grow as the size of the image grows.
'''

from PIL import Image
import argparse

# returns an array of all color values in order
def getColorValues(img):
    pixels = img.load() # loads image
    pixelArray = []
    width, height = img.size

    for y in range(height):
        for x in range(width):
            pixelArray.append([pixels[x, y][0], pixels[x, y][1], pixels[x, y][2]])

    return (pixelArray, img.size)

# calculates the maximum ammount of bits that can be encoded in an image size (floor divide by 8 to get bytes)
def maxSizeOfBits(size):
    w, h = size
    return ((w*h) * 3) - 1 # 3 bits per pixel -1 for the end marker

# converts color value array to PIL Image
def toImage(pixelArray, sz):
    img = Image.new(mode = "RGB", size = sz)
    width, height = sz
    indx = 0

    # places the pixels back where they belong
    for y in range(height):
        for x in range(width):
            img.putpixel((x, y), (pixelArray[indx][0], pixelArray[indx][1], pixelArray[indx][2]))
            indx += 1

    return img

# data is a string of 1s and 0s representing the binary data to encode
def encodeToImage(baseImg, data):
    pixels, size = getColorValues(baseImg)
    sizeOfData = len(data) // 8
    maxSizeOfData = maxSizeOfBits(size) // 8

    print("[INFO] This image can hold " + maxSizeOfData + " bytes")

    if sizeOfData > maxSizeOfData:
        print("[ERROR] data is too big, please use a bigger image! ", sizeOfData, " > ", maxSizeOfData)
        exit(3)

    print("Encoding ", sizeOfData, " bytes...")
    indx = 0 # current index of the binary data, to get the current pixel we're on get divide this by 3 and round down

    for b in data:
        pindx = indx // 3 # gets the index of the pixel using floor division
        cindx = indx%3 # gets the index of the current color value (R, G, or B)
        pixel = pixels[pindx]

        if (pixel[cindx] == 0): # we don't want to accidentally make an end-marker, so set it to at least 1
            pixel[cindx] = 1

        if (b == '1'): # colorvalue needs to be even
            if (pixel[cindx]%2 != 0): # checks if the colorvalue is odd, if it's already even do nothing!
                if (pixel[cindx] > 128): # just a precaution so we don't go over 255 or become 0
                    pixel[cindx] -= 1
                else:
                    pixel[cindx] += 1
        else: # needs to be odd
            if (pixel[cindx]%2 == 0): # checks if the colorvalue is even, if it's already odd do nothing!
                if (pixel[cindx] > 128):
                    pixel[cindx] -= 1
                else:
                    pixel[cindx] += 1
        
        
        pixels[pindx] = pixel
        indx += 1

    # now we create our end marker
    pixels[indx // 3][indx%3] = 0
    
    return toImage(pixels, size)

# returns data as string of binary
def decodeFromImage(img):
    pixels, size = getColorValues(img)
    indx = 0
    data = ""

    # while the current colorvalue isn't an end-marker
    while pixels[indx // 3][indx%3] != 0:
        if (pixels[indx // 3][indx%3]%2 == 0): # it's even, thats a 1
            data += '1'
        else:
            data += '0'
        indx += 1
    
    print("Decoded ", len(data) // 8, " bytes")
    return data

def byteToBin(byte):
    # strips the first two characters "0b"
    binary = bin(byte)[2:]

    # fill in missing bits
    for i in range(8 - len(binary)):
        binary = '0' + binary
    return binary

def fileToBin(filename):
    data = open(filename, "rb").read()
    binary = ""

    for d in data:
        binary += byteToBin(d)
    
    return binary

def binToBytes(s):
    byteArray = bytearray()
    for i in range(len(s) // 8):
        binary = s[i*8:(i*8)+8]
        byteArray.append(int(binary, 2))
    return byteArray

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="encode hidden files into images or decode hidden files from images. by default without ENCODE set, it will decode and write to OUTPUT (or out)")
    parser.add_argument("image", help="image to encode/decode from")
    parser.add_argument("-o", "--output", help="output filename")
    parser.add_argument("-e", "--encode", help="file to encode data from")
    args = parser.parse_args()

    if args.encode:
        # encode
        img = Image.open(args.image).convert('RGB')
        encodeToImage(img, fileToBin(args.encode)).save(args.output or "encoded_" + args.image)
    else:
        # decode
        img = Image.open(args.image)
        binary = decodeFromImage(img)
        out = open(args.output or "out", "wb")
        out.write(binToBytes(binary))
