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
    """Обрабатывает сообщение через pipeline функций с полным логированием"""
    try:
        print(f"🎯 [handler] НАЧАЛО ОБРАБОТКИ СООБЩЕНИЯ", file=sys.stderr)
        
        # === ШАГ 1: Получение данных из FSM ===
        print(f"📥 [handler] Получение данных из FSM...", file=sys.stderr)
        data = await state.get_data()
        current_state = data.get("current_state", "start")
        user_role = data.get("user_role", "client")
        
        print(f"📊 [handler] Текущее состояние: {current_state!r}", file=sys.stderr)
        print(f"👤 [handler] Роль пользователя: {user_role!r}", file=sys.stderr)
        print(f"🗂️ [handler] Все ключи в FSM: {list(data.keys())}", file=sys.stderr)
        
        # Детальное логирование важных полей
        for key in ['address', 'from_address', 'to_address', 'phone', 'location']:
            if key in data:
                print(f"📋 [handler] {key} в FSM: {data[key]!r}", file=sys.stderr)
        
        # === ШАГ 2: Обработка входящего сообщения ===
        print(f"📨 [handler] Обработка входящего сообщения...", file=sys.stderr)
        
        # ИНИЦИАЛИЗАЦИЯ user_input ДО использования (исправление ошибки)
        user_input = msg.text or ""
        location_data = None
        
        # Обработка геолокации
        if msg.location:
            print(f"📍 [handler] Обнаружена геолокация!", file=sys.stderr)
            user_input = "<location>"
            location_data = {
                "latitude": msg.location.latitude,
                "longitude": msg.location.longitude
            }
            print(f"📍 [handler] Координаты: {location_data}", file=sys.stderr)
        
        print(f"📝 [handler] Обработанный ввод: {user_input!r}", file=sys.stderr)
        
        # === ШАГ 3: Формирование payload ===
        print(f"🔄 [handler] Формирование payload...", file=sys.stderr)
        
        # ВАЖНО: Копируем ВСЕ данные из FSM в payload чтобы не потерять их
        payload = data.copy()
        payload.update({
            "current_state": current_state,
            "text": user_input,  # Используем инициализированную переменную
            "user_role": user_role, 
            "chat_id": msg.chat.id
        })
        
        # Добавляем location в payload если есть
        if location_data:
            payload["location"] = location_data
            print(f"📍 [handler] Location добавлен в payload", file=sys.stderr)
        
        print(f"📦 [handler] Payload сформирован. Ключи: {list(payload.keys())}", file=sys.stderr)
        print(f"🔍 [handler] Детали payload:", file=sys.stderr)
        for key, value in payload.items():
            if key not in ['location']:  # Не логируем большие объекты
                print(f"   {key}: {value!r}", file=sys.stderr)
        
        # === ШАГ 4: Запуск пайплайна обработки ===
        print(f"⚙️ [handler] Запуск пайплайна обработки...", file=sys.stderr)
        
        # 4.1 Поиск подходящей строки в таблице
        print(f"🔍 [handler] Поиск строки в таблице...", file=sys.stderr)
        row = find_row(table_path, current_state, payload['text'], user_role)
        
        if not row:
            print(f"❌ [handler] Строка не найдена в таблице", file=sys.stderr)
            await bot.send_message(msg.chat.id, "❌ Команда не распознана")
            return
        
        print(f"✅ [handler] Найдена строка: from_state={row.get('from_state')!r} -> to_state={row.get('to_state')!r}", file=sys.stderr)
        
        # 4.2 Проверка условий (guards)
        print(f"🛡️ [handler] Проверка условий...", file=sys.stderr)
        skip = check_guard(row, payload, current_state)
        print(f"🛡️ [handler] Результат проверки условий: skip={skip}", file=sys.stderr)
        
        # 4.3 Выполнение эффектов (если условия пройдены)
        if not skip:
            print(f"⚡ [handler] Выполнение эффектов...", file=sys.stderr)
            await execute_effect(row, payload, bot)
            print(f"✅ [handler] Эффекты выполнены", file=sys.stderr)
        else:
            print(f"⏭️ [handler] Эффекты пропущены (skip=True)", file=sys.stderr)
        
        # 4.4 Построение сообщения
        print(f"💬 [handler] Построение контента сообщения...", file=sys.stderr)
        message_content = build_message_content(row, payload)
        if message_content:
            print(f"✅ [handler] Контент сообщения построен: type={message_content.get('type')}", file=sys.stderr)
        else:
            print(f"ℹ️ [handler] Контент сообщения пустой", file=sys.stderr)
        
        # 4.5 Подготовка интеграций
        print(f"🔌 [handler] Подготовка интеграций...", file=sys.stderr)
        integration = prepare_integration(row)
        if integration:
            print(f"🔌 [handler] Интеграция подготовлена: {integration}", file=sys.stderr)
        
        # 4.6 Определение следующего состояния
        print(f"🔄 [handler] Определение перехода...", file=sys.stderr)
        next_state = determine_transition(row, skip)
        print(f"🔄 [handler] Следующее состояние: {next_state!r}", file=sys.stderr)
        
        # === ШАГ 5: Отправка результата пользователю ===
        print(f"📤 [handler] Отправка результата пользователю...", file=sys.stderr)
        if message_content:
            await send_message_by_content(bot, msg.chat.id, message_content)
            print(f"✅ [handler] Сообщение отправлено", file=sys.stderr)
        
        if integration:
            print(f"🔌 [handler] Интеграция: {integration}", file=sys.stderr)
        
        # === ШАГ 6: Обновление состояния FSM ===
        print(f"💾 [handler] Обновление состояния FSM...", file=sys.stderr)
        
        if next_state and hasattr(DynFSM, next_state):
            await state.set_state(getattr(DynFSM, next_state))
            print(f"✅ [handler] Состояние FSM установлено: {next_state!r}", file=sys.stderr)
        
        # ВАЖНО: ВСЕГДА сохраняем все данные payload в FSM
        new_payload = payload.copy()
        new_payload['current_state'] = next_state if next_state else current_state
        await state.update_data(**new_payload)
        
        print(f"🔄 [handler] ПЕРЕХОД ВЫПОЛНЕН: {current_state!r} → {next_state!r}", file=sys.stderr)
        print(f"💾 [handler] Сохраненные ключи в FSM: {list(new_payload.keys())}", file=sys.stderr)
        print(f"🎯 [handler] ОБРАБОТКА ЗАВЕРШЕНА УСПЕШНО", file=sys.stderr)

    except Exception as e:
        print(f"💥 [handler] КРИТИЧЕСКАЯ ОШИБКА: {e}", file=sys.stderr)
        import traceback
        print(f"💥 [handler] Трассировка ошибки:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        await bot.send_message(msg.chat.id, "⚠️ Ошибка обработки")

# --- Обработчик callback'ов ---
async def handle_callback(callback: types.CallbackQuery, state: FSMContext, table_path, DynFSM, bot):
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
    await handle_message(fake_message, state, table_path, DynFSM, bot)
    await callback.answer()  # Подтверждаем нажатие


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Программа завершена")