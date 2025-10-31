# План лекции: Реализация оплаты в Telegram чат-боте

**Длительность:** 90 минут
**Тема:** Интеграция платежной системы YooKassa в Telegram бот для заказа пиццы
**Целевая аудитория:** Студенты университета

---

## Структура лекции

### 1. Введение и контекст (10 минут)

#### 1.1. Приветствие и цели лекции (2 мин)
**Заметки для спикера:**
- Представиться, если нужно
- Объяснить, что сегодня изучим полный цикл интеграции платежей
- Показать финальный результат: бот с возможностью оплаты через Telegram Payments

#### 1.2. Архитектура проекта (3 мин)
**Заметки для спикера:**
- Показать структуру проекта на слайде/экране
- Объяснить паттерн Domain-Driven Design:
  - `domain/` - бизнес-логика, абстракции
  - `infrastructure/` - конкретные реализации (SQLite, Telegram API)
  - `handlers/` - обработчики различных событий
- Показать диаграмму или дерево файлов

#### 1.3. Текущее состояние проекта (5 мин)
**Заметки для спикера:**
- Объяснить, что бот уже умеет:
  - Выбор пиццы, размера, напитков
  - Сохранение состояния в БД
  - Отправка summary заказа
- Показать на слайде состояния заказа (OrderState enum)
- Упомянуть, что сегодня добавим оплату

**Код для показа:**
```python
# bot/domain/order_state.py
class OrderState(str, Enum):
    WAIT_FOR_PIZZA_NAME = "WAIT_FOR_PIZZA_NAME"
    WAIT_FOR_PIZZA_SIZE = "WAIT_FOR_PIZZA_SIZE"
    WAIT_FOR_DRINKS = "WAIT_FOR_DRINKS"
    WAIT_FOR_ORDER_APPROVE = "WAIT_FOR_ORDER_APPROVE"
    ORDER_FINISHED = "ORDER_FINISHED"
```

---

### 2. Telegram Payments - Теоретическая часть (15 минут)

#### 2.1. Обзор Telegram Payments (5 мин)
**Заметки для спикера:**
- Объяснить, что Telegram Payments - встроенная система оплаты
- Преимущества:
  - Не нужно уходить из чата
  - Интегрирована в интерфейс Telegram
  - Поддержка разных платежных систем (YooKassa для РФ)
- Показать схему процесса на слайде

**Диаграмма для показа:**
```
Пользователь → Бот → sendInvoice → Telegram → YooKassa → Оплата → PreCheckoutQuery → SuccessfulPayment
```

#### 2.2. Методы Telegram Bot API для платежей (7 мин)
**Заметки для спикера:**
- Показать три ключевых метода API:

**1. sendInvoice** - отправка инвойса пользователю
```python
POST /bot{token}/sendInvoice
{
  "chat_id": 12345,
  "title": "Pizza Order",
  "description": "Pizza: Margherita, Size: Medium",
  "payload": "{\"order_id\": 123}",  # Уникальные данные заказа
  "provider_token": "",  # Пустая строка для YooKassa
  "currency": "RUB",
  "prices": [
    {"label": "Pizza", "amount": 65000},  # В копейках!
    {"label": "Drink", "amount": 10000}
  ]
}
```

**2. answerPreCheckoutQuery** - подтверждение перед оплатой
```python
POST /bot{token}/answerPreCheckoutQuery
{
  "pre_checkout_query_id": "query_123",
  "ok": true  # или false с error_message
}
```

**3. SuccessfulPayment** - это update, который получает бот после оплаты
- Показать структуру update с successful_payment

#### 2.3. Важные детали YooKassa (3 мин)
**Заметки для спикера:**
- Для YooKassa с валютой RUB:
  - `provider_token` должен быть пустой строкой `""`
  - YooKassa автоматически выбирается для RUB
  - Цены указываются в копейках (минимальная единица)
- Упомянуть проблему, которая возникла: `PAYMENT_PROVIDER_INVALID`
  - Причина: передавали токен вместо пустой строки
  - Решение: использовать `provider_token=""`

---

### 3. Рефакторинг: Enum OrderState (10 минут)

