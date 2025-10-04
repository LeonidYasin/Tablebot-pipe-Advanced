# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
#!/usr/bin/env python3
import sys
from aiogram.types import FSInputFile
from .markup_builder import build_reply_markup, build_inline_markup
from .format_detector import detect_parse_mode

async def send_photo_message(bot, chat_id, content):
    """Отправляет фото"""
    media_file = content.get("media_file", "")
    inline_markup = build_inline_markup(content.get("inline_buttons", ""))
    reply_markup = build_reply_markup(content.get("reply_buttons", ""))
    
    # Используем inline-кнопки если есть, иначе обычные
    markup = inline_markup if inline_markup else reply_markup
    
    caption = content.get("caption", "")
    parse_mode = detect_parse_mode(caption)
    
    print(f"[media_sender] 🖼️ Отправка фото: {media_file}", file=sys.stderr)
    
    if media_file.startswith(('http://', 'https://')):
        return await bot.send_photo(
            chat_id=chat_id,
            photo=media_file,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=markup
        )
    else:
        photo = FSInputFile(media_file)
        return await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=markup
        )

async def send_document_message(bot, chat_id, content):
    """Отправляет документ"""
    media_file = content.get("media_file", "")
    reply_markup = build_reply_markup(content.get("reply_buttons", ""))
    caption = content.get("caption", "")
    parse_mode = detect_parse_mode(caption)
    
    print(f"[media_sender] 📄 Отправка документа: {media_file}", file=sys.stderr)
    
    if media_file.startswith(('http://', 'https://')):
        return await bot.send_document(
            chat_id=chat_id,
            document=media_file,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
    else:
        document = FSInputFile(media_file)
        return await bot.send_document(
            chat_id=chat_id,
            document=document,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )

async def send_video_message(bot, chat_id, content):
    """Отправляет видео"""
    media_file = content.get("media_file", "")
    reply_markup = build_reply_markup(content.get("reply_buttons", ""))
    caption = content.get("caption", "")
    parse_mode = detect_parse_mode(caption)
    
    print(f"[media_sender] 🎥 Отправка видео: {media_file}", file=sys.stderr)
    
    if media_file.startswith(('http://', 'https://')):
        return await bot.send_video(
            chat_id=chat_id,
            video=media_file,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
    else:
        video = FSInputFile(media_file)
        return await bot.send_video(
            chat_id=chat_id,
            video=video,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )