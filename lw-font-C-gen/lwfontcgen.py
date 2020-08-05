'''
Created on 21.7.2020

@author: E9990291
'''

import argparse
import sys
from PIL import Image
import xmltodict
from test.test_print import ClassWith__str__
from typing import Set

class Offset:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
class Rect:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)
        self.x2 = self.x+self.w
        self.y2 = self.y+self.h

class Char:
    def __init__(self, image_file: str, width: int, offset: str, rect: str, code: str):
        self.width = width
        offset = str.split(offset)
        if len(offset) != 2:
            raise Exception('Offset is an invalid string')
        self.offset = Offset(x = offset[0], y = offset[1])
        rect = str.split(rect)
        if len(rect) != 4:
            raise Exception('Rect is an invalid string')
        self.rect = Rect(x = rect[0], y = rect[1], w = rect[2], h = rect[3])
        self.code = code
        self.pixmap = Pixmap(image_file, self.rect)
        
    def get_code(self):
        return '\n\
        {{ \n\
            .width = {0}, \n\
            .offset_x = {1}, \n\
            .offset_y = {2}, \n\
            .code = w\'{3}\', \n\
            .pixmap = {4} \n\
        }},\
            '.format(
            self.width,
            self.offset.x,
            self.offset.y,
            self.code,
            self.pixmap.get_code()
            )

class Font:
    def __init__(self, family: str, size: int, height: int, style: str, char_set: Set[Char]):
        self.family = family
        self.size = int(size)
        self.height = int(height)
        self.style = style
        self.char_set = char_set
    
    def get_code(self):
        char_set_code = ''.join('{0}'.format(c.get_code()) for c in self.char_set)
        
        return ' \
/* Generated font code */ \n \
#import <lw_font.h>\n \
\n \
static const lw_font font_{0}_{2}_{3} = {{ \n\
    .family = \"{4}\", \n\
    .size = {5}, \n\
    .height = {6}, \n\
    .style = \"{7}\", \n\
    .chars_cnt = {8}, \n\
    .chars = {{ \n\
        {9} \n\
    }} \n\
}}; \n\
        '.format(
            self.family,
            self.size,
            self.height,
            self.style,
            self.family,
            self.size,
            self.height,
            self.style,
            len(self.char_set),
            char_set_code
            )
    
class Pixmap:
    def __init__(self, image_file: str, rect: Rect = None):
        im = Image.open(options.image, 'r')
        pixels = list(im.getdata())
        
        if rect == None:
            rect = Rect(x = 0, y = 0, w = width, h = height)
        
        letter_img = im.crop((rect.x, rect.y, rect.x2, rect.y2))
        pixels = list(letter_img.getdata())
        self.width, self.height = letter_img.size

        
        bytes = []
        byte = 0
        bit_cnt = 0
        for bit in pixels:
            byte = byte + ((bit>0) << bit_cnt)
            bit_cnt += 1
            if bit_cnt == 8:
                bit_cnt = 0
                bytes.append(byte)
                byte = 0
        if bit_cnt != 0:
            bytes.append(byte)
            
        self.bytes = bytes
        print(self.bytes)
        
    def __str__(self):
        str = ''
        byte=0
        bit=0
        for line in range(0, self.height):
            for column in range(0, self.width):
                if self.bytes[byte] & (1<<bit):
                    str += ' '
                else:
                    str += '#'
                bit += 1
                if bit >= 8:
                    byte += 1
                    bit = 0
            str += '\n'
        return str
    
    def get_code(self):
        str = '{'
        bytes_str = ''.join('0x{:02X}, '.format(byte) for byte in self.bytes)
        str += bytes_str[:-2] + '}'
        return str
         
def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-i", "--image", help="Your image input file.")
    parser.add_argument("-x", "--xml", help="Your xml descriptor file.")
    parser.add_argument("-o", "--output", help="Your destination output file name.")
    options = parser.parse_args(args)
    return options

if __name__ == '__main__':
    options = getOptions()
    char_set = []

    with open(options.xml, 'r') as xmlfile:
        xml = xmlfile.read()
        print("XML to parse: " + options.xml)
        xml = xmltodict.parse(xml)
        family = xml['Font']['@family']
        size = xml['Font']['@size']
        height = xml['Font']['@height']
        style = xml['Font']['@style']
        chars = xml['Font']['Char']
        # Build character set
        for char in chars:
            tmp_char = Char(image_file = options.image, width = char['@width'], offset = char['@offset'], rect = char['@rect'], code = char['@code'])
            print("Character " + tmp_char.code + ", [w:"+str(tmp_char.pixmap.width)+", h:" + str(tmp_char.pixmap.height) + "]")
            print(tmp_char.pixmap.__str__())
            char_set.append(tmp_char)
    print("Will output to " + options.output)
    print("Total characters: " + str(len(char_set)))
    font = Font(family=family, size=size, height=height, style=style, char_set=char_set)
    code = font.get_code()
    print(code)
    with open(options.output, 'w') as out_file:
        out_file.write(code)
    print('Done')
    
    
    