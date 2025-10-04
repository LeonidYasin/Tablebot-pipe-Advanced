# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
#!/usr/bin/env python3
import csv
import sys  # ← ДОБАВИТЬ

def find_row(table_path, current_state, user_text):
    """Ищет строку в таблице по состоянию и команде"""
    try:
        with open(table_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except Exception as e:
        print(f"[find_row] ❌ Ошибка загрузки таблицы: {e}", file=sys.stderr)
        return None
    
    print(f"[find_row] 🔍 Поиск: state={current_state!r}, text={user_text!r}", file=sys.stderr)
    
    for row in rows:
        if row["from_state"] == current_state:
            # Команда <text> подходит для любого текста (кроме команд)
            if row["command"] == "<text>" and not user_text.startswith('/'):
                print(f"[find_row] ✅ Найдено по <text>: {row['to_state']!r}", file=sys.stderr)
                return row
            # Точное совпадение команды
            elif row["command"] == user_text:
                print(f"[find_row] ✅ Найдено по команде: {row['to_state']!r}", file=sys.stderr)
                return row
    
    print(f"[find_row] ❌ Не найдено подходящей строки", file=sys.stderr)
    return None