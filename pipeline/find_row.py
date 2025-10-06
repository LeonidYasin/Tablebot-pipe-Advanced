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

    for row in rows:
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
            print(f"[find_row] ✅ Найдено: state={from_state!r}, command={command!r}, role={role!r} -> {row.get('to_state', 'N/A')!r}", file=sys.stderr)
            return row

    print(f"[find_row] ❌ Не найдено подходящей строки", file=sys.stderr)
    return None