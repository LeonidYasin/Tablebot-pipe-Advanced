# tablebot-pipe-advanced\pipeline\check_guard.py
# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
#!/usr/bin/env python3
import sys

def check_guard(row, payload, current_state):
    """Проверяет guard-условия для перехода"""
    # БЕЗОПАСНОЕ ИЗВЛЕЧЕНИЕ - используем .get() с значением по умолчанию
    condition = (row.get("condition") or "").strip()
    
    if not condition or condition == "—":
        return False
    
    print(f"[check_guard] 🛡️ Проверка условия: {condition}", file=sys.stderr)
    
    try:
        if condition.startswith('not_empty:'):
            field = condition[10:]
            value = payload.get(field, "")
            if not value or str(value).strip() == "":
                print(f"[check_guard] ❌ Условие не выполнено: поле {field} пустое", file=sys.stderr)
                return True
            else:
                print(f"[check_guard] ✅ Условие выполнено: поле {field} не пустое", file=sys.stderr)
                return False
                
        elif condition.startswith('equals:'):
            # Формат: equals:field:value
            parts = condition[7:].split(':', 1)
            if len(parts) == 2:
                field, expected_value = parts
                actual_value = str(payload.get(field, ""))
                if actual_value != expected_value:
                    print(f"[check_guard] ❌ Условие не выполнено: {field}={actual_value} != {expected_value}", file=sys.stderr)
                    return True
                else:
                    print(f"[check_guard] ✅ Условие выполнено: {field}={actual_value}", file=sys.stderr)
                    return False
        
        # ДОБАВЛЕНО: Проверка роли пользователя
        elif condition.startswith('role:'):
            # Формат: role:expected_role
            expected_role = condition[5:]
            user_role = payload.get("user_role", "client")
            if user_role != expected_role:
                print(f"[check_guard] ❌ Условие роли не выполнено: user_role={user_role} != {expected_role}", file=sys.stderr)
                return True
            else:
                print(f"[check_guard] ✅ Условие роли выполнено: user_role={user_role}", file=sys.stderr)
                return False
        
        # ДОБАВЛЕНО: Проверка длины текста
        elif condition.startswith('length>'):
            # Формат: length>min_length:field
            parts = condition[7:].split(':', 1)
            if len(parts) == 2:
                min_length_str, field = parts
                try:
                    min_length = int(min_length_str)
                    text = str(payload.get(field, ""))
                    if len(text) <= min_length:
                        print(f"[check_guard] ❌ Условие длины не выполнено: len({field})={len(text)} <= {min_length}", file=sys.stderr)
                        return True
                    else:
                        print(f"[check_guard] ✅ Условие длины выполнено: len({field})={len(text)} > {min_length}", file=sys.stderr)
                        return False
                except ValueError:
                    print(f"[check_guard] ❌ Неверный формат длины: {min_length_str}", file=sys.stderr)
                    return True
        
        # ДОБАВЛЕНО: Проверка наличия location
        elif condition == 'has_location':
            location = payload.get("location")
            if not location:
                print(f"[check_guard] ❌ Условие location не выполнено: location отсутствует", file=sys.stderr)
                return True
            else:
                print(f"[check_guard] ✅ Условие location выполнено", file=sys.stderr)
                return False
        
        else:
            print(f"[check_guard] ⚠️ Неизвестный тип условия: {condition}", file=sys.stderr)
            return False
        
    except Exception as e:
        print(f"[check_guard] ❌ Ошибка проверки условия: {e}", file=sys.stderr)
        return True
    
    return False