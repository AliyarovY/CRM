# Развертывание CRM API

## Локальная разработка

### Требования
- Python 3.13+
- PostgreSQL 14+ (или Docker)
- Docker и Docker Compose

### Быстрый старт с Docker Compose

```bash
# Клонируйте репозиторий
git clone <repository>
cd CRM

# Запустите все сервисы
docker-compose up -d

# Примените миграции (в контейнере API)
docker-compose exec api alembic upgrade head

# API будет доступен на http://localhost:8000
# Интерактивная документация: http://localhost:8000/docs
# pgAdmin: http://localhost:5050
```

### Локальная разработка без Docker

```bash
# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Настройте переменные окружения
cp .env.example .env

# Запустите PostgreSQL локально или в Docker
docker run -d \
  --name postgres \
  -e POSTGRES_USER=crm_user \
  -e POSTGRES_PASSWORD=crm_password \
  -e POSTGRES_DB=crm_db \
  -p 5432:5432 \
  postgres:16-alpine

# Примените миграции
alembic upgrade head

# Запустите сервер
python main.py
```

## Конфигурация

### Переменные окружения

Переменные в `.env` файле (обязательные):

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/crm_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### Docker Compose переменные

Все переменные установлены в `docker-compose.yml` для разработки:
- PostgreSQL: `crm_user` / `crm_password` / `crm_db`
- API: `SECRET_KEY=dev-secret-key` (ИЗМЕНИТЕ В PRODUCTION!)
- pgAdmin: `admin@example.com` / `admin`

## Production развертывание

### Рекомендуемая архитектура

```
┌─────────────────┐
│   Nginx (Proxy) │
└────────┬────────┘
         │
    ┌────┴────┐
    │          │
┌──────┐  ┌──────┐
│ API1 │  │ API2 │  (load balancing)
└──┬───┘  └──┬───┘
   │        │
   └────┬───┘
        │
   ┌────────────┐
   │ PostgreSQL │
   └────────────┘
```

### Требования для Production

1. **Безопасность**
   - Используйте надежный SECRET_KEY
   - Включите HTTPS/TLS
   - Используйте переменные окружения для всех секретов
   - Отключите debug режим

2. **База данных**
   - Используйте управляемый PostgreSQL сервис (AWS RDS, Google Cloud SQL и т.д.)
   - Регулярно делайте резервные копии
   - Используйте сильный пароль

3. **Мониторинг**
   - Настройте логирование
   - Мониторьте healthcheck endpoints
   - Используйте APM инструменты

4. **Масштабируемость**
   - Используйте load balancer
   - Запускайте несколько инстансов API
   - Кэшируйте часто используемые данные

### Docker для Production

Production Dockerfile:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN alembic upgrade head

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Запуск:

```bash
docker build -t crm-api:latest .

docker run -d \
  --name crm-api \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e SECRET_KEY=production-secret-key \
  --health-cmd='curl -f http://localhost:8000/health' \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  crm-api:latest
```

### Kubernetes развертывание

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crm-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: crm-api
  template:
    metadata:
      labels:
        app: crm-api
    spec:
      containers:
      - name: crm-api
        image: crm-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: crm-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: crm-secrets
              key: secret-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Миграции в Production

```bash
# Перед развертыванием новой версии
docker run --rm \
  -e DATABASE_URL=postgresql://... \
  crm-api:latest \
  alembic upgrade head

# Откатить последнюю миграцию
docker run --rm \
  -e DATABASE_URL=postgresql://... \
  crm-api:latest \
  alembic downgrade -1
```

## Мониторинг и Логирование

### Healthcheck endpoints

- `GET /health` - Статус здоровья сервиса
- `GET /ready` - Готовность к обработке запросов

### Логирование

Логи доступны в:
- Stdout контейнера (Docker)
- Файлы логов (если настроены)
- Системы мониторинга (DataDog, New Relic и т.д.)

### Метрики для мониторинга

- Время отклика API
- Количество ошибок
- Использование БД
- Активные подключения

## Резервные копии и восстановление

### PostgreSQL резервные копии

```bash
# Создать резервную копию
docker-compose exec postgres pg_dump -U crm_user crm_db > backup.sql

# Восстановить из резервной копии
docker-compose exec -T postgres psql -U crm_user crm_db < backup.sql
```

## Обновление версии

```bash
# Остановить текущую версию
docker-compose down

# Обновить код
git pull origin main

# Собрать новый образ
docker-compose build

# Применить миграции
docker-compose up -d postgres
docker-compose run --rm api alembic upgrade head

# Запустить новую версию
docker-compose up -d
```

## Troubleshooting

### API не стартует

```bash
# Проверьте логи
docker-compose logs api

# Проверьте подключение к БД
docker-compose exec api python -c "from app.database import engine; print('DB OK')"
```

### Миграции не применяются

```bash
# Проверьте статус миграций
docker-compose exec api alembic current

# Откатите и переприменяйте
docker-compose exec api alembic downgrade base
docker-compose exec api alembic upgrade head
```

### PostgreSQL не стартует

```bash
# Проверьте данные
docker-compose exec postgres pg_isready

# Проверьте объем
docker volume ls | grep postgres_data
```

## Чеклист для Production

- [ ] Изменить SECRET_KEY на надежный
- [ ] Включить HTTPS
- [ ] Настроить CORS правильно (не "*")
- [ ] Отключить debug режим
- [ ] Настроить логирование
- [ ] Настроить мониторинг
- [ ] Создать резервные копии БД
- [ ] Настроить автоматические резервные копии
- [ ] Включить rate limiting
- [ ] Настроить email уведомления об ошибках
- [ ] Документировать процесс развертывания
- [ ] Протестировать откат версии
