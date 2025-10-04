# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
# handlers/callback_handler.py
#!/usr/bin/env python3
from aiogram import types
# Убедитесь, что handle_message из message_handler.py может принять bot
from handlers.message_handler import handle_message

async def handle_callback(callback: types.CallbackQuery, state, table_path, DynFSM, bot):
    """Обрабатывает нажатия на inline-кнопки"""
    # Создаем fake-message из callback данных
    fake_message = types.Message(
        message_id=callback.message.message_id,
        from_user=callback.from_user,
        chat=callback.message.chat,  
        date=callback.message.date,
        text=callback.data  # Используем callback_data как текст команды
    )

    # Обрабатываем как обычное сообщение
    # handle_message должен быть изменён, как показано в предыдущем ответе, чтобы принимать bot
    await handle_message(fake_message, state, table_path, DynFSM, bot)
    await callback.answer()  # Подтверждаем нажатие