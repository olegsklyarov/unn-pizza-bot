# План миграции на асинхронность и добавления логирования

## Часть 1: Добавление логирования (для демонстрации синхронности)

### 1.1. Логирование HTTP запросов

**Файл:** `bot/infrastructure/messenger_telegram.py`

**Изменения:**
- Добавить модуль `logging` и настроить логгер
- Обернуть метод `_make_request` логированием:
  - Логировать начало запроса: `[HTTP] → {method} {url}`
  - Засечь время начала запроса
  - После получения ответа логировать: `[HTTP] ← {method} {url} - {duration}ms`
  - Показывать время выполнения в миллисекундах

**Пример вывода:**
```
[2024-01-15 10:23:45.123] [HTTP] → POST https://api.telegram.org/bot.../sendMessage
[2024-01-15 10:23:45.456] [HTTP] ← POST sendMessage - 333ms
[2024-01-15 10:23:45.457] [HTTP] → POST https://api.telegram.org/bot.../deleteMessage
[2024-01-15 10:23:45.789] [HTTP] ← POST deleteMessage - 332ms
```

### 1.2. Логирование запросов к БД

**Файл:** `bot/infrastructure/storage_postgres.py`

**Изменения:**
- Добавить модуль `logging` и настроить логгер
- Обернуть каждый SQL запрос логированием:
  - Логировать начало: `[DB] → {method_name} - {sql_query}`
  - Засечь время начала
  - После выполнения логировать: `[DB] ← {method_name} - {duration}ms`

**Пример вывода:**
```
[2024-01-15 10:23:45.100] [DB] → get_user - SELECT ... FROM users WHERE telegram_id = %s
[2024-01-15 10:23:45.120] [DB] ← get_user - 20ms
[2024-01-15 10:23:45.121] [DB] → update_user_order_json - UPDATE users SET order_json = %s ...
[2024-01-15 10:23:45.140] [DB] ← update_user_order_json - 19ms
```

### 1.3. Настройка логирования

**Создать:** `bot/infrastructure/logger.py` (опционально, для централизованной настройки)

**Или добавить в начало каждого файла:**
```python
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s.%(msecs)03d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

**Результат:** В терминале будет видно, что все запросы выполняются последовательно, один за другим.

---

## Часть 2: Миграция на асинхронность

### 2.1. Обновление зависимостей

**Файл:** `requirements.txt`

**Добавить:**
- `aiohttp` - для асинхронных HTTP запросов
- `asyncpg` - для асинхронных запросов к PostgreSQL

**Удалить:**
- `pg8000` (заменяется на `asyncpg`)

### 2.2. Асинхронизация HTTP запросов (Messenger)

**Файл:** `bot/infrastructure/messenger_telegram.py`

**Изменения:**
- Заменить `urllib.request` на `aiohttp.ClientSession`
- Сделать все методы `async`
- Использовать `async with aiohttp.ClientSession() as session:`
- Использовать `await session.post(...)`
- Сохранить логирование, добавив информацию о параллельности

**Новая структура:**
```python
class MessengerTelegram(Messenger):
    def __init__(self):
        self._session: aiohttp.ClientSession | None = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def _make_request(self, method: str, **kwargs) -> dict:
        # async HTTP request with logging
        ...
    
    async def send_message(self, ...) -> dict:
        ...
    # все методы становятся async
```

### 2.3. Асинхронизация запросов к БД (Storage)

**Файл:** `bot/infrastructure/storage_postgres.py`

**Изменения:**
- Заменить `pg8000` на `asyncpg`
- Использовать connection pool (`asyncpg.create_pool`)
- Сделать все методы `async`
- Использовать `await conn.execute(...)` и `await conn.fetch(...)`
- Сохранить логирование

**Новая структура:**
```python
class StoragePostgres(Storage):
    def __init__(self):
        self._pool: asyncpg.Pool | None = None
    
    async def _get_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(...)
        return self._pool
    
    async def get_user(self, telegram_id: int) -> dict | None:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # async SQL query with logging
            ...
```

### 2.4. Обновление абстрактных классов

**Файл:** `bot/domain/messenger.py`

**Изменения:**
- Все методы должны быть `async`

**Файл:** `bot/domain/storage.py`

**Изменения:**
- Все методы должны быть `async`

### 2.5. Асинхронизация Dispatcher

**Файл:** `bot/dispatcher.py`

**Изменения:**
- Метод `dispatch` должен стать `async`
- Все вызовы `storage` и `messenger` должны быть с `await`

```python
async def dispatch(self, update: dict) -> None:
    telegram_id = self._get_telegram_id_from_update(update)
    user = await self._storage.get_user(telegram_id) if telegram_id else None
    # ...
    for handler in self._handlers:
        if handler.can_handle(...):
            status = await handler.handle(...)
            # ...
