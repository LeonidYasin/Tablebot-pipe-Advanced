# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
#!/usr/bin/env python3
import sys
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def build_reply_markup(buttons_str):
    """Создает обычную клавиатуру"""
    if not buttons_str or buttons_str == "—":
        return None
    
    buttons = [btn.strip() for btn in buttons_str.split('|') if btn.strip()]
    
    keyboard_buttons = []
    for btn_text in buttons:
        keyboard_buttons.append([KeyboardButton(text=btn_text)])
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True
    )
    
    print(f"[markup_builder] 📋 Создана Reply клавиатура: {buttons}", file=sys.stderr)
    return keyboard

def build_inline_markup(buttons_str):
    """Создает inline-клавиатуру"""
    if not buttons_str or buttons_str == "—":
        return None
    
    inline_buttons = []
    
    for btn_spec in buttons_str.split('|'):
        btn_spec = btn_spec.strip()
        if not btn_spec:
            continue
            
        if ':' in btn_spec:
            text, callback_data = btn_spec.split(':', 1)
            button = InlineKeyboardButton(text=text.strip(), callback_data=callback_data.strip())
        else:
            button = InlineKeyboardButton(text=btn_spec, callback_data=btn_spec)
        
        inline_buttons.append([button])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_buttons)
    
    print(f"[markup_builder] 🔘 Создана Inline клавиатура: {buttons_str}", file=sys.stderr)
    return keyboard