#### 3.1. Проблема: Magic Strings (3 мин)
**Заметки для спикера:**
- Показать старый код с магическими строками:
```python
# БЫЛО:
storage.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")
if state == "WAIT_FOR_PIZZA_SIZE":
    ...
```

**Проблемы:**
- Опечатки не ловятся компилятором
- Нет автодополнения в IDE
- Сложно рефакторить
- Нет централизованного списка всех состояний

#### 3.2. Решение: Python Enum (4 мин)
**Заметки для спикера:**
- Показать создание enum:
```python
# bot/domain/order_state.py
from enum import Enum

class OrderState(str, Enum):
    """Enum representing the possible states of a pizza order."""
    WAIT_FOR_PIZZA_NAME = "WAIT_FOR_PIZZA_NAME"
    WAIT_FOR_PIZZA_SIZE = "WAIT_FOR_PIZZA_SIZE"
    WAIT_FOR_DRINKS = "WAIT_FOR_DRINKS"
    WAIT_FOR_ORDER_APPROVE = "WAIT_FOR_ORDER_APPROVE"
    ORDER_FINISHED = "ORDER_FINISHED"
```

**Почему `str, Enum`?**
- Наследование от `str` позволяет использовать значения как строки
- Совместимость с существующим кодом (БД хранит строки)
- Можно сравнивать: `state == OrderState.WAIT_FOR_PIZZA_NAME`

#### 3.3. Замена всех magic strings (3 мин)
**Заметки для спикера:**
- Показать процесс замены во всех handlers:
  - Импорт: `from bot.domain.order_state import OrderState`
  - Замена: `"WAIT_FOR_PIZZA_NAME"` → `OrderState.WAIT_FOR_PIZZA_NAME`
- Упомянуть, что это коммит `4499bec Enum OrderState`

**Код для показа:**
```python
# БЫЛО:
if state != "WAIT_FOR_PIZZA_NAME":
    return False

# СТАЛО:
if state != OrderState.WAIT_FOR_PIZZA_NAME:
    return False
```

---

### 4. Разделение обработчика approval (8 минут)

#### 4.1. Проблема: Один большой handler (3 мин)
**Заметки для спикера:**
- Показать старый `order_approval.py`:
  - Обрабатывал и `order_approve`, и `order_restart`
  - Использовал `if/elif` внутри handle()
  - Нарушение Single Responsibility Principle

#### 4.2. Решение: Разделение на два handlers (3 мин)
**Заметки для спикера:**
- Создать два отдельных handler'а:

**OrderApprovalApprovedHandler:**
```python
def can_handle(...) -> bool:
    if "callback_query" not in update:
        return False
    if state != OrderState.WAIT_FOR_ORDER_APPROVE:
        return False
    callback_data = update["callback_query"]["data"]
    return callback_data == "order_approve"  # Только approve
```

**OrderApprovalRestartHandler:**
```python
def can_handle(...) -> bool:
    # ... похожая проверка
    return callback_data == "order_restart"  # Только restart
```

**Преимущества:**
- Каждый handler отвечает за одно действие
- Легче тестировать
- Легче поддерживать
- Четче структура кода

#### 4.3. Регистрация handlers (2 мин)
**Заметки для спикера:**
- Показать обновленный `__init__.py`:
```python
def get_handlers() -> list[Handler]:
    return [
        # ... другие handlers
        OrderApprovalApprovedHandler(),  # Новый
        OrderApprovalRestartHandler(),   # Новый
        # ...
    ]
```

**Упомянуть коммит:** `da403ff Split the order_approval.py handler`

---

### 5. Интеграция sendInvoice (20 минут)

#### 5.1. Добавление метода в Messenger (5 мин)
**Заметки для спикера:**
- Показать добавление метода в интерфейс:

```python
# bot/domain/messenger.py
@abstractmethod
def send_invoice(
    self,
    chat_id: int,
    title: str,
    description: str,
    payload: str,
    provider_token: str,
    currency: str,
    prices: list,
    **kwargs,
) -> dict: ...
```

- Показать реализацию в `MessengerTelegram`:
```python
def send_invoice(...) -> dict:
    return self._make_request(
        "sendInvoice",
        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token=provider_token,
        currency=currency,
        prices=prices,
        **kwargs,
    )
```

