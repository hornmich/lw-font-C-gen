/*
 * Lightweight fonts for embedded systems.
 *
 * To use the library:
 * 1) Generate fonts C and H files by the lwfontcgen.py tool.
 * 2) Add the lw_fonts.h and generated H file to your include path
 * 3) Add the lw_fonts.c and generated C file to your build
 * 4) Include the generated font H file in your source code.
 *
 * To draw a character:
 * 1) Call lw_get_char to get the character definiton lw_char_def_t.
 * 2) Add offset_x and offset_y to the desired coordinates
 * 3) Draw pixel by pixel from the pixmap array, using the width and height as boundaries.
 *
 * To make a new line, use the lw_font_t.height value
 *
 *  Created on: 20. 7. 2020
 *      Author: Michal Horn
 */

#ifndef LW_FONT_H_
#define LW_FONT_H_

#include "stdint.h"
#include "stdbool.h"
#include "wchar.h"

/** Character definition */
typedef struct {
	const uint8_t width;    /**< Pixmap width */
	const uint8_t height;   /**< Pixmap height */
	const int8_t offset_x;  /**< Pixmap drawing offset X*/
	const int8_t offset_y;  /**< Pixmap drawing ofgset Y */
	const uint8_t* pixmap;  /**< Pixmap data */
} lw_char_def_t;

/** Character map */
typedef struct {
	const wchar_t char_code;        /**< Code of the character */
	const lw_char_def_t char_def;   /**< Character definition */
} lw_char_map_t;

/** Font definition */
typedef struct {
	const char* family;          /**< Font family literal. E.g. "Arial" */
	const uint8_t size;          /**< Font size in pixels */
	const uint8_t height;        /**< Line height in pixels */
	const char* style;           /**< Font style literal. E.g. "Regular" */
	const uint16_t chars_cnt;    /**< Number of characters */
	const lw_char_map_t *chars;  /**< Characters */
	const bool inv;              /**< Color inversion is used */
} lw_font_t;

/**
 * Lookup the character in the font charset.
 *
 * @param [in] font The font to look for the character
 * @param [in] c Character to look for.
 *
 * @returns Pointer to character definition or NULL if not found.
 */
const lw_char_def_t* lw_get_char(const lw_font_t* font, wchar_t c);

#endif /* LW_FONT_H_ */
