'''
Lightweight font C code generator.

Use this script together with lw_font library to generate lightweight pixmap fonts.

The expected input files are an image of font bitmap and XML descriptor file. Both
can be obtained easily with the application FontBuilder from https://github.com/andryblack/fontbuilder

The script takes the bitmap and the XML file and generates C code for lw_font library.

@author: Michal Horn
'''
import argparse
import sys
from PIL import Image
import xmltodict
from xmltodict import ParsingInterrupted
from test.test_print import ClassWith__str__
from typing import Set
import logging
from sys import exit

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
        if len(self.pixmap.bytes) == 0:
            pixmap_def_name = 'NULL'
        else:
            pixmap_def_name = 'pixmap_{0}'.format(id(self.pixmap))
        return '\
    {{ \n\
        .char_code = L\'{0}\', \n\
        .char_def = {{\n\
            .width = {1},\n\
            .offset_x = {2},\n\
            .offset_y = {3},\n\
            .pixmap = {4}\n\
        }}\n\
    }},\n'.format(
            self.get_c_wchar(),
            self.width,
            self.offset.x,
            self.offset.y,
            pixmap_def_name
            )
    
    def get_c_wchar(self):
        escape = ['\'', '\\', '\"']
        if self.code in escape:
            return '\\'+self.code
        else:
            return self.code

class Font:
    def __init__(self, family: str, size: int, height: int, style: str, char_set: Set[Char], inverted: bool = False):
        self.family = family
        self.size = int(size)
        self.height = int(height)
        self.inverted = inverted
        self.style = style
        self.char_set = char_set
        
    def __str__(self):
        str = '{0}_{1}_{2}'.format(self.family, self.size, self.style)
        if not self.inverted:
            str += ' not'
        str += ' inverted'
        return str
    
    def short_name(self):
        return '{0}_{1}_{2}'.format(self.family, self.size, self.style)
    
    def get_code(self):
        char_set_code = ''.join('{0}\n'.format(c.get_code()) for c in self.char_set)
        pixmaps_code = ''.join('{0}\n'.format(c.pixmap.get_code()) for c in self.char_set)
        chars_def_code = ''.join('{0}'.format(c.get_code()) for c in self.char_set)
        chars_def_code = chars_def_code[:-2]+'\n'
        chars_code = '\
const lw_char_map_t chars_{0}[{1}_CHARS_CNT] = {{\n\
{2}\
}};\n\
'.format(self.short_name(), self.short_name().upper(), chars_def_code)

        file_header = '\
/* Generated font code */\n \
#include \"lw_font.h\"\n\
\n\
#define {0}_CHARS_CNT ({1})\n\
\n\
'.format(
        self.short_name().upper(),
        len(self.char_set)
        )
       
        font_code = '\
const lw_font_t font_{0} = {{ \n\
    .family = \"{1}\", \n\
    .size = {2}, \n\
    .height = {3}, \n\
    .style = \"{4}\", \n\
    .inv = {5}, \n\
    .chars_cnt = {6}_CHARS_CNT, \n\
    .chars = chars_{0}\n\
}}; \n'.format(
        self.short_name(),
        self.family,
        self.size,
        self.height,
        self.style,
        int(self.inverted),
        self.short_name().upper(),
        )
        
        return file_header+pixmaps_code+chars_code+font_code
        
    def get_header(self):
        blocker = '_{0}_H_'.format(self.short_name().upper())
        return '\
/* Generated header file for font. */\n\
\n\
#ifndef {0}\n\
#define {0}\n\
\n\
#include \"lw_font.h\"\n\
\n\
extern const lw_font_t font_{1};\n\
\n\
#endif /* {0} */'.format(blocker, self.short_name())
    
