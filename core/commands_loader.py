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

    for i, r in enumerate(rows):
        cmd = (r.get("bot_command") or "").strip()
        desc = (r.get("bot_description") or "").strip()

        if cmd and desc:
            # Проверяем, начинается ли команда с '/'
            if cmd.startswith('/'):
                # Убираем '/' перед созданием команды, как ожидает aiogram
                clean_cmd = cmd[1:]
                commands.append(types.BotCommand(command=clean_cmd, description=desc))
                print(f"[commands] ✅ Найдена команда: /{clean_cmd} -> {desc}", file=sys.stderr)
            else:
                print(f"[commands] ⚠️ Найдена строка с bot_command не начинающимся с '/': '{cmd}', строка {i+1}", file=sys.stderr)
        else:
            # Логируем строки, которые не подходят (опционально)
            # if not cmd and not desc:
            #      print(f"[commands] ℹ️ Строка {i+1} не содержит bot_command и bot_description, пропущена.", file=sys.stderr)
            # elif not cmd:
            #      print(f"[commands] ℹ️ Строка {i+1} не содержит bot_command, пропущена.", file=sys.stderr)
            # elif not desc:
            #      print(f"[commands] ℹ️ Строка {i+1} не содержит bot_description, пропущена.", file=sys.stderr)
            pass

    print(f"[commands] 📋 Итого загружено {len(commands)} команд из таблицы.", file=sys.stderr)
    if commands:
        print(f"[commands] 📝 Список команд: {[f'/{cmd.command} - {cmd.description}' for cmd in commands]}", file=sys.stderr)
    else:
        print(f"[commands] 📝 Команды для установки не найдены в таблице.", file=sys.stderr)

    return commands