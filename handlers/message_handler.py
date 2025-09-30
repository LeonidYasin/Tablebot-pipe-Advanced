#!/usr/bin/env python3
# handlers/message_handler.py

# Импорты функций пайплайна напрямую из модуля pipeline
from pipeline import (
    find_row,
    check_guard,
    execute_effect,
    build_message_content, # Было notification, теперь build_message
    prepare_integration,   # Было integrations, теперь prepare_integration
    determine_transition   # Было transition
)
from core.message_sender import send_message_by_content
from aiogram.fsm.context import FSMContext
from aiogram import types
import sys # Для логов, если нужно

async def handle_message(msg: types.Message, state: FSMContext, table_path, DynFSM, bot): # <-- Добавлен bot
    """Обрабатывает входящие сообщения"""
    try:
        # Получаем текущее состояние
        data = await state.get_data()
        current_state = data.get("current_state", "start")

        # Создаем payload для пайплайна
        # Добавим chat_id отправителя в payload, это может пригодиться
        payload = {"current_state": current_state, "text": msg.text or "", "chat_id": msg.chat.id}

        print(f"[handler] 📥 Сообщение: state={current_state!r}, text={payload['text']!r}", file=sys.stderr)

        # --- ЗАПУСК ПАЙПЛАЙНА НАПРЯМУЮ ---
        # 1. find_row
        row = find_row(table_path, current_state, payload['text'])

        # 2. check_guard
        skip = check_guard(row, payload, current_state) if row else False

        # 3. execute_effect (теперь принимает bot)
        if row and not skip:
            execute_effect(row, payload, bot) # <-- Передаем bot

        # 4. build_message_content
        message_content = build_message_content(row, payload) if row else None

        # 5. prepare_integration
        integration = prepare_integration(row) if row else None

        # 6. determine_transition
        next_state = determine_transition(row, skip)

        # --- ОБРАБОТКА РЕЗУЛЬТАТОВ ---
        # 7. Отправка сообщения
        if message_content:
            await send_message_by_content(bot, msg.chat.id, message_content)

        # 8. Интеграции (реализация зависит от prepare_integration)
        if integration:
            print(f"[handler] 🔌 Интеграция: {integration}", file=sys.stderr)
            # Вызов интеграции (реализация зависит от возвращаемого prepare_integration формата)
            # Пока оставим как есть, но может потребоваться доработка
            # await run_integration(integration, payload) # <-- Нужно реализовать, если используется

        # 9. Переход состояния
        if next_state and hasattr(DynFSM, next_state):
            await state.set_state(getattr(DynFSM, next_state))
            # Обновляем current_state в FSM
            await state.update_data(current_state=next_state, **payload) # Сохраняем и состояние, и весь payload
            print(f"[handler] 🔄 Переход: {current_state!r} → {next_state!r}", file=sys.stderr)
        else:
            # Если перехода нет, но были изменения в payload (например, save: в execute_effect),
            # всё равно сохраняем обновлённый payload
            await state.update_data(**payload)

    except Exception as e:
        print(f"[handler] 💥 Ошибка: {e}", file=sys.stderr)
        await msg.answer("⚠️ Ошибка обработки")