# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
#!/usr/bin/env python3

def detect_parse_mode(text):
    """Автоматически определяет тип форматирования по тексту"""
    if not text:
        return None
    
    if "<" in text and ">" in text:  # HTML теги
        return "HTML"
    elif "**" in text or "__" in text or "`" in text:  # Markdown
        return "MarkdownV2"
    return None