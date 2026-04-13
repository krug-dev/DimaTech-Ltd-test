# Payment API

Асинхронное REST API для работы с пользователями, счетами и платежами.

## Технологии

- FastAPI
- PostgreSQL
- SQLAlchemy (async)
- Alembic (миграции)
- Docker Compose

## Запуск с Docker Compose

```bash
# Сборка и запуск всех сервисов
docker-compose up --build

# Приложение будет доступно на http://localhost:8000
# Swagger docs: http://localhost:8000/docs
```

## Запуск без Docker

### Требования

- Python 3.11+
- PostgreSQL 15+

### Установка

```bash
# Перейдите в папку проекта
cd C:\Users\User\Desktop\testPython

# Создайте виртуальное окружение
python -m venv venv

# Активируйте виртуальное окружение
.\venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt

# Создайте БД в PostgreSQL
psql -U postgres -c "CREATE DATABASE testdb;"

# Примените миграции (таблицы создаются автоматически)
alembic upgrade head

# Или создайте таблицы вручную через Python
python -c "from app.main import app; from app.database import engine, Base; import asyncio; asyncio.run(Base.metadata.create_all(engine))"

# Запустите скрипт для создания тестовых данных
python seed_data.py

# Запуск приложения
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Тестовые данные

### Пользователь
- **Email:** user@test.com
- **Password:** user123

### Администратор
- **Email:** admin@test.com
- **Password:** admin123

## API Endpoints

### Аутентификация
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/token` | Получить токен (form-data: grant_type=password, username=email, password=password) |

### Пользователь (требуется токен пользователя)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/me` | Данные текущего пользователя |
| GET | `/api/accounts` | Список счетов пользователя |
| GET | `/api/payments` | Список платежей пользователя |

### Администратор (требуется токен админа)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/admin/me` | Данные администратора |
| POST | `/api/admin/users` | Создать пользователя |
| PUT | `/api/admin/users/{id}` | Обновить пользователя |
| DELETE | `/api/admin/users/{id}` | Удалить пользователя |
| GET | `/api/admin/users` | Список всех пользователей со счетами |

### Вебхук
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/webhook/payment` | Обработка платежа |
| GET | `/api/webhook/payment/{transaction_id}` | Получить информацию о платеже (админ) |

## Пример webhook запроса

```json
{
  "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
  "user_id": 1,
  "account_id": 1,
  "amount": 100,
  "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
}
```

### Формирование подписи

Подпись вычисляется как SHA256 от строки:
```
{account_id}{amount}{transaction_id}{user_id}{secret_key}
```

Где secret_key = `gfdmhghif38yrf9ew0jkf32`

Пример для данных выше:
```
data_string = "1" + "100" + "5eae174f-7cd0-472c-bd36-35660f00132b" + "1" + "gfdmhghif38yrf9ew0jkf32"
signature = sha256(data_string.encode()).hexdigest()
```

## Переменные окружения

| Переменная | Значение по умолчанию | Описание |
|------------|----------------------|----------|
| DATABASE_URL | postgresql+asyncpg://postgres:postgres@localhost:5432/testdb | URL для подключения к БД |
| SECRET_KEY | gfdmhghif38yrf9ew0jkf32 | Секретный ключ для JWT и подписи |
