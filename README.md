# CRM API

API для управления отношениями с клиентами, разработанный на FastAPI

## Установка

### Требования

- Python 3.13+
- PostgreSQL 14+
- Docker (опционально)

### Инструкции по установке

1. Клонируйте репозиторий
2. Создайте виртуальное окружение:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Настройте переменные окружения:
   ```bash
   cp .env.example .env
   ```

5. Запустите PostgreSQL через Docker Compose:
   ```bash
   docker-compose up -d
   ```

6. Примените миграции:
   ```bash
   alembic upgrade head
   ```

7. Запустите API сервер:
   ```bash
   python main.py
   ```

## Документация API

После запуска сервера перейдите по ссылкам:
- Интерактивная документация: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Структура проекта

```
crm/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/
│   │   └── schemas/
│   ├── core/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── config.py
│   ├── database.py
│   └── main.py
├── alembic/
├── tests/
└── requirements.txt
```

## Разработка

### Запуск тестов:
```bash
pytest
```

Для более подробной информации о тестировании см. [tests/README.md](tests/README.md)

Доступные опции:
```bash
pytest tests/unit/                   # Только unit тесты
pytest tests/integration/            # Только интеграционные тесты
pytest -v                            # С подробным выводом
pytest --cov=app                     # С покрытием кода
pytest tests/integration/test_full_scenario.py  # Сквозной тест
```

### Проверка типов:
```bash
mypy app
```

### Форматирование кода:
```bash
ruff check app --fix
```

## Архитектура

Проект следует многослойной архитектуре:

- **Модели (models/)** - ORM модели SQLAlchemy для работы с базой данных
- **Репозитории (repositories/)** - Слой доступа к данным с CRUD операциями
- **Сервисы (services/)** - Бизнес-логика и валидация
- **Schemas (schemas/)** - Pydantic схемы для валидации запросов/ответов
- **Endpoints (endpoints/)** - FastAPI маршруты

## Основные возможности

- Управление организациями и пользователями
- CRUD операции для контактов, сделок, задач и активностей
- JWT аутентификация с ролями
- Контроль доступа на основе ролей (RBAC)
- Аналитика и статистика
- Асинхронная работа с базой данных

## API Endpoints

### Аутентификация (`/api/v1/auth`)
- `POST /auth/register` - Регистрация нового пользователя
- `POST /auth/login` - Вход в систему
- `POST /auth/refresh` - Обновление токена доступа
- `GET /auth/me` - Получить информацию о текущем пользователе
- `POST /auth/change-password` - Изменить пароль

### Организации (`/api/v1/organizations`)
- `GET /organizations/me` - Получить организацию текущего пользователя

### Контакты (`/api/v1/contacts`)
- `GET /contacts` - Список контактов (с поиском и пагинацией)
- `POST /contacts` - Создать контакт
- `GET /contacts/{id}` - Получить контакт
- `PATCH /contacts/{id}` - Обновить контакт
- `DELETE /contacts/{id}` - Удалить контакт

### Сделки (`/api/v1/deals`)
- `GET /deals` - Список сделок (с фильтрацией по статусу и поиском)
- `POST /deals` - Создать сделку
- `GET /deals/{id}` - Получить сделку
- `PATCH /deals/{id}` - Обновить сделку
- `POST /deals/{id}/status` - Изменить статус сделки
- `DELETE /deals/{id}` - Удалить сделку

### Задачи (`/api/v1/tasks`)
- `GET /tasks` - Список задач (с фильтрацией)
- `POST /tasks` - Создать задачу
- `GET /tasks/{id}` - Получить задачу
- `PATCH /tasks/{id}` - Обновить задачу
- `POST /tasks/{id}/complete` - Отметить задачу выполненной
- `DELETE /tasks/{id}` - Удалить задачу

### Активности (`/api/v1/activities`)
- `GET /deals/{deal_id}/activities` - Список активностей сделки
- `POST /deals/{deal_id}/activities` - Создать активность для сделки
- `GET /contacts/{contact_id}/activities` - Список активностей контакта
- `POST /contacts/{contact_id}/activities` - Создать активность для контакта

### Аналитика (`/api/v1/analytics`)
- `GET /analytics/deals/summary` - Сводка по сделкам
- `GET /analytics/tasks/summary` - Сводка по задачам
- `GET /analytics/contacts/statistics` - Статистика контактов
- `GET /analytics/activities/statistics` - Статистика активностей
- `GET /analytics/dashboard` - Полная сводка дашборда

