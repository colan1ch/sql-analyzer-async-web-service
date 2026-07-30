# Асинхронный сервис SQL Analyzer

## Краткое описание

Отдельный асинхронный сервис учебной системы SQL Analyzer для курса «Разработка интернет-приложений». Сервис принимает заявку на расчёт, выполняет вычисление в фоновом потоке с задержкой и отправляет результат обратно в основной Go-сервис по HTTP.

## Основные возможности

- приём задания на расчёт времени выполнения SQL-запроса;
- фоновое выполнение задачи через `ThreadPoolExecutor`;
- задержка выполнения от 5 до 10 секунд;
- расчёт времени выполнения и количества полученных строк по данным индексов;
- отправка результатов в основной сервис через callback;
- endpoint проверки состояния сервиса.

## Лабораторные работы и ветки

- [Лабораторная работа № 8 — межсервисное взаимодействие и асинхронность](https://github.com/colan1ch/sql-analyzer-async-web-service/tree/async_web_service)

В `main` объединена финальная версия ветки `async_web_service`.

## Стек технологий

- Python;
- Django `4.2.7`;
- Django REST Framework `3.14.0`;
- Requests `2.31.0`;
- python-dotenv `1.0.0`;
- SQLite используется в конфигурации Django;
- `ThreadPoolExecutor` для фонового выполнения задач.

## Установка и запуск

Требуется Python с `pip`.

```bash
cd async_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver 8000
```

В Windows для активации окружения используется команда `.venv\\Scripts\\activate`. Переменные `MAIN_SERVICE_URL` и `ASYNC_SERVICE_SECRET_KEY` определены в настройках Django; callback в текущей реализации использует адрес и ключ, заданные константами в [`async_service/calculator/views.py`](async_service/calculator/views.py).

## API

Запуск расчёта:

```http
POST http://127.0.0.1:8000/api/calculate-query-execution-time/
Content-Type: application/json

{
  "query_id": 1,
  "indexes_data": [
    {
      "index_id": 1,
      "cardinality": 100,
      "rows_count": 500,
      "date_query": "2024-12-15",
      "received_rows_id": 1
    }
  ]
}
```

Метод возвращает `202 Accepted`, после чего задача выполняется асинхронно. Проверка состояния:

```http
GET http://127.0.0.1:8000/api/health/
```

Маршруты определены в [`async_service/calculator/urls.py`](async_service/calculator/urls.py), обработчики — в [`async_service/calculator/views.py`](async_service/calculator/views.py), формулы — в [`async_service/calculator/calculations.py`](async_service/calculator/calculations.py).

## Структура проекта

```text
async_service/
├── manage.py
├── async_service/         настройки и URL-маршрутизация Django
└── calculator/            API расчёта и фоновые задачи
    ├── calculations.py    вычисления
    ├── urls.py            маршруты `/api/`
    └── views.py           HTTP-обработчики и callback
requirements.txt           зависимости Python
```

## Статус проекта

Учебный асинхронный сервис лабораторной работы № 8 курса «Разработка интернет-приложений». Реализация объединена в `main`; сервис рассчитан на совместную работу с основным Go-веб-сервисом.

## Связанные репозитории

- [Фронтенд](https://github.com/colan1ch/sql-analyzer)
- [Основной веб-сервис](https://github.com/colan1ch/sql-analyzer-web-service)

## Описание для GitHub

Асинхронный сервис расчёта результатов для SQL Analyzer. Стек: Python, Django, Django REST Framework, Requests и ThreadPoolExecutor. Принимает задания, выполняет расчёты с задержкой и передаёт результаты основному Go-веб-сервису.
