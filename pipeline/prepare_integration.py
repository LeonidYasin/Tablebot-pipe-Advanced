#!/usr/bin/env python3

import sys

def prepare_integration(row):
    """Подготавливает данные для интеграций"""
    if not row or not row.get("integrations") or row["integrations"] == "—":
        return None
    
    integration = row["integrations"]
    print(f"[prepare_integration] 🔌 Интеграция: {integration!r}")
    
    # Можно добавить парсинг разных типов интеграций
    if integration.startswith("http:"):
        print(f"[prepare_integration] 🌐 HTTP запрос: {integration}")
    
    elif integration.startswith("email:"):
        print(f"[prepare_integration] 📧 Email: {integration}")
    
    return integration