**Упомянуть коммит:** `3646b1f sendInvoice Telegram Bot API method added`

#### 5.2. Обновление OrderApprovalApprovedHandler (10 мин)
**Заметки для спикера:**
- Показать новый код обработчика:
  1. Расчет цен на основе размера пиццы и напитка
  2. Формирование prices массива (в копейках!)
  3. Создание payload с данными заказа
  4. Отправка invoice

**Код для детального разбора:**
```python
# Расчет цен (в копейках для RUB)
pizza_prices = {
    "Small (25cm)": 50000,   # 500.00 RUB
    "Medium (30cm)": 65000,  # 650.00 RUB
    "Large (35cm)": 80000,   # 800.00 RUB
    "Extra Large (40cm)": 95000,  # 950.00 RUB
}
drink_price = 10000  # 100.00 RUB

pizza_price = pizza_prices.get(pizza_size, 50000)
prices = [
    {"label": f"Pizza: {pizza_name} ({pizza_size})", "amount": pizza_price}
]

if drink and drink != "No drinks":
    prices.append({"label": f"Drink: {drink}", "amount": drink_price})

# Payload - JSON строка с данными заказа
order_payload = json.dumps({
    "telegram_id": telegram_id,
    "pizza_name": pizza_name,
    "pizza_size": pizza_size,
    "drink": drink,
})

# Отправка invoice
messenger.send_invoice(
    chat_id=update["callback_query"]["message"]["chat"]["id"],
    title="Pizza Order",
    description=f"Pizza: {pizza_name}, Size: {pizza_size}, Drink: {drink}",
    payload=order_payload,
    provider_token="",  # Пустая строка для YooKassa!
    currency="RUB",
    prices=prices,
)
```

**Важные моменты:**
- Цены в копейках (минимальная единица валюты)
- Payload - JSON строка, будет передан обратно в successful_payment
- `provider_token=""` для YooKassa

#### 5.3. Обработка ошибок HTTP (5 мин)
**Заметки для спикера:**
- Показать улучшение `_make_request`:
```python
try:
    with urllib.request.urlopen(request) as response:
        # ... обработка ответа
except urllib.error.HTTPError as e:
    # Печатаем тело ответа для отладки
    error_body = e.read().decode("utf-8")
    print(f"HTTP Error {e.code}: {error_body}")
    raise
```

**Почему это важно:**
- Помогает отлаживать проблемы с API
- Видим точную ошибку от Telegram (например, `PAYMENT_PROVIDER_INVALID`)
- Упрощает диагностику

---

### 6. Обработка PreCheckoutQuery (12 минут)

#### 6.1. Что такое PreCheckoutQuery? (3 мин)
**Заметки для спикера:**
- Объяснить, что это запрос перед оплатой
- Telegram отправляет его боту после того, как пользователь нажал "Pay"
- Бот должен подтвердить или отклонить
- Можно проверить сумму, валюту, данные заказа

**Схема:**
```
Пользователь нажимает "Pay" →
Telegram отправляет PreCheckoutQuery →
Бот проверяет →
Бот отвечает ok=true/false
```

#### 6.2. Добавление метода answerPreCheckoutQuery (3 мин)
**Заметки для спикера:**
- Показать добавление в интерфейс:
```python
@abstractmethod
def answer_pre_checkout_query(
    self, pre_checkout_query_id: str, ok: bool, **kwargs
) -> dict: ...
```

- Показать реализацию:
```python
def answer_pre_checkout_query(...) -> dict:
    return self._make_request(
        "answerPreCheckoutQuery",
        pre_checkout_query_id=pre_checkout_query_id,
        ok=ok,
        **kwargs,
    )
```

#### 6.3. Создание PreCheckoutQueryHandler (6 мин)
**Заметки для спикера:**
- Показать создание нового handler'а:
```python
class PreCheckoutQueryHandler(Handler):
    def can_handle(self, update, state, order_json, storage, messenger) -> bool:
        return "pre_checkout_query" in update

    def handle(self, update, state, order_json, storage, messenger) -> HandlerStatus:
        pre_checkout_query = update["pre_checkout_query"]
        pre_checkout_query_id = pre_checkout_query["id"]

        # Подтверждаем оплату
        messenger.answer_pre_checkout_query(
            pre_checkout_query_id=pre_checkout_query_id,
            ok=True
        )

        return HandlerStatus.STOP
```

