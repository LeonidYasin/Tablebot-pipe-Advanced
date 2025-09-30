#!/usr/bin/env python3
import sys
from .markup_builder import build_reply_markup

async def send_poll_message(bot, chat_id, content):
    """Отправляет опрос"""
    reply_markup = build_reply_markup(content.get("reply_buttons", ""))
    
    # Парсим опции для опроса
    options = content.get("options", [])
    if isinstance(options, str):
        options = [opt.strip() for opt in options.split(',')]
    
    print(f"[poll_sender] 📊 Отправка опроса: {len(options)} вариантов", file=sys.stderr)
    
    return await bot.send_poll(
        chat_id=chat_id,
        question=content.get("text", ""),
        options=options,
        reply_markup=reply_markup
    )