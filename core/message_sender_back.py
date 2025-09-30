#!/usr/bin/env python3
import sys
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile
)
from pathlib import Path

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

async def send_text_message(bot, chat_id, content):
    """Отправляет текстовое сообщение"""
    reply_markup = build_reply_markup(content.get("reply_buttons", ""))
    inline_markup = build_inline_markup(content.get("inline_buttons", ""))
    
    # Используем inline-кнопки если есть, иначе обычные
    markup = inline_markup if inline_markup else reply_markup
    
    return await bot.send_message(
        chat_id=chat_id,
        text=content.get("text", ""),
        parse_mode=detect_parse_mode(content.get("text", "")),
        reply_markup=markup
    )

async def send_photo_message(bot, chat_id, content):
    """Отправляет фото"""
    media_file = content.get("media_file", "")
    inline_markup = build_inline_markup(content.get("inline_buttons", ""))
    reply_markup = build_reply_markup(content.get("reply_buttons", ""))
    
    # Используем inline-кнопки если есть, иначе обычные
    markup = inline_markup if inline_markup else reply_markup
    
    if media_file.startswith(('http://', 'https://')):
        return await bot.send_photo(
            chat_id=chat_id,
            photo=media_file,
            caption=content.get("caption", ""),
            parse_mode=detect_parse_mode(content.get("caption", "")),
            reply_markup=markup
        )
    else:
        photo = FSInputFile(media_file)
        return await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=content.get("caption", ""),
            parse_mode=detect_parse_mode(content.get("caption", "")),
            reply_markup=markup
        )

async def send_document_message(bot, chat_id, content):
    """Отправляет документ"""
    media_file = content.get("media_file", "")
    reply_markup = build_reply_markup(content.get("reply_buttons", ""))
    
    if media_file.startswith(('http://', 'https://')):
        return await bot.send_document(
            chat_id=chat_id,
            document=media_file,
            caption=content.get("caption", ""),
            parse_mode=detect_parse_mode(content.get("caption", "")),
            reply_markup=reply_markup
        )
    else:
        document = FSInputFile(media_file)
        return await bot.send_document(
            chat_id=chat_id,
            document=document,
            caption=content.get("caption", ""),
            parse_mode=detect_parse_mode(content.get("caption", "")),
            reply_markup=reply_markup
        )

async def send_video_message(bot, chat_id, content):
    """Отправляет видео"""
    media_file = content.get("media_file", "")
    reply_markup = build_reply_markup(content.get("reply_buttons", ""))
    
    if media_file.startswith(('http://', 'https://')):
        return await bot.send_video(
            chat_id=chat_id,
            video=media_file,
            caption=content.get("caption", ""),
            parse_mode=detect_parse_mode(content.get("caption", "")),
            reply_markup=reply_markup
        )
    else:
        video = FSInputFile(media_file)
        return await bot.send_video(
            chat_id=chat_id,
            video=video,
            caption=content.get("caption", ""),
            parse_mode=detect_parse_mode(content.get("caption", "")),
            reply_markup=reply_markup
        )

async def send_poll_message(bot, chat_id, content):
    """Отправляет опрос"""
    reply_markup = build_reply_markup(content.get("reply_buttons", ""))
    
    # Парсим опции для опроса
    options = content.get("options", [])
    if isinstance(options, str):
        options = [opt.strip() for opt in options.split(',')]
    
    return await bot.send_poll(
        chat_id=chat_id,
        question=content.get("text", ""),
        options=options,
        reply_markup=reply_markup
    )

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

def detect_parse_mode(text):
    """Автоматически определяет тип форматирования по тексту"""
    if "<" in text and ">" in text:  # HTML теги
        return "HTML"
    elif "**" in text or "__" in text or "`" in text:  # Markdown
        return "Markdown"
    return None

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
    
    print(f"[message_sender] 📋 Создана Reply клавиатура: {buttons}", file=sys.stderr)
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
    
    print(f"[message_sender] 🔘 Создана Inline клавиатура: {buttons_str}", file=sys.stderr)
    return keyboard