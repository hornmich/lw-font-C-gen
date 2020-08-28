/*
 * lw_font.c
 *
 *  Created on: 11. 8. 2020
 *      Author: Michal Horn
 */
#include "lw_font.h"

const lw_char_def_t* lw_get_char(const lw_font_t* font, wchar_t c) {
	for (int i = 0; i < font->chars_cnt; i++) {
		if (c == font->chars[i].char_code) {
			return &font->chars[i].char_def;
		}
	}
	return NULL;
}

uint16_t lw_get_char_width(const lw_font_t* font, wchar_t c) {
	const lw_char_def_t* c_def = lw_get_char(font, c);
	if (c_def == NULL) {
		return 0;
	}

	return c_def->width + c_def->offset_x;
}

uint16_t lw_get_string_line_width(const lw_font_t* font, const wchar_t* str) {
	uint16_t str_width = 0;
	for (int i = 0; i < wcslen(str); i++) {
		if (str[i] == L'\r' || str[i] == L'\n') {
			break;
		}
		str_width += lw_get_char_width(font, str[i]);
	}
	return str_width;
}
