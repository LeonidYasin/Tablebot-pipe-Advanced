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
    
    # Используем inline-кнопки если есть, иначе обычные
    markup = inline_markup if inline_markup else reply_markup
    
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