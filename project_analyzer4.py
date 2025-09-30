import os
import argparse
from pathlib import Path
from datetime import datetime
import humanize

# Константы по умолчанию
DEFAULT_EXTENSIONS = ['.py', '.md', '.txt', '.csv']
EXCLUDED_FILES = ['project_overview.txt', '.gitignore', 'temp.txt']

def get_output_filename(base_name="project_overview"):
    """Генерирует имя файла с временной меткой."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.txt"

def is_excluded_output_file(filename):
    """Проверяет, является ли файл итоговым отчетом."""
    return (filename.startswith("project_overview_") and 
            filename.endswith(".txt") and
            len(filename) > len("project_overview_XXXXXX.txt"))

def should_include_file(file_path, included_extensions):
    """Проверяет, нужно ли включать файл в анализ."""
    file_path = Path(file_path)
    
    # Исключаем скрытые файлы и системные файлы
    if any(part.startswith('.') for part in file_path.parts):
        return False
    
    # Исключаем файлы из черного списка
    if file_path.name in EXCLUDED_FILES:
        return False
    
    # Исключаем итоговые отчеты
    if is_excluded_output_file(file_path.name):
        return False
    
    # Проверяем расширение
    if file_path.suffix.lower() not in included_extensions:
        return False
    
    return True

def get_file_info(file_path):
    """Возвращает информацию о файле (размер, время изменения)."""
    try:
        stat = file_path.stat()
        return {
            'size': stat.st_size,
            'mtime': stat.st_mtime,
            'size_str': humanize.naturalsize(stat.st_size),
            'mtime_str': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        }
    except OSError:
        return None

def read_file_content(file_path):
    """Читает содержимое файла с обработкой ошибок."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Добавляем перенос строки если его нет в конце
            if content and not content.endswith('\n'):
                content += '\n'
            return content
    except UnicodeDecodeError:
        return "!!! НЕВОЗМОЖНО ПРОЧИТАТЬ (бинарный файл или неверная кодировка)\n"
    except Exception as e:
        return f"!!! ОШИБКА ПРИ ЧТЕНИИ: {e}\n"

def get_directory_tree(project_path, included_extensions):
    """Генерирует древовидную структуру каталогов проекта."""
    project_path = Path(project_path)
    tree_lines = []
    file_count = 0

    def build_tree(directory, prefix=""):
        nonlocal file_count
        contents = []
        try:
            contents = sorted(os.listdir(directory))
        except PermissionError:
            return [f"{prefix}└── ⚠️ Нет доступа"]

        files = []
        dirs = []

        for item in contents:
            item_path = directory / item
            if item_path.is_dir():
                if not item.startswith('.'):  # Исключаем скрытые папки
                    dirs.append(item)
            else:
                if should_include_file(item_path, included_extensions):
                    files.append(item)

        # Сначала файлы, потом папки
        items = files + dirs
        tree = []

        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            item_path = directory / item

            if item_path.is_file():
                # Это файл
                file_count += 1
                file_info = get_file_info(item_path)
                if file_info:
                    tree.append(f"{prefix}{'└── ' if is_last else '├── '}📄 {item} ({file_info['size_str']})")
                else:
                    tree.append(f"{prefix}{'└── ' if is_last else '├── '}📄 {item} (⚠️)")
            else:
                # Это папка
                tree.append(f"{prefix}{'└── ' if is_last else '├── '}📁 {item}/")
                extension = "    " if is_last else "│   "
                tree.extend(build_tree(item_path, prefix + extension))

        return tree

    tree_lines.append("🌳 ДРЕВОВИДНАЯ СТРУКТУРА ПРОЕКТА:")
    tree_lines.append(".")
    tree_lines.extend(build_tree(project_path))
    tree_lines.append("")  # Пустая строка для разделения

    return tree_lines, file_count

