# \tablebot-pipe-advanced\core\message_sender\text_sender.py
# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
#!/usr/bin/env python3
import sys
from .markup_builder import build_reply_markup, build_inline_markup
from .format_detector import detect_parse_mode

async def send_text_message(bot, chat_id, content):
    """Отправляет текстовое сообщение"""
    # Проверяем, есть ли текст для отправки
    if not content.get("text") and not content.get("caption"):
        print(f"[text_sender] ⚠️ Пропускаем отправку: нет текста и подписи", file=sys.stderr)
        return None
    
    reply_markup = build_reply_markup(content.get("reply_buttons", ""))
    inline_markup = build_inline_markup(content.get("inline_buttons", ""))
    
     # Специальная обработка для запроса локации
    if content.get("integrations") == "request_location":
        print(f"[text_sender] 📍 Обнаружен запрос геолокации!", file=sys.stderr)
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        
        # Создаем клавиатуру с кнопкой геолокации
        buttons = []
        
        # Добавляем альтернативные кнопки если есть
        if content.get("reply_buttons"):
            alt_buttons = [btn.strip() for btn in content.get("reply_buttons", "").split('|') if btn.strip()]
            for btn_text in alt_buttons:
                buttons.append([KeyboardButton(text=btn_text)])
        
        # Добавляем кнопку геолокации (работает в мобильных приложениях)
        buttons.append([KeyboardButton(text="📍 Отправить геолокацию", request_location=True)])
        
        markup = ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True,
            one_time_keyboard=True
        )
        print(f"[text_sender] 📍 Создана клавиатура с запросом геолокации", file=sys.stderr)
    else:
    
        # Используем inline-кнопки если есть, иначе обычные
        markup = inline_markup if inline_markup else reply_markup
        
        # ДОБАВЛЕНО: Очистка клавиатуры если reply_buttons пустое или "—"
        if content.get("reply_buttons", "").strip() in ["", "—"] and not inline_markup:
            from aiogram.types import ReplyKeyboardRemove
            markup = ReplyKeyboardRemove()
            print(f"[text_sender] 🗑️ Клавиатура очищена", file=sys.stderr)
        else:
            print(f"[text_sender] 📋 Используется обычная клавиатура: {content.get('reply_buttons')}", file=sys.stderr)
    
    parse_mode = detect_parse_mode(content.get("text", ""))
    
    text_to_send = content.get("text", "") or content.get("caption", "")
    
    print(f"[text_sender] 📝 Отправка текста: {len(text_to_send)} chars, parse_mode: {parse_mode}", file=sys.stderr)
    print(f"[text_sender] итоговый text: {text_to_send!r}", file=sys.stderr)
    print(f"[text_sender] parse_mode: {parse_mode}", file=sys.stderr)
    
    return await bot.send_message(
        chat_id=chat_id,
        text=text_to_send,
        parse_mode=parse_mode,
        reply_markup=markup
    )