**Важно объяснить:**
- Handler не зависит от state (может обработать в любой момент)
- Всегда отвечаем `ok=True` (можно добавить валидацию позже)
- Это коммит `242a33a send invoice, success payment processting`

**Возможные улучшения:**
- Проверка суммы платежа
- Проверка валюты
- Валидация payload
- Проверка наличия товара на складе

---

### 7. Обработка SuccessfulPayment (15 минут)

#### 7.1. Что такое SuccessfulPayment? (3 мин)
**Заметки для спикера:**
- Это update, который Telegram отправляет после успешной оплаты
- Приходит как часть message
- Содержит все данные об оплате
- Включает `invoice_payload` - те данные, которые мы отправили в sendInvoice

**Структура update:**
```json
{
  "update_id": 123,
  "message": {
    "message_id": 456,
    "from": {...},
    "chat": {...},
    "successful_payment": {
      "currency": "RUB",
      "total_amount": 75000,
      "invoice_payload": "{\"telegram_id\":12345,\"pizza_name\":\"...\"}",
      "telegram_payment_charge_id": "...",
      "provider_payment_charge_id": "..."
    }
  }
}
```

#### 7.2. Создание SuccessfulPaymentHandler (8 мин)
**Заметки для спикера:**
- Показать создание handler'а:
```python
class SuccessfulPaymentHandler(Handler):
    def can_handle(self, update, state, order_json, storage, messenger) -> bool:
        if "message" not in update:
            return False
        return "successful_payment" in update["message"]

    def handle(self, update, state, order_json, storage, messenger) -> HandlerStatus:
        telegram_id = update["message"]["from"]["id"]
        successful_payment = update["message"]["successful_payment"]

        # Парсим payload, который мы отправили в sendInvoice
        payload = json.loads(successful_payment["invoice_payload"])
        pizza_name = payload.get("pizza_name", "Unknown")
        pizza_size = payload.get("pizza_size", "Unknown")
        drink = payload.get("drink", "Unknown")

        # Обновляем состояние на ORDER_FINISHED
        storage.update_user_state(telegram_id, OrderState.ORDER_FINISHED)

        # Отправляем подтверждение
        order_confirmation = f"""✅ **Order Confirmed!**
🍕 **Your Order:**
• Pizza: {pizza_name}
• Size: {pizza_size}
• Drink: {drink}

Thank you for your payment! Your pizza will be ready soon.

Send /start to place another order."""

        messenger.send_message(
            chat_id=update["message"]["chat"]["id"],
            text=order_confirmation,
            parse_mode="Markdown",
        )

        return HandlerStatus.STOP
```

**Важные моменты:**
- Извлекаем данные из `invoice_payload` (наш JSON)
- Обновляем состояние на `ORDER_FINISHED`
- Отправляем подтверждение пользователю
- Можно добавить отправку заказа на кухню/в систему

#### 7.3. Регистрация новых handlers (2 мин)
**Заметки для спикера:**
- Показать обновленный список handlers:
```python
def get_handlers() -> list[Handler]:
    return [
        UpdateDatabaseLogger(),
        EnsureUserExists(),
        MessageStart(),
        PizzaSelectionHandler(),
        PizzaSizeHandler(),
        PizzaDrinksHandler(),
        OrderApprovalApprovedHandler(),
        OrderApprovalRestartHandler(),
        PreCheckoutQueryHandler(),      # Новый!
        SuccessfulPaymentHandler(),    # Новый!
    ]
```

**Порядок важен!**
- PreCheckoutQueryHandler проверяется перед SuccessfulPaymentHandler
- Если бы было наоборот, могли бы пропустить обработку

#### 7.4. Демо работы (2 мин)
**Заметки для спикера:**
- Если есть возможность, показать живое demo
- Или показать скриншоты/видео процесса оплаты
- Показать финальное сообщение пользователю

