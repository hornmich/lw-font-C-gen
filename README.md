#Lightweight Embedded C Font Generator

This is a Python script for generating Unicode fonts for C embedded firmware from any
TTF (TrueType Font).

The script takes the TTF file, size in pixels and set of required letters as
input and generates C code that can be directly included into your project.

## Requirements

* Python3 (tested and developed on Python 3.8
* The generated code requires C99 compatible compiler
* (PIL library)[https://pillow.readthedocs.io/en/3.0.x/installation.html] to be installed 

## Usage

    usage: lwfontcgen.py [-h] [-o OUTPUT] [-b INVERTED] ttf-file size chars-file

    Parses command.

    positional arguments:
      ttf-file              TrueType (ttf) input font file.
      size                  Size in pixels.
      chars-file            File with characters.

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            Your destination output file name.
      -b INVERTED, --inverted INVERTED
                            Generate inverted bitmaps.

* ttf-file - is the path to the TrueType font file, from which the embedded font will be generated.
* size - is the desired font size (height to be more specific) in pixels
* chars-file - is a file containing the letters to be included in the generated embedded font.
* -o - is an optional parameter to specify the name of the output files. By default, the files are nameaccording to the font, for example font_Arial_20_Bold.c and font_Arial_20_Bold.h.
* -b - is an optional parameter to invert the font pixels.

## Example

The following typical command will generate Arial Bold 12px size font into the default c and h files.

    ->> python.exe lwfontcgen.py arialbd.ttf 12 chars.txt
    Font Arial_12_Bold not inverted (8 characters) generated to font_Arial_12_Bold.c and font_Arial_12_Bold.h

If the content of the chars.txt file is

    abcdABCD

The contenf of the generated font_Arial_12_Bold.h will be

	/* Generated header file for font. */

	#ifndef _ARIAL_12_BOLD_H_
	#define _ARIAL_12_BOLD_H_

	#include "lw_font.h"

	extern const lw_font_t font_Arial_12_Bold;

	#endif /* _ARIAL_12_BOLD_H_ */
	
The contenf of the generated font_Arial_12_Bold.c will be (shortened)

	/* Generated font code */
	#include "lw_font.h"

	#define ARIAL_12_BOLD_CHARS_CNT (8)

	/* Pixmaps */
	/*
	 ####  
	#   ## 
	  #### 
	 ## ## 
	##  ## 
	##  ## 
	 ##### 

	*/

	

	/*
	#####   
	##  ##  
	##   ## 
	##   ## 
	##   ## 
	##   ## 
	##   ## 
	##  ##  
	#####   

	*/
	const uint8_t pixmap_65501168[] = {0x1F, 0x33, 0x63, 0x63, 0x63, 0x63, 0x63, 0x33, 0x1F};


	/* Characters */
	const lw_char_map_t chars_Arial_12_Bold[ARIAL_12_BOLD_CHARS_CNT] = {
		{
			.char_code = L'a',
			.char_def = {
				.width = 7,
				.height = 10
				.offset_x = 0,
				.offset_y = 4,
				.pixmap = pixmap_65500640
			}
		},	
		
	...
		
		{
			.char_code = L'D',
			.char_def = {
				.width = 9,
				.height = 10,
				.offset_x = 0,
				.offset_y = 2,
				.pixmap = pixmap_65501168
			}
		},
	};

	/* Font */
	const lw_font_t font_Arial_12_Bold = {
		.family = "Arial",
		.size = 12,
		.height = 12,
		.style = "Bold",
		.inv = 0,
		.chars_cnt = ARIAL_12_BOLD_CHARS_CNT,
		.chars = chars_Arial_12_Bold
	};
	
With these, in your code, you may just include the font_Arial_12_Bold.h, add lw_font.h to your include path and draw the pixmaps of each fonts by your favourite drawing engine.