## Аутентификация

Все запросы (кроме аутентификации) требуют:
1. Заголовок `Authorization: Bearer {token}` с JWT токеном
2. Заголовок `X-Organization-Id: {uuid}` с ID организации

## Примеры API запросов

### 1. Регистрация пользователя

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword123"
  }'
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Вход в систему

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 3. Получение информации о текущем пользователе

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 4. Создание контакта

```bash
curl -X POST http://localhost:8000/api/v1/contacts \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "X-Organization-Id: {ORG_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Smith",
    "email": "john.smith@company.com",
    "phone": "+1234567890",
    "company": "ACME Corp",
    "position": "Manager"
  }'
```

### 5. Получение списка контактов

```bash
curl http://localhost:8000/api/v1/contacts?skip=0&limit=10 \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "X-Organization-Id: {ORG_ID}"
```

### 6. Создание сделки

```bash
curl -X POST http://localhost:8000/api/v1/deals \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "X-Organization-Id: {ORG_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Enterprise Contract",
    "amount": 100000.00,
    "description": "Large enterprise deal"
  }'
```

### 7. Изменение статуса сделки

```bash
curl -X POST http://localhost:8000/api/v1/deals/{DEAL_ID}/status \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "X-Organization-Id: {ORG_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

### 8. Создание задачи

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "X-Organization-Id: {ORG_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "assigned_to": "550e8400-e29b-41d4-a716-446655440111",
    "title": "Prepare proposal",
    "priority": "high",
    "deal_id": "550e8400-e29b-41d4-a716-446655440222"
  }'
```

### 9. Логирование активности

```bash
curl -X POST http://localhost:8000/api/v1/activities/deals/{DEAL_ID} \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "X-Organization-Id: {ORG_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "activity_type": "call",
    "title": "Client call",
    "description": "Discussed project requirements"
  }'
```

### 10. Получение аналитики

```bash
curl http://localhost:8000/api/v1/analytics/dashboard \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "X-Organization-Id: {ORG_ID}"
```

**Ответ:**
```json
{
  "deals": {
    "total_deals": 5,
    "new": 2,
    "in_progress": 2,
    "won": 1,
    "lost": 0,
    "win_rate": 20.0,
    "pipeline_amount": 150000.00,
    "won_amount": 100000.00
  },
  "tasks": {
    "total_tasks": 10,
    "todo": 4,
    "in_progress": 3,
    "done": 3,
    "overdue": 0,
    "completion_rate": 30.0
  },
  "contacts": {
    "total_contacts": 5
  },
  "activities": {
    "total_activities": 12,
    "calls": 5,
    "emails": 3,
    "meetings": 2,
    "notes": 2
  }
}
```

## Роли и права доступа

### Доступные роли:

| Роль | READ | CREATE | UPDATE | DELETE |
|------|------|--------|--------|--------|
| OWNER | ✓ | ✓ | ✓ | ✓ |
| ADMIN | ✓ | ✓ | ✓ | ✓ |
| MANAGER | ✓ | ✓ | ✓ | ✗ |
| SALES | ✓ | ✓ | ✓* | ✗ |
| VIEWER | ✓ | ✗ | ✗ | ✗ |

*SALES может изменять только свои собственные задачи

## Статусы и переходы

### Статусы сделок:
- `new` - Новая сделка
- `in_progress` - В работе
- `won` - Выиграна
- `lost` - Потеряна
- `closed` - Закрыта

**Валидные переходы:**
- NEW → IN_PROGRESS, LOST
- IN_PROGRESS → WON, LOST
- WON, LOST, CLOSED → не могут переходить

### Статусы задач:
- `todo` - К выполнению
- `in_progress` - В процессе
- `done` - Завершена
- `cancelled` - Отменена

## Ошибки и коды ответов

| Код | Описание |
|-----|----------|
| 200 | OK - Успешный запрос |
| 201 | Created - Ресурс создан |
| 204 | No Content - Успешное удаление |
| 400 | Bad Request - Неверные параметры |
| 401 | Unauthorized - Требуется аутентификация |
| 403 | Forbidden - Нет прав доступа |
| 404 | Not Found - Ресурс не найден |
| 409 | Conflict - Конфликт (дублирование) |
| 500 | Internal Server Error - Ошибка сервера |
