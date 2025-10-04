# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
#!/usr/bin/env python3

import sys

def check_guard(row, payload, current_state):
    """Проверяет условия guard'а"""
    if not row or not row.get("condition") or row["condition"] == "—":
        return False
    
    condition = row["condition"]
    print(f"[check_guard] 🛡️ Проверка условия: {condition!r}")
    
    # Простая реализация условий
    if condition.startswith("not_empty:"):
        field = condition.split(":", 1)[1]
        result = bool(payload.get(field))
        print(f"[check_guard] not_empty:{field} → {result}")
        return not result  # True = пропустить
    
    print(f"[check_guard] ⚠️ Неизвестное условие, разрешаю")
    return False