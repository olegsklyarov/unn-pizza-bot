# План лекции: Dockerizing Telegram бота

**Длительность:** 90 минут
**Тема:** Контейнеризация Telegram бота с использованием Docker и Docker Compose
**Целевая аудитория:** Студенты университета

---

## Структура лекции

### 1. Введение и мотивация (10 минут)

**Ключевые идеи:**
- Docker решает проблему "у меня работает, а у тебя нет"
- Контейнеры vs виртуальные машины: легковесность и изоляция
- Основные концепции: Image → Container, Dockerfile, Docker Compose
- Преимущества: единая среда, масштабирование, простое развертывание

**Live демо:**
- Показать структуру проекта и зависимости
- Объяснить проблему разных окружений

---

### 2. Dockerfile - Теория и практика (20 минут)

**Теоретическая часть (5 мин):**
- Dockerfile - инструкции для сборки образа
- Основные инструкции: FROM, WORKDIR, COPY, RUN, ENV, CMD
- Важность порядка инструкций для кеширования слоев

**Live Coding (15 мин):**
- Создание Dockerfile пошагово:
  1. `FROM python:3.13-slim` - базовый образ
  2. `WORKDIR /app` - рабочая директория
  3. `COPY requirements.txt .` - копирование зависимостей
  4. `RUN python -m venv ... && pip install ...` - установка зависимостей
  5. `COPY bot/ ./bot/` - копирование кода
  6. `ENV PATH="/app/venv/bin:$PATH"` - настройка окружения
  7. `CMD ["python", "-m", "bot"]` - команда запуска
- Создание `.dockerignore` для оптимизации
- Тестирование сборки: `docker build -t pizza-bot .`

---

### 3. Docker Compose - Теория и практика (25 минут)

**Теоретическая часть (5 мин):**
- Docker Compose - оркестрация multi-container приложений
- Структура docker-compose.yml: services, volumes, networks
- Основные директивы: build, image, environment, ports, depends_on

**Live Coding (20 мин):**

**Сервис PostgreSQL (10 мин):**
```yaml
services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DATABASE}
    ports:
      - "${POSTGRES_PORT}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
```
- Объяснение: переменные окружения, проброс портов, тома, healthcheck

**Сервис Telegram бота (10 мин):**
```yaml
  telegram_bot:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      POSTGRES_HOST: postgres  # Имя сервиса в Docker сети
      POSTGRES_USER: ${POSTGRES_USER}
      # ... остальные переменные
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
```
- Объяснение: build vs image, Docker DNS (имена сервисов), зависимости, перезапуск

---

### 4. Запуск и тестирование (15 минут)

**Подготовка (3 мин):**
- Создание .env файла из .env.example
- Важно: `POSTGRES_HOST=postgres` для Docker сети

**Запуск (5 мин):**
```bash
docker-compose up --build        # Сборка и запуск
docker-compose up -d --build     # Фоновый режим
docker-compose logs -f telegram_bot  # Логи
docker-compose ps                # Статус
docker-compose down              # Остановка
```

**Проверка (7 мин):**
- Проверка статуса контейнеров
- Просмотр логов бота и PostgreSQL
- Тестирование подключения к БД
- Проверка работы бота

---

### 5. Лучшие практики (5 минут)

**Оптимизация:**
- Порядок инструкций: зависимости → код (для кеширования)
- Использование .dockerignore
- Минимизация слоев в RUN командах

**Безопасность:**
- Секреты в .env, не в образах
- Использование slim образов

---

### 6. Вопросы и ответы (5 минут)

**Ключевые моменты:**
1. Dockerfile создает образ, Docker Compose оркестрирует контейнеры
2. Порядок инструкций важен для кеширования
3. Контейнеры общаются по именам сервисов в Docker сети
4. Используйте .dockerignore для оптимизации

---

## Домашнее задание

1. Создать Dockerfile для проекта
2. Создать docker-compose.yml (приложение + БД)
3. Добавить .dockerignore
4. Запустить через Docker Compose
5. Проверить работу

**Критерии:**
- ✅ Dockerfile собирается без ошибок
- ✅ docker-compose.yml запускает все сервисы
- ✅ Приложение работает в контейнере
- ✅ Используется .dockerignore
- ✅ Переменные в .env

---

## Шаблоны

### Dockerfile
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt
COPY bot/ ./bot/
ENV PATH="/app/venv/bin:$PATH"
CMD ["python", "-m", "bot"]
```

### docker-compose.yml
```yaml
services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DATABASE}
    ports:
      - "${POSTGRES_PORT}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]

  telegram_bot:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      POSTGRES_HOST: postgres
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DATABASE: ${POSTGRES_DATABASE}
      TELEGRAM_TOKEN: ${TELEGRAM_TOKEN}
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
```

---

## Примечания для преподавателя

**Частые проблемы:**
1. Ошибка подключения к БД → проверить `POSTGRES_HOST=postgres` (имя сервиса)
2. Ошибка сборки → проверить requirements.txt и синтаксис Dockerfile
3. Контейнер падает → проверить логи: `docker-compose logs telegram_bot`
