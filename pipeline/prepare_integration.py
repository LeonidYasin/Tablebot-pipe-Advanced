# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
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