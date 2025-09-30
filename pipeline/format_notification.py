#!/usr/bin/env python3
import sys
import html

def format_notification(row, payload):
    """Форматирует текст уведомления"""
    if not row or not row.get("notification") or row["notification"] == "—":
        return None
    
    template = row["notification"]
    try:
        # Заменяем {field} на значения из payload
        text = template
        for key, value in payload.items():
            placeholder = "{" + key + "}"
            if placeholder in text:
                safe_value = html.escape(str(value))   # ← экранируем
                text = text.replace(placeholder, str(safe_value))
        
        print(f"[format_notification] 💬 Уведомление: {template!r} → {text!r}", file=sys.stderr)
        return text
    
    except Exception as e:
        print(f"[format_notification] ❌ Ошибка форматирования: {e}", file=sys.stderr)
        return template