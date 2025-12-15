# Django Async Service

Асинхронный сервис на Django для обработки расчетов ExecutionTime и ReceivedRows.

## Установка

```bash
cd async_service
python -m venv venv
source venv/bin/activate  # macOS/Linux
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
python manage.py migrate
```

## Запуск сервиса

```bash
python manage.py runserver 8001
```

Сервис будет доступен на `http://localhost:8001`

## API Endpoints

### POST /api/calculate/

Запускает асинхронный расчет.

**Request:**
```json
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

**Response (202 Accepted):**
```json
{
  "status": "processing",
  "query_id": 1,
  "message": "Calculation started asynchronously. Results will be sent to main service.",
  "estimated_time": "5-10 seconds"
}
```

### GET /api/health/

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "async-calculator"
}
```

## Переменные окружения

Создайте файл `.env` в папке `async_service`:

```env
MAIN_SERVICE_URL=http://localhost:8080
ASYNC_SERVICE_SECRET_KEY=secret_key_8byte
DEBUG=True
```

## Процесс работы

1. Go сервис отправляет POST запрос на `/api/calculate/` с данными заявки и индексов
2. Django сервис принимает запрос и возвращает 202 (Accepted)
3. В фоновом потоке выполняется:
   - Задержка 5-10 секунд (имитация расчетов)
   - Расчет `execution_time` по формуле: `sum(log2(cardinality)) + product(rows_count / cardinality)`
   - Расчет `received_rows` для каждого индекса: `rows_count - cardinality`
4. Результаты отправляются обратно на Go сервис POST запросом на `/api/queries/{query_id}/results`
5. Go сервис обновляет поля в БД

## Формулы расчета

### ExecutionTime
```
execution_time = sum(log2(cardinality_i)) + product(rows_count_i / cardinality_i)
```

### ReceivedRows (для каждого индекса)
```
received_rows = max(0, rows_count - cardinality)
```

## Авторизация

Все запросы между сервисами используют простой механизм авторизации через Bearer токен:
- Header: `Authorization: Bearer secret_key_8byte`
- Проверка происходит через сравнение константы

## Интеграция с Go сервисом

Go сервис должен иметь endpoints:

1. **POST /api/queries/{query_id}/results** - принимает результаты расчетов
2. **POST /api/queries/{query_id}/error** - уведомление об ошибке

При формировании заявки (статус "formed") Go сервис отправляет запрос на `/api/calculate/` Django сервиса.
