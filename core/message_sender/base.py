#!/usr/bin/env python3
import sys
from .text_sender import send_text_message
from .media_sender import send_photo_message, send_document_message, send_video_message
from .poll_sender import send_poll_message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

async def send_message_by_content(bot, chat_id, content):
    """Отправляет сообщение на основе описания контента"""
    message_type = content.get("type", "text")
    
    if message_type == "text":
        return await send_text_message(bot, chat_id, content)
    elif message_type == "photo":
        return await send_photo_message(bot, chat_id, content)
    elif message_type == "document":
        return await send_document_message(bot, chat_id, content)
    elif message_type == "video":
        return await send_video_message(bot, chat_id, content)
    elif message_type == "poll":
        return await send_poll_message(bot, chat_id, content)
    elif message_type == "location":
        return await send_location_request(bot, chat_id, content)
    else:
        print(f"[message_sender] ⚠️ Неизвестный тип сообщения: {message_type}", file=sys.stderr)
        return await send_text_message(bot, chat_id, content)

async def send_location_request(bot, chat_id, content):
    """Запрашивает локацию"""
    return await bot.send_message(
        chat_id=chat_id,
        text="Поделитесь вашей локацией:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📍 Отправить локацию", request_location=True)]],
            resize_keyboard=True
        )
    )