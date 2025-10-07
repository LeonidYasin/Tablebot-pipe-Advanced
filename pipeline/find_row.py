# \tablebot-pipe-advanced\pipeline\find_row.py
# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

def find_row(table_path, current_state, user_input, user_role=None):
    """Находит подходящую строку в таблице для текущего состояния и ввода"""
    try:
        with open(table_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except Exception as e:
        print(f"[find_row] ❌ Ошибка чтения таблицы: {e}", file=sys.stderr)
        return None

    print(f"[find_row] 🔍 Поиск: state={current_state!r}, text={user_input!r}, role={user_role!r}", file=sys.stderr)

    matching_rows = []
    
    for i, row in enumerate(rows):
        # Безопасное извлечение всех полей по именам
        from_state = (row.get("from_state") or "").strip()
        command = (row.get("command") or "").strip()
        role = (row.get("role") or "").strip()
        condition = (row.get("condition") or "").strip()

        # Пропускаем строки с пустыми обязательными полями
        if not from_state or not command:
            continue

        # Проверяем совпадение состояния
        if from_state != current_state and from_state != "any":
            continue

        # Проверяем совпадение роли (если роль указана в таблице)
        if role and user_role and role != user_role and role != "any":
            continue

        # Проверяем совпадение команды
        if command == user_input or command == "<text>" or command == "<location>":
            matching_rows.append((i + 2, row))  # +2 потому что: 0-based index + 1 строка заголовков + 1 для человекочитаемого номера
            print(f"[find_row] ✅ Найдено совпадение: строка {i+2}, state={from_state!r}, command={command!r}, role={role!r} -> {row.get('to_state', 'N/A')!r}", file=sys.stderr)

    # Обработка дублирования строк
    if len(matching_rows) > 1:
        print(f"[find_row] ⚠️  Обнаружено дублирование! Найдено {len(matching_rows)} подходящих строк:", file=sys.stderr)
        for line_num, row in matching_rows:
            print(f"[find_row] ⚠️   - Строка {line_num}: from_state={row.get('from_state')!r}, command={row.get('command')!r}, to_state={row.get('to_state')!r}", file=sys.stderr)
        
        # Выбираем первую строку (приоритет по порядку в таблице)
        selected_line, selected_row = matching_rows[0]
        print(f"[find_row] ⚠️  Выбрана строка {selected_line} (первая в таблице)", file=sys.stderr)
        print(f"[find_row] ✅ Финальный выбор: state={selected_row.get('from_state')!r}, command={selected_row.get('command')!r} -> {selected_row.get('to_state', 'N/A')!r}", file=sys.stderr)
        return selected_row
    
    elif len(matching_rows) == 1:
        line_num, row = matching_rows[0]
        print(f"[find_row] ✅ Найдена одна подходящая строка {line_num}: state={row.get('from_state')!r}, command={row.get('command')!r} -> {row.get('to_state', 'N/A')!r}", file=sys.stderr)
        return row
    else:
        print(f"[find_row] ❌ Не найдено подходящих строк", file=sys.stderr)
        return None