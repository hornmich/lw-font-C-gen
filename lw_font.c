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