class Pixmap:
    def __init__(self, image_file: str, rect: Rect = None):
        logging.info('PIXMAP: Creating new pixmap')
        logging.debug('Image file: {0}, rect: {1}'.format(image_file, rect))
        im = Image.open(options.image, 'r')
        pixels = list(im.getdata())
        
        if rect == None:
            rect = Rect(x = 0, y = 0, w = width, h = height)
        
        letter_img = im.crop((rect.x, rect.y, rect.x2, rect.y2))
        pixels = list(letter_img.getdata())
        self.width, self.height = letter_img.size
        logging.debug('Pixmap dimensions: [{0}, {1}]'.format(self.width, self.height))
        
        logging.info('Creating bytearrays from pixels.')
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
        logging.debug('Byte Array: {0}'.format(self.bytes))
        
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
        pixmap_def_name = 'pixmap_{0}'.format(id(self))
        bytes_str = ''.join('0x{:02X}, '.format(byte) for byte in self.bytes)
        bytes_str = bytes_str[:-2]

        illustration = self.__str__()

        return '\
/*\n\
{0}\n\
*/\n\
const uint8_t {1}[] = {{{2}}};\
'.format(
        illustration,
        pixmap_def_name,
        bytes_str)
         
def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-i", "--image", help="Your image input file.")
    parser.add_argument("-x", "--xml", help="Your xml descriptor file.")
    parser.add_argument("-o", "--output", default=None, help="Your destination output file name.")
    parser.add_argument("-b", "--inverted", default=False, type=bool, help="Type pixmap is inverted.")

    options = parser.parse_args(args)
    return options

if __name__ == '__main__':
    options = getOptions()
    char_set = []
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='lwfontcgen.log', filemode='w', level=logging.DEBUG)
    
    logging.info('Lightweight generator started.')
    logging.debug('Input files:\n - Image: {0}\n - XML: {1}'.format(options.image, options.xml))

    try:
        with open(options.xml, 'r') as xmlfile:
            xml = xmlfile.read()
            logging.info('Parsing XML.')
            xml = xmltodict.parse(xml)
            family = xml['Font']['@family']
            size = xml['Font']['@size']
            height = xml['Font']['@height']
            style = xml['Font']['@style']
            chars = xml['Font']['Char']
            # Build character set
            logging.info('Adding characters.')
            for char in chars:
                tmp_char = Char(image_file = options.image, width = char['@width'], offset = char['@offset'], rect = char['@rect'], code = char['@code'])
                logging.debug('Character \'{0}\' [w: {1}; h: {2}]'.format(tmp_char.code, tmp_char.pixmap.width, tmp_char.pixmap.height))
                logging.debug('\n{0}'.format(tmp_char.pixmap.__str__()))
                char_set.append(tmp_char)
    except OSError as e:
        str = 'ERROR: Input XML file {0} could not be read: {1}'.format(options.xml, e.msg)
        print(str)
        logging.error(str)  
        exit(1) 
    except ParsingInterrupted as e :
        str = 'ERROR: XML parsing failed: {0}'.format(e.msg)
        print(str)
        logging.error(str)
        exit(2)  
    except ExpatError as e:
        str = 'ERROR: XML parsing failed: {0}'.format(e.msg)
        print(str)
        logging.error(str)
        exit(2)          
    except Exception as e:
        str = 'ERROR: {0}'.format(e.msg)
        print(str)
        logging.error(str)
        exit(3)   
    logging.info('Done.')        
    logging.info('Creating font.')
    font = Font(family=family, size=size, height=height, style=style, char_set=char_set, inverted=options.inverted)
    logging.info('Done.')        
    logging.debug('Number of characters: {0}'.format(len(font.char_set)))        
    
    if options.output == None:
        options.output = 'font_{0}'.format(font.short_name())
    else:
        if options.output[-2:] != '.c':
            options.output += '.c'
    logging.debug('Output file: {0}'.format(options.output))

    try:
        ofile = options.output+'.c'
        logging.info('Generating code.')
        with open(ofile, 'w') as out_file:
            out_file.write(font.get_code())
        logging.info('Generating header.')
        ofile = options.output+'.h'
        with open(ofile, 'w') as out_file:
            out_file.write(font.get_header())
    except OSError as e:
        str = 'ERROR: Output file {0} could not be created: {1}'.format(ofile, e.msg)
        print(str)
        logging.error(str)  
        exit(1)
    logging.info('Done.')
    print('Font {0} ({1} characters) generated to {2} and {3}'.format(font, len(font.char_set), options.output+'.c', options.output+'.h'))
    
    
    