---

### 8. Полный процесс оплаты - Анализ (10 минут)

#### 8.1. Обзор всего flow (5 мин)
**Заметки для спикера:**
- Показать полный flow на слайде/доске:

```
1. Пользователь нажимает "✅ Ok"
   ↓
2. CallbackQuery update → OrderApprovalApprovedHandler
   → sendInvoice
   ↓
3. Пользователь видит invoice → нажимает "Pay"
   ↓
4. PreCheckoutQuery update → PreCheckoutQueryHandler
   → answerPreCheckoutQuery(ok=true)
   ↓
5. Пользователь подтверждает в платежной системе
   ↓
6. SuccessfulPayment update → SuccessfulPaymentHandler
   → update state to ORDER_FINISHED
   → send confirmation message
```

#### 8.2. HTTP запросы и SQL операции (3 мин)
**Заметки для спикера:**
- Показать все HTTP запросы:
  1. `answerCallbackQuery` - подтверждение кнопки
  2. `deleteMessage` - удаление summary
  3. `sendInvoice` - отправка инвойса
  4. `answerPreCheckoutQuery` - подтверждение перед оплатой
  5. `sendMessage` - финальное подтверждение

- Показать SQL операции:
  1. `SELECT` - получение пользователя (3 раза)
  2. `INSERT` - сохранение updates в telegram_events (3 раза)
  3. `UPDATE` - изменение state на ORDER_FINISHED (1 раз)

#### 8.3. Открыть PAYMENT_FLOW.md (2 мин)
**Заметки для спикера:**
- Показать файл `PAYMENT_FLOW.md`
- Объяснить, что там детальное описание на всех уровнях
- Рекомендовать изучить его для понимания всех деталей

---

### 9. Практические советы и лучшие практики (5 минут)

#### 9.1. Валидация платежей (2 мин)
**Заметки для спикера:**
- Рекомендации для production:
  - Проверять сумму в PreCheckoutQuery
  - Проверять валюту
  - Валидировать payload
  - Логировать все платежи
  - Хранить invoice_id для связи с платежной системой

**Код примера валидации:**
```python
def handle(self, ...):
    pre_checkout_query = update["pre_checkout_query"]

    # Валидация суммы
    expected_total = 75000  # из БД или расчет
    if pre_checkout_query["total_amount"] != expected_total:
        messenger.answer_pre_checkout_query(
            pre_checkout_query_id=pre_checkout_query["id"],
            ok=False,
            error_message="Сумма заказа изменилась. Пожалуйста, создайте новый заказ."
        )
        return HandlerStatus.STOP

    # Валидация валюты
    if pre_checkout_query["currency"] != "RUB":
        # ...

    # Если все ок
    messenger.answer_pre_checkout_query(
        pre_checkout_query_id=pre_checkout_query["id"],
        ok=True
    )
```

#### 9.2. Обработка ошибок (2 мин)
**Заметки для спикера:**
- Что делать при ошибках:
  - Логировать все исключения
  - Отправлять пользователю понятные сообщения
  - Не менять state при ошибках
  - Использовать idempotent операции

#### 9.3. Тестирование (1 мин)
**Заметки для спикера:**
- Использовать тестовые карты YooKassa
- Тестировать все сценарии:
  - Успешная оплата
  - Отклонение пользователем
  - Ошибки платежной системы
- Использовать staging окружение

---

### 10. Вопросы и ответы (5 минут)

**Заметки для спикера:**
- Подготовить ответы на частые вопросы:
  - Как работает YooKassa?
  - Можно ли использовать другие платежные системы?
  - Как обрабатывать возвраты?
  - Безопасность платежей
  - Как масштабировать на продакшн?

---

## Домашнее задание (для студентов)

### Задание 1: Добавить валидацию PreCheckoutQuery
Добавить проверку суммы платежа в `PreCheckoutQueryHandler`:
- Рассчитать ожидаемую сумму на основе данных заказа
- Сравнить с `total_amount` из query
- Если не совпадает, отклонить с понятным сообщением

### Задание 2: Улучшить обработку ошибок
- Добавить try-catch в handlers
- Логировать ошибки
- Отправлять пользователю сообщения об ошибках