def calculate_project_stats(project_path, included_extensions):
    """Собирает подробную статистику по проекту."""
    project_path = Path(project_path)
    stats = {
        'total_files': 0,
        'total_folders': 0,
        'files_by_extension': {},
        'files_by_folder': {},
        'total_size': 0,
        'largest_file': {'path': None, 'size': 0},
        'oldest_file': {'path': None, 'mtime': float('inf')},
        'newest_file': {'path': None, 'mtime': 0},
        'folder_structure': {}
    }

    for root, dirs, files in os.walk(project_path):
        # Убираем скрытые папки из обработки
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        current_folder = Path(root).relative_to(project_path)
        stats['total_folders'] += 1

        # Статистика по файлам в папке
        folder_files_count = 0
        folder_size = 0

        for file in files:
            file_path = Path(root) / file
            
            if not should_include_file(file_path, included_extensions):
                continue

            file_info = get_file_info(file_path)
            if not file_info:
                continue

            # Общая статистика
            stats['total_files'] += 1
            stats['total_size'] += file_info['size']

            # Статистика по расширениям
            ext = file_path.suffix.lower()
            stats['files_by_extension'][ext] = stats['files_by_extension'].get(ext, 0) + 1

            # Самый большой файл
            if file_info['size'] > stats['largest_file']['size']:
                stats['largest_file'] = {'path': file_path.relative_to(project_path), 'size': file_info['size']}

            # Самый старый и новый файл
            if file_info['mtime'] < stats['oldest_file']['mtime']:
                stats['oldest_file'] = {'path': file_path.relative_to(project_path), 'mtime': file_info['mtime']}
            if file_info['mtime'] > stats['newest_file']['mtime']:
                stats['newest_file'] = {'path': file_path.relative_to(project_path), 'mtime': file_info['mtime']}

            # Статистика по папкам
            folder_files_count += 1
            folder_size += file_info['size']

        # Сохраняем статистику по текущей папке
        if current_folder != Path('.'):
            stats['files_by_folder'][str(current_folder)] = {
                'file_count': folder_files_count,
                'total_size': folder_size
            }

    return stats

