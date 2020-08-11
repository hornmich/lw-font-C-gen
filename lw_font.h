/*
 * ili9341_font.h
 *
 *  Created on: 20. 7. 2020
 *      Author: E9990291
 */

#ifndef LW_FONT_H_
#define LW_FONT_H_

#include "stdint.h"
#include "stdbool.h"
#include "wchar.h"

typedef struct {
	const uint8_t width;
	const uint8_t height;
	const int8_t offset_x;
	const int8_t offset_y;
	const uint8_t* pixmap;
} lw_char_def_t;

typedef struct {
	const wchar_t char_code;
	const lw_char_def_t char_def;
} lw_char_map_t;

typedef struct {
	const char* family;
	const uint8_t size;
	const uint8_t height;
	const char* style;
	const uint16_t chars_cnt;
	const lw_char_map_t *chars;
	const bool inv;
} lw_font_t;

#endif /* LW_FONT_H_ */
