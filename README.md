
# TableBot-Pipe Advanced 🚀

> **TableBot-Pipe Advanced** — это эволюция [TableBot-Pipe](https://github.com/...), расширенная архитектура для создания сложных Telegram-ботов на основе CSV/XLSX таблиц.

Этот проект позволяет **описать всю бизнес-логику бота в таблице**, а Python-код отвечает **только за оркестрацию** и **техническую реализацию**. В отличие от оригинального `tablebot-pipe`, **Advanced** включает в себя возможности для **многопользовательских сценариев**, **отслеживания прогресса** и **взаимодействия между сессиями**.

## 🌟 Особенности

*   **Всё в таблице:** Состояния, переходы, сообщения, кнопки, условия, эффекты, прогресс — всё описывается в `table_final.csv` (или XLSX).
*   **Микросервисная архитектура:** Обработка сообщений разделена на независимые функции (find_row, check_guard, execute_effect, build_message, и т.д.).
*   **Многопользовательские сессии:** Поддержка взаимодействия между несколькими акторами (например, Клиент, Водитель, Оператор).
*   **Уведомления между сессиями:** Возможность отправлять сообщения из одной сессии в другую (через `result_action: notify_user_by_chat_id:<target_chat_id>:<message_template>`).
*   **Отображение прогресса:** Поддержка строк прогресса и визуальных прогресс-баров, настраиваемых через колонку `progress_config` в таблице.
*   **Динамическое FSM:** Состояния и переходы создаются автоматически на основе таблицы.
*   **Командное меню:** Команды для меню бота автоматически генерируются из колонок `bot_command` и `bot_description` в таблице.
*   **Интеграции:** Возможность вызова внешних HTTP-сервисов и других интеграций.
*   **Модульность:** Код легко расширяется, добавляя новые микросервисы или функции отправки сообщений.
*   **Поддержка XLSX:** Работа как с CSV, так и с Excel-файлами (XLSX).

## 🏗️ Архитектура

```text
Пользователь -> Telegram -> 08_core_loop.py -> pipeline/ -> Ответ пользователю
                                    ↓
                              table_final.csv
```

*   **`08_core_loop.py`**: Основной цикл бота, обработчики сообщений и callback'ов.
*   **`pipeline/`**: Набор независимых Python-модулей, выполняющих конкретные задачи пайплайна.
*   **`table_final.csv`**: Центральный файл с описанием логики бота.
*   **`core/`**: Ядро системы (загрузка токена, таблицы, FSM, отправка сообщений).
*   **`handlers/`**: Обработчики входящих событий (сообщения, кнопки).

## 🚀 Запуск

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/your-username/tablebot-pipe-advanced.git
    cd tablebot-pipe-advanced
    ```

2.  **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Убедитесь, что `requirements.txt` включает `aiogram`, `pandas`, `openpyxl` для поддержки XLSX)*

3.  **Настройте токен бота:**
    *   Создайте файл `.env` или `token.env` в корне проекта.
    *   Добавьте строку: `BOT_TOKEN=ваш_токкен_от_botfather`

4.  **Настройте таблицу:**
    *   Отредактируйте `table_final.csv` (или `table.xlsx`) в соответствии с вашей логикой.
    *   Обратите внимание на колонки `bot_command`, `bot_description` и `progress_config`.

5.  **Запустите бота:**
    ```bash
    python 08_core_loop.py table_final.csv
    # или
    python 08_core_loop.py table.xlsx
    ```

## 📊 Формат таблицы

Формат таблицы `table_final.csv` (или `table.xlsx`) определяет всю логику бота. Каждая строка описывает *переход* из одного состояния в другое при определённом *вводе*.

### Основные колонки

| Колонка | Описание | Пример |
| :--- | :--- | :--- |
| `process_name` | Имя процесса (может использоваться для логики или фильтрации, часто просто константа) | `TestBot`, `PizzaOrder` |
| `from_state` | Исходное состояние пользователя | `start`, `menu`, `step1` |
| `to_state` | Целевое состояние, в которое перейдёт пользователь | `menu`, `step1`, `step2` |
| `command` | Команда или текст, который должен ввести пользователь для перехода | `/start`, `Далее`, `<text>` (любой текст) |
| `condition` | Условие, которое должно быть выполнено для перехода (опционально) | `not_empty:text`, `equals:user_type:admin` |

### Колонки для отправки сообщений

| Колонка | Описание | Пример |
| :--- | :--- | :--- |
| `message_text` | Основной текст сообщения, которое отправит бот | `Добро пожаловать!`, `Шаг 1 из 3` |
| `caption` | Подпись к медиафайлу (если `media_file` указан) | `Наше меню` |
| `media_file` | Путь или URL к медиафайлу (фото, видео, документ и т.д.) | `menu.jpg`, `https://example.com/video.mp4` |

### Колонки для интерактивных элементов

| Колонка | Описание | Пример |
| :--- | :--- | :--- |
| `reply_markup` | Обычные (reply) кнопки, разделённые `\|` | `Да\|Нет\|Отмена` |
| `inline_markup` | Inline-кнопки, формат: `Текст:callback_data\|Текст2:callback_data2` | `Подтвердить:confirm\|Отмена:cancel` |

### Колонки для дополнительной логики

| Колонка | Описание | Пример |
| :--- | :--- | :--- |
| `notification` | Текст уведомления (может использоваться отдельно от `message_text`) | `Заказ принят: {order_id}` |
| `integrations` | Описание внешнего вызова (HTTP, email и т.д.) | `http:POST https://api.com/order` |
| `result_action` | Side-effect действия (сохранение данных, очистка, отправка в другой чат) | `save:order_id:123`, `clear:temp_data`, `notify_user_by_chat_id:123456789:Привет!` |

### Колонки для командного меню и прогресса

| Колонка | Описание | Пример |
| :--- | :--- | :--- |
| `bot_command` | Команда для отображения в меню бота (должна начинаться с `/`) | `/start`, `/help` |
| `bot_description` | Описание команды для меню бота | `Запустить бота`, `Получить помощь` |
| `progress_config` | Конфигурация отображения прогресса (описание см. ниже) | `manual:1/3`, `track:step_field`, `bar:step_field` |

---

### Подробное описание `progress_config`

Колонка `progress_config` позволяет настраивать отображение прогресса *внутри* `message_text`. Поддерживаемые форматы:

*   `disabled`: Прогресс не отображается для этой строки.
*   `manual:current_step/total_steps`: Отображает текст вида `[Шаг current_step/total_steps]`.
*   `track:field_name`: Отображает текст вида `[Прогресс: значение_из_payload[field_name]]`.
*   `bar:field_name`: Отображает визуальный прогресс-бар (например, `████░░░░`), используя значение из `payload[field_name]` и, при необходимости, `payload.get("total_steps_for_bar", 8)`.
*   `track:field_name\|bar:field_name`: Комбинация текстового прогресса и бара.

---

### Подробное описание `result_action`

Колонка `result_action` позволяет выполнять побочные действия при переходе. Поддерживаемые форматы:

*   `save:field:value`: Сохраняет `value` в `payload[field]`. `value` может содержать плейсхолдеры `{other_field}`, которые будут подставлены из `payload`.
*   `clear:field`: Удаляет `field` из `payload`.
*   `notify_user_by_chat_id:target_chat_id:message_template`: (Расширение Advanced) Отправляет сообщение `message_template` в чат с ID `target_chat_id`. `message_template` может содержать плейсхолдеры `{field}`, которые будут подставлены из `payload` текущей сессии.

---

### Пример строки таблицы

| process_name | from_state | to_state | command | condition | message_text | result_action | progress_config | bot_command | bot_description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| TestBot | start | menu | /start | | Добро пожаловать! Выберите действие. | save:current_step:1\|save:user_id:{chat_id} | manual:1/3 | /start | Запустить бота |
| TestBot | menu | step1 | Начать | | Шаг 1. Пожалуйста, введите что-нибудь. | save:current_step:2 | track:current_step\|bar:current_step | | |
| TestBot | step1 | step2 | `<text>` | | Вы ввели: <b>{text}</b>. Переход к шагу 2. | save:current_step:3\|notify_user_by_chat_id:123456789:Клиент {user_id} ввёл {text} на шаге 1! | track:current_step\|bar:current_step | | |

## 🧩 Расширение

*   **Новые типы сообщений:** Добавьте функции в `core/message_sender/`.
*   **Новые эффекты:** Добавьте логику в `pipeline/execute_effect.py`.
*   **Новые интеграции:** Добавьте парсер в `pipeline/prepare_integration.py`.
*   **Новые условия (guards):** Добавьте логику в `pipeline/check_guard.py`.

## 📁 Структура проекта (итоговый листинг)

```
├── 08_core_loop.py
├── create_test_media.py
├── project_analyzer4.py
├── table.csv
├── table_final.csv
├── table_final_back.csv
├── table_fixed.csv
├── table_pizza.csv
├── table_urls.csv
├── арх.txt
├── .env (или token.env - примерный файл)
├── requirements.txt (примерный файл)
├── core/
│   ├── commands_loader.py
│   ├── fsm_builder.py
│   ├── message_sender_back.py
│   ├── pipeline_executor.py
│   ├── table_loader.py
│   ├── token_loader.py
│   └── message_sender/
│       ├── __init__.py
│       ├── base.py
│       ├── format_detector.py
│       ├── markup_builder.py
│       ├── media_sender.py
│       ├── poll_sender.py
│       └── text_sender.py
├── doc/
│   ├── deepseek_text_20250929_e42670.txt
│   └── Новый текстовый документ.txt
├── handlers/
│   ├── callback_handler.py
│   └── message_handler.py
└── pipeline/
    ├── __init__.py
    ├── build_message.py
    ├── check_guard.py
    ├── determine_transition.py
    ├── execute_effect.py
    ├── find_row.py
    ├── format_notification.py
    └── prepare_integration.py
```

*(Примечание: Структура взята из `project_overview.txt`. Файлы `.env`, `requirements.txt` добавлены как ожидаемые.)*

## 📄 Лицензия

MIT
```

---

Этот `README.md` теперь включает:

1.  **Описание проекта и его особенностей.**
2.  **Архитектуру.**
3.  **Инструкции по запуску.**
4.  **Полное развёрнутое описание таблицы и всех её столбцов**, включая `progress_config` и `result_action` с новыми возможностями.
5.  **Раздел "Расширение".**
6.  **Итоговый листинг файлов проекта**, как того требовалось, на основе `project_overview.txt`.
7.  **Лицензию.**