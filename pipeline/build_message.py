# \tablebot-pipe-advanced\pipeline\build_message.py
# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
#!/usr/bin/env python3
import sys
from .format_notification import format_notification

def build_message_content(row, payload):
    """Строит полное описание сообщения для отправки"""
    if not row:
        return None

    content = {"type": "text"}

    # --- НАЧАЛО: Логика для progress_config ---
    progress_text = ""
    progress_config = row.get("progress_config", "").strip()
    if progress_config:
        print(f"[build_message] 🔍 Обработка progress_config: '{progress_config}'", file=sys.stderr)

        # Простой парсер для progress_config
        parts = progress_config.split('|') # Поддержка комбинаций через |
        current_step = 0
        total_steps = 0
        field_name = ""
        bar_length = 8 # Длина визуального прогресс-бара

        for part in parts:
            part = part.strip()
            if part == "disabled":
                progress_text = ""
                break # Отключаем прогресс для этой строки
            elif part.startswith("manual:"):
                # Формат: manual:current/total
                try:
                    current_str, total_str = part[len("manual:"):].split('/')
                    current_step = int(current_str)
                    total_steps = int(total_str)
                    progress_text += f"[Шаг {current_step}/{total_steps}] "
                except (ValueError, IndexError):
                    print(f"[build_message] ⚠️ Неверный формат manual в progress_config: '{part}'", file=sys.stderr)
            elif part.startswith("track:"):
                # Формат: track:field_name
                field_name = part[len("track:"):]
                current_val = payload.get(field_name, 0)
                try:
                    current_step = int(current_val) # Предполагаем, что значение числовое
                    # total_steps может быть задано отдельно или извлекаться из другого места
                    # Для простоты, если не задано в manual, можно задать вручную или извлекать из payload
                    # Пока просто отобразим значение поля
                    progress_text += f"[Прогресс: {current_step}] "
                except (ValueError, TypeError):
                    print(f"[build_message] ⚠️ Значение поля {field_name} не является числом: {current_val}", file=sys.stderr)
            elif part.startswith("bar:"):
                # Формат: bar:field_name
                # Для бара нужен current_step и total_steps
                bar_field_name = part[len("bar:"):]
                current_val = payload.get(bar_field_name, 0)
                try:
                    current_step = int(current_val)
                    # total_steps должен быть известен. Его можно задать в manual или в payload
                    # Попробуем найти из payload или использовать значение по умолчанию/из manual
                    # Попробуем получить total_steps из payload, например, как max_steps
                    total_steps = payload.get("max_steps", 8) # Значение по умолчанию 8
                    # Если в manual был задан total, используем его
                    # Это требует более сложной логики парсинга, чтобы передать total сюда
                    # Упрощаем: если manual был, его total_steps уже использовалось выше для текста
                    # или мы можем использовать отдельное поле в payload или фиксированное значение.
                    # Для этого примера, используем payload.get("total_steps_for_bar") или 8
                    total_steps_bar = payload.get("total_steps_for_bar", total_steps if total_steps > 0 else 8)

                    # Создание визуального бара
                    filled = '█' * min(current_step, total_steps_bar)
                    empty = '░' * max(0, total_steps_bar - current_step)
                    bar_str = f"[{filled}{empty}]"
                    progress_text += bar_str
                except (ValueError, TypeError):
                    print(f"[build_message] ⚠️ Значение поля {bar_field_name} для бара не является числом: {current_val}", file=sys.stderr)

        if progress_text:
             print(f"[build_message] ✅ Сформирован прогресс: '{progress_text}'", file=sys.stderr)
        else:
             print(f"[build_message] 📉 Прогресс отключен или не рассчитан для config: '{progress_config}'", file=sys.stderr)
    # --- КОНЕЦ: Логика для progress_config ---


    # --- НАЧАЛО: Обработка message_text с учетом progress_text ---
    # Текст сообщения (приоритет у message_text, потом notification)
    message_text = ""
    if row.get("message_text") and row["message_text"] != "—":
        message_text = row["message_text"]
    elif row.get("notification") and row["notification"] != "—":
        message_text = format_notification(row, payload)

    # Если есть текст, добавляем к нему progress_text (если он есть)
    if message_text:
        # Вставляем progress_text в начало message_text
        full_message_text = progress_text + message_text
        print(f"[build] message_text до fmt: {full_message_text!r}, payload: {payload}", file=sys.stderr)

        # форматируем {placeholders} самостоятельно
        # Обратите внимание: форматирование теперь применяется к объединённому тексту
        if "{" in full_message_text:
            for key, value in payload.items():
                placeholder = "{" + key + "}"
                if placeholder in full_message_text:
                    # Экранируем HTML-символы, если используете HTML parse_mode
                    safe_val = str(value).replace("&", "&amp;").replace("<", "<").replace(">", ">")
                    full_message_text = full_message_text.replace(placeholder, safe_val)
            print(f"[build] отформатировано: {full_message_text!r}", file=sys.stderr)

        content["text"] = full_message_text # <-- Теперь content["text"] содержит и прогресс, и основной текст

    # --- КОНЕЦ: Обработка message_text с учетом progress_text ---


    # Подпись для медиа
    if row.get("caption") and row["caption"] != "—":
        content["caption"] = row["caption"]

    # Медиа файлы
    if row.get("media_file") and row["media_file"] != "—":
        content["media_file"] = row["media_file"]

        file_ext = row["media_file"].lower()
        # Для URL файлов определяем тип по расширению в URL
        if any(ext in file_ext for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            content["type"] = "photo"
        elif any(ext in file_ext for ext in ['.mp4', '.avi', '.mov', '.mkv']):
            content["type"] = "video"
        elif any(ext in file_ext for ext in ['.pdf', '.doc', '.docx', '.txt']):
            content["type"] = "document"
        elif any(ext in file_ext for ext in ['.mp3', '.wav', '.ogg']):
            content["type"] = "audio"

    # Клавиатуры
    if row.get("reply_markup") and row["reply_markup"] != "—":
        content["reply_buttons"] = row["reply_markup"]

    if row.get("inline_markup") and row["inline_markup"] != "—":
        content["inline_buttons"] = row["inline_markup"]

    # ДОБАВЛЕНО: Передача integrations для запроса геолокации
    if row.get("integrations") and row["integrations"] != "—":
        content["integrations"] = row["integrations"]
        print(f"[build_message] 🔌 Интеграции: {row['integrations']}", file=sys.stderr)

    # Опросы (только если тип ещё не определён)
    if row.get("entities") and row["entities"] != "—" and content.get("type") == "text":
        content["options"] = [opt.strip() for opt in row["entities"].split(',')]
        content["type"] = "poll"

    print(f"[build_message] 🎨 Создан контент: {content['type']}, text: {bool(content.get('text'))}, media: {content.get('media_file')}, integrations: {content.get('integrations', 'нет')}", file=sys.stderr)

    return content