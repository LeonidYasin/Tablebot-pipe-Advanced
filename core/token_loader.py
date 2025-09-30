#!/usr/bin/env python3
import os
import sys  # ← ДОБАВИТЬ ЭТО
from pathlib import Path

def load_bot_token():
    """Загружает токен бота из переменных окружения или файлов"""
    token = os.getenv("BOT_TOKEN")
    if token:
        print("[core] 🗝️ Токен из переменной окружения", file=sys.stderr)
        return token.strip()

    # Проверяем .env файл
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("BOT_TOKEN="):
                value = line.split("=", 1)[1].strip().strip('"\'')
                if value:
                    print("[core] 🗝️ Токен из .env", file=sys.stderr)
                    return value

    # Проверяем token.env
    token_file = Path("token.env")
    if token_file.exists():
        raw = token_file.read_text(encoding="utf-8").strip()
        if raw:
            print("[core] 🗝️ Токен из token.env", file=sys.stderr)
            return raw

    return None