# \tablebot-pipe-advanced\08_core_loop.py
# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
#!/usr/bin/env python3
import signal
import asyncio
import sys
from pathlib import Path



from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

# Микро-импорты
from core.token_loader import load_bot_token
from core.table_loader import load_table
from core.fsm_builder import extract_states_from_table, create_fsm_from_states

# Старый импорт:
# from core.message_sender import send_message_by_content

# Новый импорт:
from core.message_sender import *

from pipeline import *

from core.commands_loader import extract_commands

# --- Основная функция main ---
async def main():
    TABLE_FILE = sys.argv[1] if len(sys.argv) > 1 else "table.csv"
    table_path = Path(TABLE_FILE)
    
    if not table_path.exists():
        print(f"❌ Файл не найден: {TABLE_FILE}")
        return

    token = load_bot_token()
    if not token:
        print("❌ Токен не найден!")
        return

    # Загрузка FSM
    rows = load_table(TABLE_FILE)
    states_found = extract_states_from_table(rows)
    DynFSM = create_fsm_from_states(states_found)
    print(f"🧠 Создано {len(states_found)} состояний")

    # Настройка бота
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(token)
    
    # --- НАЧАЛО: Добавленный код для установки командного меню ---
    print("[main] 🔄 Начинаю загрузку командного меню из таблицы...", file=sys.stderr)
    try:
        cmds = extract_commands(TABLE_FILE) # <- Вызов функции из core.commands_loader
        if cmds:  # Проверяем, что команды найдены
            await bot.set_my_commands(cmds)     # <- Установка команд боту
            print(f"[main] ✅ Командное меню обновлено: {len(cmds)} команд.", file=sys.stderr)
        else:
            print(f"[main] ⚠️ Команды не найдены в таблице, меню не обновлено.", file=sys.stderr)
    except Exception as e:
        print(f"[main] ❌ Ошибка при установке командного меню: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    # --- КОНЕЦ: Добавленный код ---

    # Хендлеры
    @dp.message(Command("start", "reset"))
    async def start_handler(msg: types.Message, state: FSMContext):
        await state.set_data({"current_state": "start"})
        if msg.text == "/reset":
            await msg.answer("🔄 Бот сброшен")
        await handle_message(msg, state, table_path, DynFSM, bot)

        
    @dp.message()
    async def message_handler(msg: types.Message, state: FSMContext):
        # --- команда перезагрузки меню из таблицы ---
        if msg.text == "/reload_menu":
            cmds = extract_commands(str(table_path))
            await bot.set_my_commands(cmds)
            await msg.answer("✅ Меню перезагружено из таблицы")
            return   # дальше не идём по pipeline
        # --- основной pipeline ---
        await handle_message(msg, state, table_path, DynFSM, bot)

    @dp.callback_query()
    async def callback_handler(callback: types.CallbackQuery, state: FSMContext):
        await handle_callback(callback, state, table_path, DynFSM, bot)

    # Запуск
    print("🚀 Бот запущен. Ctrl+C для остановки.")
    
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("\n🛑 Остановка по запросу пользователя...")
    finally:
        print("⏳ Завершаем работу...")
        try:
            await bot.session.close()
            print("✅ Бот остановлен")
        except:
            print("✅ Бот остановлен (сессия уже закрыта)")



# --- Обработчик сообщений ---
async def handle_message(msg: types.Message, state: FSMContext, table_path, DynFSM, bot):
    """Обрабатывает сообщение через pipeline функций"""
    try:
        data = await state.get_data()
        current_state = data.get("current_state", "start")
        user_role = data.get("user_role", "client")
        
        # Обработка геолокации
        user_input = msg.text
        location_data = None
        
        if msg.location:
            user_input = "<location>"
            location_data = {
                "latitude": msg.location.latitude,
                "longitude": msg.location.longitude
            }
        
        payload = {
            "current_state": current_state, 
            "text": user_input,
            "user_role": user_role,
            "chat_id": msg.chat.id
        }
        
        # Добавляем location в payload если есть
        if location_data:
            payload["location"] = location_data
        
        print(f"📥 Вход: state={current_state!r}, text={payload['text']!r}, role={user_role!r}, location={location_data is not None}")

        # Pipeline вызовов с передачей роли
        row = find_row(table_path, current_state, payload['text'], user_role)
        
        if not row:
            await bot.send_message(msg.chat.id, "❌ Команда не распознана")
            return

        skip = check_guard(row, payload, current_state)
        
        if not skip:
            await execute_effect(row, payload, bot)  # ДОБАВЛЕНО: await
        
        message_content = build_message_content(row, payload)
        integration = prepare_integration(row)
        next_state = determine_transition(row, skip)

        # Отправка результата
        if message_content:
            await send_message_by_content(bot, msg.chat.id, message_content)
        
        if integration:
            print(f"🔌 Интеграция: {integration}")
        
        if next_state and hasattr(DynFSM, next_state):
            await state.set_state(getattr(DynFSM, next_state))
            # Обновляем данные без дублирования
            new_payload = payload.copy()
            new_payload['current_state'] = next_state
            await state.update_data(**new_payload)
            print(f"🔄 Переход: {current_state!r} → {next_state!r}")
        else:
            await state.update_data(**payload)

    except Exception as e:
        print(f"💥 Ошибка: {e}")
        import traceback
        traceback.print_exc()
        await bot.send_message(msg.chat.id, "⚠️ Ошибка обработки")


# --- Обработчик callback'ов ---
async def handle_callback(callback: types.CallbackQuery, state: FSMContext, table_path, DynFSM, bot):
    """Обрабатывает нажатия на inline-кнопки"""
    # Создаем fake-message из callback данных
    fake_message = types.Message(
        message_id=callback.message.message_id,
        from_user=callback.from_user,
        chat=callback.message.chat,  # ← ИСПРАВЛЕНО: callback.message.chat
        date=callback.message.date,
        text=callback.data  # Используем callback_data как текст команды
    )
    
    # Обрабатываем как обычное сообщение
    await handle_message(fake_message, state, table_path, DynFSM, bot)
    await callback.answer()  # Подтверждаем нажатие


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Программа завершена")