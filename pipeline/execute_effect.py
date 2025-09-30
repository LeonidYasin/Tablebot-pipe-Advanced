# pipeline/execute_effect.py
#!/usr/bin/env python3
import sys
import asyncio # Если нужно немного подождать перед отправкой

def execute_effect(row, payload, bot): # <-- Добавляем bot как параметр
    """Выполняет side-effect действия"""
    action = row.get("result_action", "").strip()
    if not action:
        print("[execute_effect] ⏹️ Нет действия", file=sys.stderr)
        return

    print(f"[execute_effect] 🛠️ Выполнение: {action!r}", file=sys.stderr)

    # --- НАЧАЛО: Новый эффект для отправки другому пользователю по chat_id ---
    if action.startswith("notify_user_by_chat_id:"):
        try:
            # Формат: notify_user_by_chat_id:target_chat_id:message_template
            # message_template может содержать плейсхолдеры {field}, которые будут заменены из payload
            parts = action.split(":", 2)
            if len(parts) < 3:
                print(f"[execute_effect] ⚠️ Неверный формат notify_user_by_chat_id: {action}", file=sys.stderr)
                return
            _, target_chat_id_str, message_template = parts

            # Подстановка плейсхолдеров из payload в message_template
            text_to_send = message_template
            for key, value in payload.items():
                placeholder = "{" + key + "}"
                if placeholder in text_to_send:
                    # Экранируем HTML, если используете parse_mode HTML
                    # import html # Если нужно
                    # safe_val = html.escape(str(value))
                    # text_to_send = text_to_send.replace(placeholder, safe_val)
                    # Пока без экранирования, если не нужно
                    text_to_send = text_to_send.replace(placeholder, str(value))

            target_chat_id = int(target_chat_id_str)
            print(f"[execute_effect] 📬 Отправка в {target_chat_id!r}: {text_to_send!r}", file=sys.stderr)
            # Используем bot для отправки
            # Запускаем в отдельной задаче, чтобы не блокировать основной пайплайн
            # asyncio.create_task(bot.send_message(target_chat_id, text_to_send))
            # Или просто await (блокирует, но проще)
            asyncio.run_coroutine_threadsafe(bot.send_message(target_chat_id, text_to_send), bot.session._connector._loop)
            # await bot.send_message(target_chat_id, text_to_send) # Если не нужно асинхронно

        except ValueError:
            print(f"[execute_effect] ⚠️ Неверный формат chat_id в notify_user_by_chat_id: {action}", file=sys.stderr)
        except Exception as e:
            print(f"[execute_effect] ❌ Ошибка при отправке уведомления: {e}", file=sys.stderr)
        return
    # --- КОНЕЦ: Новый эффект для отправки другому пользователю ---

    # --- СТАРЫЕ эффекты ---
    if action.startswith("save:"):
        try:
            _, field, value = action.split(":", 2)
            # Подстановка значений из payload в value (если нужно)
            for k, v in payload.items():
                placeholder = "{" + k + "}"
                if placeholder in value:
                    value = value.replace(placeholder, str(v))
            payload[field] = value
            print(f"[execute_effect] 💾 Сохранено {field} = {value!r}", file=sys.stderr)
        except ValueError:
            print(f"[execute_effect] ⚠️ Неверный формат save: {action}", file=sys.stderr)
    elif action.startswith("clear:"):
        field = action.split(":", 1)[1]
        payload.pop(field, None)
        print(f"[execute_effect] 🧹 Очищено {field}", file=sys.stderr)
    else:
        print(f"[execute_effect] ❓ Неизвестное действие: {action}", file=sys.stderr)
