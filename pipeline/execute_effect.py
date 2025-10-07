# \tablebot-pipe-advanced\pipeline\execute_effect.py
# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
#!/usr/bin/env python3
import sys
import asyncio

async def reverse_geocode(lat, lon):
    """Преобразует координаты в адрес с помощью Nominatim"""
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="tablebot_taxi")
        location = await asyncio.to_thread(geolocator.reverse, (lat, lon))
        return location.address if location else "Адрес не определен"
    except ImportError:
        print("[execute_effect] ⚠️ Установите geopy: pip install geopy", file=sys.stderr)
        return f"Координаты: {lat}, {lon}"
    except Exception as e:
        print(f"[execute_effect] ❌ Ошибка геокодирования: {e}", file=sys.stderr)
        return f"Координаты: {lat}, {lon}"

async def execute_effect(row, payload, bot):  # ДОБАВЛЕНО: async
    """Выполняет side-effect действия из result_action"""
    # БЕЗОПАСНОЕ ИЗВЛЕЧЕНИЕ - используем .get() с значением по умолчанию
    result_action = (row.get("result_action") or "").strip()
    
    if not result_action or result_action == "—":
        print("[execute_effect] ⏹️ Нет действия", file=sys.stderr)
        return
    
    print(f"[execute_effect] 🔧 Выполняю: {result_action}", file=sys.stderr)
    
    # Парсим действия (могут быть разделены |)
    actions = [a.strip() for a in result_action.split('|') if a.strip()]
    
    for action in actions:
        try:
            if action.startswith('save:'):
                # Формат: save:field_name:value
                parts = action[5:].split(':', 1)
                if len(parts) == 2:
                    field, value_template = parts
                    
                    # Специальная обработка для location
                    if field == "location" and "location" in payload and isinstance(payload["location"], dict):
                        # Сохраняем location как объект, а не как строку
                        payload[field] = payload["location"]
                        print(f"[execute_effect] 💾 Сохранено location как объект: {payload[field]}", file=sys.stderr)
                    else:
                        # Подставляем значения из payload в value_template
                        value = value_template
                        
                        # Обрабатываем все плейсхолдеры {field_name}
                        for key, val in payload.items():
                            placeholder = '{' + key + '}'
                            if placeholder in value:
                                # Для location объекта подставляем отдельные поля
                                if key == "location" and isinstance(val, dict):
                                    value = value.replace("{location[latitude]}", str(val.get('latitude', '')))
                                    value = value.replace("{location[longitude]}", str(val.get('longitude', '')))
                                    value = value.replace("{location}", f"{val.get('latitude')}, {val.get('longitude')}")
                                else:
                                    # Для обычных полей просто подставляем значение
                                    value = value.replace(placeholder, str(val))
                        
                        # Если остались незамещенные плейсхолдеры, пробуем найти их в payload
                        if "{" in value:
                            for key, val in payload.items():
                                placeholder = '{' + key + '}'
                                if placeholder in value:
                                    value = value.replace(placeholder, str(val))
                        
                        payload[field] = value
                        print(f"[execute_effect] 💾 Сохранено: {field} = {value}", file=sys.stderr)
            
            elif action.startswith('clear:'):
                # Формат: clear:field_name
                field = action[6:]
                if field in payload:
                    del payload[field]
                    print(f"[execute_effect] 🗑️ Очищено: {field}", file=sys.stderr)
            
            elif action.startswith('notify_user_by_chat_id:'):
                # Формат: notify_user_by_chat_id:target_chat_id:message_template
                parts = action[22:].split(':', 1)
                if len(parts) == 2:
                    target_chat_id_str, message_template = parts
                    try:
                        target_chat_id = int(target_chat_id_str)
                        # Подставляем значения в шаблон сообщения
                        message = message_template
                        for key, val in payload.items():
                            placeholder = '{' + key + '}'
                            message = message.replace(placeholder, str(val))
                        
                        # Отправляем сообщение (нужен доступ к bot)
                        if bot:
                            from core.message_sender import send_message_by_content
                            await send_message_by_content(bot, target_chat_id, {"type": "text", "text": message})  # ДОБАВЛЕНО: await
                            print(f"[execute_effect] 📨 Уведомление отправлено в чат {target_chat_id}", file=sys.stderr)
                    except ValueError:
                        print(f"[execute_effect] ❌ Неверный chat_id: {target_chat_id_str}", file=sys.stderr)
            
            # В execute_effect.py добавьте обработку location
            elif action.startswith('geocode_location'):
                if 'location' in payload:
                    lat = payload['location']['latitude']
                    lon = payload['location']['longitude']
                    # Вызов API для обратного геокодирования
                    address = await reverse_geocode(lat, lon)
                    payload['address'] = address
                    print(f"[execute_effect] 🗺️ Геокодирование: {lat},{lon} -> {address}", file=sys.stderr)
            
            # В функцию execute_effect добавьте:
            elif action == 'request_location':
                print(f"[execute_effect] 📍 Запрос геолокации", file=sys.stderr)
                # Это действие только для логирования, реальный запрос делается в message_sender
            
            # ДОБАВЛЕНО: Поддержка многоролевых действий из вашей таблицы
            elif action.startswith('notify_operator'):
                # Уведомление оператора
                print(f"[execute_effect] 📢 Уведомление оператора", file=sys.stderr)
                # Здесь можно добавить логику уведомления конкретного оператора
                
            elif action.startswith('notify_executor'):
                # Уведомление исполнителя
                print(f"[execute_effect] 📢 Уведомление исполнителя", file=sys.stderr)
                
            elif action.startswith('notify_client'):
                # Уведомление клиента
                print(f"[execute_effect] 📢 Уведомление клиента", file=sys.stderr)
                
            elif action.startswith('assign_executor'):
                # Назначение исполнителя
                print(f"[execute_effect] 👤 Назначение исполнителя", file=sys.stderr)
                
            elif action.startswith('order_done'):
                # Заказ завершен
                print(f"[execute_effect] ✅ Заказ завершен", file=sys.stderr)
                
            elif action.startswith('order_cancelled'):
                # Заказ отменен
                print(f"[execute_effect] ❌ Заказ отменен", file=sys.stderr)
            
            elif action == 'geocode_location':
                if 'location' in payload and isinstance(payload['location'], dict):
                    lat = payload['location'].get('latitude')
                    lon = payload['location'].get('longitude')
                    if lat and lon:
                        address = await reverse_geocode(lat, lon)
                        payload['address'] = address
                        payload['from_address'] = address
                        print(f"[execute_effect] 🗺️ Геокодирование: {lat},{lon} -> {address}", file=sys.stderr)
            
            
            
            else:
                print(f"[execute_effect] ⚠️ Неизвестное действие: {action}", file=sys.stderr)
                
        except Exception as e:
            print(f"[execute_effect] ❌ Ошибка выполнения {action}: {e}", file=sys.stderr)
           
           
