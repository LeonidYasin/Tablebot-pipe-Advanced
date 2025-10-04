# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
#!/usr/bin/env python3
import csv
import sys  # ← ДОБАВИТЬ
from pathlib import Path

def load_table(file_path):
    """Загружает таблицу из CSV или XLSX файла"""
    path = Path(file_path)
    
    if path.suffix.lower() in ['.xlsx', '.xls']:
        return load_excel_table(file_path)
    elif path.suffix.lower() == '.csv':
        return load_csv_table(file_path)
    else:
        print(f"[table_loader] ❌ Неподдерживаемый формат: {path.suffix}", file=sys.stderr)
        raise ValueError(f"Неподдерживаемый формат: {path.suffix}")

def load_csv_table(file_path):
    """Загружает CSV таблицу"""
    try:
        with open(file_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        print(f"[table_loader] 📄 Загружен CSV: {len(rows)} строк", file=sys.stderr)
        return rows
    except Exception as e:
        print(f"[table_loader] ❌ Ошибка загрузки CSV: {e}", file=sys.stderr)
        raise Exception(f"Ошибка загрузки CSV: {e}")

def load_excel_table(file_path):
    """Загружает Excel таблицу"""
    try:
        import pandas as pd
        df = pd.read_excel(file_path)
        rows = df.to_dict('records')
        
        # Конвертируем все значения в строки
        for row in rows:
            for key in row:
                if pd.isna(row[key]):
                    row[key] = ""
                else:
                    row[key] = str(row[key]).strip()
        
        print(f"[table_loader] 📊 Загружен Excel: {len(rows)} строк", file=sys.stderr)
        return rows
    except ImportError:
        print("[table_loader] ❌ Для работы с Excel установите: pip install pandas openpyxl", file=sys.stderr)
        raise Exception("Для работы с Excel установите: pip install pandas openpyxl")
    except Exception as e:
        print(f"[table_loader] ❌ Ошибка загрузки Excel: {e}", file=sys.stderr)
        raise Exception(f"Ошибка загрузки Excel: {e}")