```

### 2.6. Асинхронизация Handlers

**Файл:** `bot/handlers/handler.py`

**Изменения:**
- Метод `handle` должен стать `async`
- Метод `can_handle` может остаться синхронным (но если использует storage/messenger, тоже async)

**Все файлы в `bot/handlers/`:**
- Все методы `handle` должны стать `async`
- Все вызовы `storage` и `messenger` должны быть с `await`

**Пример:**
```python
async def handle(
    self,
    update: dict,
    state: OrderState,
    order_json: dict,
    storage: Storage,
    messenger: Messenger,
) -> HandlerStatus:
    telegram_id = update["message"]["from"]["id"]
    
    await storage.clear_user_order_json(telegram_id)
    await storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_NAME)
    
    await messenger.send_message(...)
    await messenger.send_message(...)
    return HandlerStatus.STOP
```

### 2.7. Асинхронизация Long Polling

**Файл:** `bot/long_polling.py`

**Изменения:**
- Функция `start_long_polling` должна стать `async`
- Использовать `asyncio` для основного цикла
- Вызовы `messenger.get_updates` и `dispatcher.dispatch` должны быть с `await`

```python
async def start_long_polling(dispatcher: Dispatcher, messenger: Messenger) -> None:
    next_update_offset = 0
    while True:
        updates = await messenger.get_updates(offset=next_update_offset, timeout=30)
        for update in updates:
            next_update_offset = max(next_update_offset, update["update_id"] + 1)
            await dispatcher.dispatch(update)
            print(".", flush=True)
```

### 2.8. Обновление точки входа

**Файл:** `bot/__main__.py`

**Изменения:**
- Функция `main` должна стать `async`
- Использовать `asyncio.run(main())`

```python
async def main() -> None:
    try:
        storage: Storage = StoragePostgres()
        messenger: Messenger = MessengerTelegram()
        
        dispatcher = Dispatcher(storage, messenger)
        dispatcher.add_handlers(*get_handlers())
        await bot.long_polling.start_long_polling(dispatcher, messenger)
    except KeyboardInterrupt:
        print("\nBye!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 2.9. Оптимизация: Параллельное выполнение независимых операций

**Примеры для оптимизации:**

**В `pizza_selection.py`:**
```python
# Вместо последовательного выполнения:
await storage.update_user_order_json(telegram_id, {"pizza_name": pizza_name})
await storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_SIZE)
await messenger.answer_callback_query(update["callback_query"]["id"])

# Можно выполнить параллельно:
await asyncio.gather(
    storage.update_user_order_json(telegram_id, {"pizza_name": pizza_name}),
    storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_SIZE),
    messenger.answer_callback_query(update["callback_query"]["id"]),
)
```

**В `message_start.py`:**
```python
# Два send_message можно выполнить параллельно:
await asyncio.gather(
    messenger.send_message(...),
    messenger.send_message(...),
)
```

### 2.10. Улучшение логирования для демонстрации параллельности

**Обновить логирование:**
- Добавить уникальный ID для каждого запроса (можно использовать `id(update)` или `uuid`)
- Показывать, когда запросы выполняются параллельно
- Использовать разные префиксы или цвета для HTTP и DB запросов

**Пример вывода после миграции:**
```
[2024-01-15 10:23:45.123] [HTTP] → POST sendMessage [req:abc123]
[2024-01-15 10:23:45.124] [HTTP] → POST deleteMessage [req:def456]
[2024-01-15 10:23:45.125] [DB] → update_user_order_json [req:ghi789]
[2024-01-15 10:23:45.456] [HTTP] ← POST sendMessage - 333ms [req:abc123]
[2024-01-15 10:23:45.457] [HTTP] ← POST deleteMessage - 333ms [req:def456]
[2024-01-15 10:23:45.500] [DB] ← update_user_order_json - 375ms [req:ghi789]
```

Видно, что запросы начались почти одновременно и выполнялись параллельно!

---

## Порядок выполнения

1. **Сначала добавить логирование** (Часть 1)
   - Это покажет текущую синхронность
   - Можно протестировать и убедиться, что логирование работает

2. **Затем мигрировать на асинхронность** (Часть 2)
   - Постепенно, начиная с низкоуровневых компонентов
   - Тестировать после каждого шага

3. **Оптимизировать параллельность** (Часть 2.9)
   - После того, как базовая асинхронность работает
   - Найти места, где можно использовать `asyncio.gather`

---

## Тестирование

После каждого этапа:
1. Запустить бота
2. Отправить несколько сообщений
3. Проверить логи - должны видеть время выполнения
4. После миграции на async - должны видеть параллельность

---

## Важные замечания

1. **Connection Pool для БД:** `asyncpg` использует connection pool, что более эффективно чем создание нового соединения для каждого запроса
2. **HTTP Session:** `aiohttp.ClientSession` должен быть переиспользован, не создавать новый для каждого запроса
3. **Обработка ошибок:** Убедиться, что все async методы правильно обрабатывают исключения
4. **Закрытие ресурсов:** При завершении работы бота нужно закрыть session и pool