### Задание 3: Добавить тесты
- Написать тест для `PreCheckoutQueryHandler`
- Написать тест для `SuccessfulPaymentHandler`
- Использовать моки для Messenger и Storage

---

## Резюме изменений в ветке payments

### Коммиты:
1. **`4499bec` - Enum OrderState**
   - Создан `bot/domain/order_state.py`
   - Заменены все magic strings на enum значения
   - Улучшена типобезопасность

2. **`3646b1f` - sendInvoice метод**
   - Добавлен метод `send_invoice` в `Messenger` интерфейс
   - Реализован в `MessengerTelegram`
   - Добавлена обработка HTTP ошибок

3. **`da403ff` - Разделение order_approval**
   - Создан `OrderApprovalApprovedHandler`
   - Создан `OrderApprovalRestartHandler`
   - Удален старый `order_approval.py`

4. **`242a33a` - Интеграция оплаты**
   - Реализован `sendInvoice` в `OrderApprovalApprovedHandler`
   - Создан `PreCheckoutQueryHandler`
   - Создан `SuccessfulPaymentHandler`
   - Обновлена регистрация handlers

5. **`b0d1b53` - Описание процесса**
   - Создан `PAYMENT_FLOW.md` с детальным описанием
   - Документация всего процесса оплаты

### Новые файлы:
- `bot/domain/order_state.py` - enum состояний заказа
- `bot/handlers/order_approval_approved.py` - обработка подтверждения
- `bot/handlers/order_approval_restart.py` - обработка перезапуска
- `bot/handlers/pre_checkout_query.py` - обработка pre-checkout
- `bot/handlers/successful_payment.py` - обработка успешной оплаты
- `PAYMENT_FLOW.md` - документация процесса

### Измененные файлы:
- `bot/domain/messenger.py` - добавлен `send_invoice` и `answer_pre_checkout_query`
- `bot/infrastructure/messenger_telegram.py` - реализация новых методов, обработка ошибок
- `bot/infrastructure/storage_sqlite.py` - тип state изменен на `OrderState`
- `bot/domain/storage.py` - тип state в `update_user_state` изменен
- Все handlers - использование `OrderState` enum вместо строк
- `bot/handlers/__init__.py` - регистрация новых handlers

---

## Дополнительные материалы для демонстрации

### Слайды для показа:
1. Архитектура проекта (дерево файлов)
2. Диаграмма flow оплаты
3. Сравнение кода "до" и "после"
4. Структура update для каждого этапа
5. HTTP запросы с примерами
6. SQL запросы с примерами

### Код для live coding (опционально):
- Показать создание enum
- Показать разделение handler'а
- Показать добавление sendInvoice
- Показать создание новых handlers

---

## Контрольные вопросы для студентов

1. Почему мы используем `str, Enum` для OrderState?
2. Зачем разделили `order_approval` на два handler'а?
3. Почему `provider_token=""` для YooKassa?
4. Почему цены указываются в копейках?
5. Что содержит `invoice_payload` и зачем он нужен?
6. В каком порядке вызываются handlers?
7. Когда меняется state на `ORDER_FINISHED`?
8. Какие SQL операции выполняются при оплате?
9. Как обрабатываются HTTP ошибки?
10. Что можно улучшить в текущей реализации?

---

## Заметки для спикера

### Технические моменты:
- Убедиться, что есть доступ к проекту на GitHub/GitLab
- Подготовить демо-бот или скриншоты
- Иметь под рукой `PAYMENT_FLOW.md`
- Готовые примеры кода в IDE

### Время на секции:
- Введение: 10 мин (строго!)
- Теория: 15 мин
- Практика: 50 мин
- Вопросы: 10 мин
- Буфер: 5 мин

### Интерактивность:
- Задавать вопросы студентам
- Просить объяснить концепции
- Обсудить альтернативные решения
- Привести аналогии из реальной жизни

### Если что-то пошло не так:
- Не паниковать при технических проблемах
- Использовать `PAYMENT_FLOW.md` как план Б
- Перейти к вопросам раньше, если отстали
- Помнить про 5 минут буфера

---

**Удачи на лекции! 🍕**

