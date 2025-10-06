# \tablebot-pipe-advanced\core\commands_loader.py
# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from aiogram import types

def extract_commands(table_path):
    """Читает CSV и возвращает список BotCommand из строк с bot_command и bot_description"""
    rows = []
    try:
        with open(table_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except Exception as e:
        print(f"[commands] ❌ Ошибка чтения таблицы {table_path}: {e}", file=sys.stderr)
        return []

    commands = []
    print(f"[commands] 📊 Прочитано {len(rows)} строк из {table_path}", file=sys.stderr)
    
    # Отладочная информация о структуре таблицы
    if rows:
        headers = list(rows[0].keys())
        print(f"[commands] 🔍 Заголовки таблицы: {headers}", file=sys.stderr)
        print(f"[commands] 🔍 Доступные колонки: {', '.join(headers)}", file=sys.stderr)

    for i, r in enumerate(rows):
        # Поиск по именам колонок, а не по позициям
        cmd = (r.get("bot_command") or "").strip()
        desc = (r.get("bot_description") or "").strip()

        # Детальная отладка для первых нескольких строк
        if i < 3:  # Показываем отладку для первых 3 строк
            all_columns = {k: v for k, v in r.items() if v.strip()}
            print(f"[commands] 🔍 Строка {i+1} значимые колонки: {all_columns}", file=sys.stderr)

        if cmd and desc:
            if cmd.startswith('/'):
                clean_cmd = cmd[1:]
                commands.append(types.BotCommand(command=clean_cmd, description=desc))
                print(f"[commands] ✅ Найдена команда: /{clean_cmd} -> {desc}", file=sys.stderr)
            else:
                print(f"[commands] ⚠️ Найдена строка с bot_command не начинающимся с '/': '{cmd}', строка {i+1}", file=sys.stderr)
        else:
            # Логируем только если есть частичное заполнение (для отладки)
            if cmd and not desc:
                print(f"[commands] ℹ️ Строка {i+1} имеет bot_command но нет bot_description: '{cmd}'", file=sys.stderr)
            elif desc and not cmd:
                print(f"[commands] ℹ️ Строка {i+1} имеет bot_description но нет bot_command: '{desc}'", file=sys.stderr)

    print(f"[commands] 📋 Итого загружено {len(commands)} команд из таблицы.", file=sys.stderr)
    if commands:
        print(f"[commands] 📝 Список команд: {[f'/{cmd.command} - {cmd.description}' for cmd in commands]}", file=sys.stderr)
    else:
        print(f"[commands] 📝 Команды для установки не найдены в таблице.", file=sys.stderr)

    return commands

# Функция для тестирования
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        table_file = sys.argv[1]
        print(f"[commands] Тестируем извлечение команд из: {table_file}")
        cmds = extract_commands(table_file)
        print(f"[commands] Найдено команд: {len(cmds)}")
    else:
        print("Укажите путь к CSV файлу таблицы.")