def format_stats_table(stats, project_path, tree_lines):
    """Форматирует статистику в виде читаемых таблиц."""
    lines = []
    lines.append("=" * 80)
    lines.append("ДЕТАЛЬНАЯ СТАТИСТИКА ПРОЕКТА")
    lines.append("=" * 80)
    lines.append(f"Проект: {project_path.name}")
    lines.append(f"Путь: {project_path.absolute()}")
    lines.append(f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Общий размер: {humanize.naturalsize(stats['total_size'])}")
    lines.append(f"Всего файлов: {stats['total_files']}")
    lines.append(f"Всего папок: {stats['total_folders']}")
    lines.append("")

    # Добавляем древовидную структуру
    lines.extend(tree_lines)

    # Статистика по расширениям файлов
    if stats['files_by_extension']:
        lines.append("📊 РАСПРЕДЕЛЕНИЕ ПО РАСШИРЕНИЯМ:")
        lines.append("-" * 40)
        for ext, count in sorted(stats['files_by_extension'].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"{ext:8} : {count:4d} файлов")
        lines.append("")

    # Крупнейшие файлы
    if stats['largest_file']['path']:
        lines.append("🏆 САМЫЕ БОЛЬШИЕ ФАЙЛЫ:")
        lines.append("-" * 40)
        lines.append(f"Крупнейший: {stats['largest_file']['path']} ({humanize.naturalsize(stats['largest_file']['size'])})")
        lines.append("")

    # Временные метки
    if stats['oldest_file']['path']:
        lines.append("🕐 ВРЕМЕННЫЕ МЕТКИ:")
        lines.append("-" * 40)
        oldest_time = datetime.fromtimestamp(stats['oldest_file']['mtime'])
        newest_time = datetime.fromtimestamp(stats['newest_file']['mtime'])
        lines.append(f"Самый старый: {stats['oldest_file']['path']} ({oldest_time.strftime('%Y-%m-%d')})")
        lines.append(f"Самый новый:  {stats['newest_file']['path']} ({newest_time.strftime('%Y-%m-%d')})")
        lines.append("")

    # Статистика по папкам (только папки с файлами)
    if stats['files_by_folder']:
        lines.append("📂 СТАТИСТИКА ПО ПАПКАМ:")
        lines.append("-" * 40)
        sorted_folders = sorted(stats['files_by_folder'].items(),
                               key=lambda x: x[1]['file_count'], reverse=True)

        for folder, data in sorted_folders:
            if data['file_count'] > 0:
                size_str = humanize.naturalsize(data['total_size'])
                lines.append(f"{folder:<30} : {data['file_count']:3d} файлов, {size_str:>10}")
        lines.append("")

    lines.append("=" * 80)
    lines.append("")
    return "\n".join(lines)

def create_project_overview(project_path, output_file=None, included_extensions=None):
    """Создает общий текстовый файл со всем кодом проекта для загрузки в ИИ-ассистенты."""
    if included_extensions is None:
        included_extensions = DEFAULT_EXTENSIONS
        
    if output_file is None:
        output_file = get_output_filename()

    project_path = Path(project_path)
    output_file = Path(output_file)

    # Проверяем существование пути проекта
    if not project_path.exists():
        print(f"❌ Ошибка: Папка '{project_path}' не существует!")
        return False
    if not project_path.is_dir():
        print(f"❌ Ошибка: '{project_path}' не является папкой!")
        return False

    # Генерируем древовидную структуру
    print("🌳 Генерация древовидной структуры...")
    tree_lines, tree_file_count = get_directory_tree(project_path, included_extensions)

    # Выводим структуру в консоль
    print("\n".join(tree_lines))
    print(f"📊 Найдено файлов в структуре: {tree_file_count}")
    print("-" * 50)

    # Собираем статистику
    print("📊 Сбор детальной статистики...")
    stats = calculate_project_stats(project_path, included_extensions)

    separator = "\n" + "=" * 80 + "\n"
    file_separator = "\n" + "-" * 60 + "\n"

    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # Записываем детальную статистику
            stats_text = format_stats_table(stats, project_path, tree_lines)
            outfile.write(stats_text)

            # Записываем заголовок
            outfile.write("СОДЕРЖИМОЕ ФАЙЛОВ ПРОЕКТА")
            outfile.write(separator)

            # Рекурсивно обходим все файлы в директории
            files_processed = 0
            for file_path in project_path.rglob('*'):
                if (file_path.is_file() and 
                    should_include_file(file_path, included_extensions)):

                    # Записываем заголовок файла
                    relative_path = file_path.relative_to(project_path)
                    file_info = get_file_info(file_path)
                    
                    outfile.write(f"ФАЙЛ: {relative_path}\n")
                    if file_info:
                        outfile.write(f"Размер: {file_info['size_str']}\n")
                        outfile.write(f"Изменен: {file_info['mtime_str']}\n")
                    else:
                        outfile.write("Размер: N/A\n")
                        outfile.write("Изменен: N/A\n")
                    outfile.write(file_separator)

                    # Читаем и записываем содержимое
                    content = read_file_content(file_path)
                    outfile.write(content)

                    outfile.write(separator)
                    files_processed += 1

            # Финальная статистика
            outfile.write(f"АНАЛИЗ ЗАВЕРШЕН.\n")
            outfile.write(f"Обработано файлов: {files_processed}\n")
            outfile.write(f"Общий размер: {humanize.naturalsize(stats['total_size'])}\n")
            outfile.write(f"Время создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print(f"✅ Обзор проекта создан: {output_file.absolute()}")
        print(f"📦 Размер итогового файла: {humanize.naturalsize(output_file.stat().st_size)}")
        print(f"📄 Обработано файлов: {files_processed}")
        return True

    except Exception as e:
        print(f"❌ Ошибка при создании файла: {e}")
        return False

def main():
    """Основная функция с обработкой запуска без параметров."""
    try:
        import humanize
    except ImportError:
        print("❌ Требуется установка пакета 'humanize'")
        print("   Установите: pip install humanize")
        return

    parser = argparse.ArgumentParser(
        description='Создание обзора проекта для ИИ-анализа',
        epilog='Примеры использования:\n'
               '  python project_analyzer.py                 # Анализ текущей папки\n'
               '  python project_analyzer.py /путь/к/проекту # Анализ указанной папки\n'
               '  python project_analyzer.py -e .py .json .txt -o отчет.txt',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('project_path', nargs='?', default='.',
                       help='Путь к папке проекта (по умолчанию: текущая папка)')
    parser.add_argument('-o', '--output', 
                       help='Имя выходного файла (по умолчанию: сгенерируется автоматически с временной меткой)')
    parser.add_argument('-e', '--extensions', nargs='+', default=DEFAULT_EXTENSIONS,
                       help='Расширения файлов для включения (по умолчанию: .py .md .txt)')

    args = parser.parse_args()

    # Генерируем имя файла, если не указано
    if args.output is None:
        args.output = get_output_filename()

    # Обрабатываем случай, когда путь не указан (используем текущую папку)
    project_path = Path(args.project_path).absolute()

    print("🚀 Запуск анализатора проекта...")
    print(f"📁 Папка проекта: {project_path}")
    print(f"📄 Выходной файл: {args.output}")
    print(f"🔍 Расширения: {', '.join(args.extensions)}")
    print("-" * 50)

    success = create_project_overview(
        project_path=project_path,
        output_file=args.output,
        included_extensions=args.extensions
    )

    if success:
        print("✅ Готово! Файл можно загружать в ИИ-ассистент.")
    else:
        print("❌ Завершено с ошибками.")

if __name__ == "__main__":
    main()