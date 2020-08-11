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
from PIL import Image, ImageFont
import logging
from sys import exit
from string import Template
from typing import Set, List, Tuple

class Char:
    def __init__(self, font: ImageFont, code: str):
        self.code = code
        bmp = ttf_font.getmask2(code, mode='1')
        self.width = bmp[0].size[0]
        self.offset = bmp[1]
        self.pixmap = Pixmap(list(bmp[0]), bmp[0].size)
        
    def get_code(self):
        if len(self.pixmap.bytes) == 0:
            pixmap_def_name = 'NULL'
        else:
            pixmap_def_name = 'pixmap_{0}'.format(id(self.pixmap))
        code_filling = {
            'char_code': self.get_c_wchar(),
            'width': self.width,
            'offset_x': self.offset[0],
            'offset_y': self.offset[1],
            'pixmap': pixmap_def_name
        }
        
        with open('templates/char_def.ctemp', 'r') as temp_file:
            template = Template( temp_file.read() )
        code = template.safe_substitute(code_filling)

        return code
    
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
        pixmaps_code = ''.join('{0}\n'.format(c.pixmap.get_code()) for c in self.char_set)
        chars_def_code = ''.join('{0}'.format(c.get_code()) for c in self.char_set)
        code_filling = {
            'font_name_upper': self.short_name().upper(),
            'chars_cnt': len(self.char_set),
            'pixmap_def': pixmaps_code,
            'font_name': self.short_name(),
            'chars_def': chars_def_code,
            'family': self.family,
            'size': self.size,
            'height': self.height,
            'style': self.style,
            'inverted': int(self.inverted)
        }
        
        with open('templates/font_def.ctemp', 'r') as temp_file:
            template = Template( temp_file.read() )
        code = template.safe_substitute(code_filling)

        return code
        
    def get_header(self):
        code_filling = {
            'header_blocker': '_{0}_H_'.format(self.short_name().upper()),
            'font_name': self.short_name()
        }
        
        with open('templates/header.ctemp', 'r') as temp_file:
            template = Template( temp_file.read() )
        code = template.safe_substitute(code_filling)

        return code
    
class Pixmap:
    def __init__(self, image_bytes: list, size: tuple):
        logging.info('PIXMAP: Creating new pixmap')
        logging.debug('Image data: {0}'.format(image_bytes))
        
        self.width, self.height = size
        logging.debug('Pixmap dimensions: [{0}, {1}]'.format(self.width, self.height))
        
        logging.info('Creating bytearrays from pixels.')
        bytes = []
        byte = 0
        bit_cnt = 0
        for bit in image_bytes:
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
                    str += '#'
                else:
                    str += ' '
                bit += 1
                if bit >= 8:
                    byte += 1
                    bit = 0
            str += '\n'
        return str
    
    def get_code(self):
        bytes_str = ''.join('0x{:02X}, '.format(byte) for byte in self.bytes)
        bytes_str = bytes_str[:-2]
        code_filling = {
            'char_preview' : self.__str__(), 
            'pixmap_definition_name' : 'pixmap_{0}'.format(id(self)), 
            'pixmap_bytes':bytes_str
        }

        with open('templates/pixmap_def.ctemp', 'r') as temp_file:
            template = Template( temp_file.read() )
        code = template.safe_substitute(code_filling)

        return code
         
def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument('TTF_file', metavar='ttf-file', type=str, help="TrueType (ttf) input font file.")
    parser.add_argument('size', metavar='size', type=int, help="Size in pixels.")
    parser.add_argument('chars', metavar='chars-file', type=str, help="File with characters.")
    parser.add_argument("-o", "--output", default=None, help="Your destination output file name.")
    parser.add_argument("-b", "--inverted", default=False, type=bool, help="Generate inverted bitmaps.")

    options = parser.parse_args(args)
    return options

if __name__ == '__main__':
    options = getOptions()
    char_set = []
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='lwfontcgen.log', filemode='w', level=logging.DEBUG)
    
    logging.info('Lightweight generator started.')
    logging.debug('Inputs:\n - TTF: {0}\n - Size: {1} px\n - Characters file: {2}'.format(options.TTF_file, options.size, options.chars))

    try:
        logging.info('Opening TTF font.')
        ttf_font=ImageFont.truetype(font=options.TTF_file, size=options.size)
        family=ttf_font.getname()[0]
        style=ttf_font.getname()[1]
        height=options.size
        size = options.size
        
        logging.info('Loading list of characters.')
        with open(options.chars, 'r', encoding='utf8') as chars_file:
            chars=list(chars_file.read())
        logging.info('Done, {0} characters loaded.'.format(len(chars)))
        logging.debug(chars)

        logging.info('Creating characters.')
        for c in chars:
            logging.info('Character ' + c)
            tmp_char = Char(font=ttf_font, code=c)
            logging.debug('Character \'{0}\' [w: {1}; h: {2}]'.format(tmp_char.code, tmp_char.pixmap.width, tmp_char.pixmap.height))
            logging.debug('\n{0}'.format(tmp_char.pixmap.__str__()))
            char_set.append(tmp_char)
    except OSError as e:
        str = 'ERROR: Input XML file {0} could not be read: {1}'.format(options.xml, e.msg)
        print(str)
        logging.error(str)  
        exit(1) 
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
        with open(ofile, 'w', encoding='utf8') as out_file:
            out_file.write(font.get_code())
        logging.info('Generating header.')
        ofile = options.output+'.h'
        with open(ofile, 'w', encoding='utf8') as out_file:
            out_file.write(font.get_header())
    except OSError as e:
        str = 'ERROR: Output file {0} could not be created: {1}'.format(ofile, e.msg)
        print(str)
        logging.error(str)  
        exit(1)
    logging.info('Done.')
    print('Font {0} ({1} characters) generated to {2} and {3}'.format(font, len(font.char_set), options.output+'.c', options.output+'.h'))
    
    
    