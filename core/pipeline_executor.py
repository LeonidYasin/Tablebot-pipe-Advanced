# Copyright (C) 2025 Leonid Yasin
# This file is part of Tablebot-pipe-Advanced and is licensed under the GNU GPL v3.0.
# See the LICENSE file for details.
#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import os

async def execute_pipeline(table_path, payload, scripts_chain):
    """Выполняет цепочку микросервисов и возвращает результат"""
    try:
        # Создаем временный файл с входными данными
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json', delete=False) as f:
            json.dump(payload, f, ensure_ascii=False)
            input_file = f.name

        result_file = None
        intermediate_files = []
        success = True
        
        for i, (script_name, script_args) in enumerate(scripts_chain):
            # Определяем входной файл
            if i == 0:
                input_f = input_file
            else:
                input_f = intermediate_files[-1]

            # Определяем выходной файл
            if i == len(scripts_chain) - 1:
                with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json', delete=False) as f:
                    result_file = f.name
                output_f = result_file
            else:
                with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json', delete=False) as f:
                    intermediate_files.append(f.name)
                output_f = intermediate_files[-1]

            # Запускаем скрипт
            cmd = [sys.executable, script_name] + script_args
            print(f"[pipeline] 🔧 Запуск {script_name}...", file=sys.stderr)
            
            with open(input_f, 'r', encoding='utf-8') as infile:
                with open(output_f, 'w', encoding='utf-8') as outfile:
                    process = subprocess.run(
                        cmd,
                        stdin=infile,
                        stdout=outfile,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=5
                    )
                    
                    if process.stderr:
                        print(f"[pipeline] {script_name} stderr: {process.stderr.strip()}", file=sys.stderr)
                    
                    if process.returncode != 0:
                        print(f"[pipeline] ❌ {script_name} завершился с ошибкой", file=sys.stderr)
                        success = False
                        break

        # Читаем результат
        result = None
        if success and result_file and os.path.exists(result_file):
            with open(result_file, 'r', encoding='utf-8') as f:
                result_data = f.read().strip()
                if result_data:
                    result = json.loads(result_data)

        # Очистка временных файлов
        for f in [input_file, result_file] + intermediate_files:
            try:
                if f and os.path.exists(f):
                    os.unlink(f)
            except:
                pass

        return result

    except subprocess.TimeoutExpired:
        print("[pipeline] ❌ Пайплайн завис", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[pipeline] 💥 Ошибка: {e}", file=sys.stderr)
        return None