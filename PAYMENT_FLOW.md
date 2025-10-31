# Процесс оплаты пиццы - Полное описание

Этот документ описывает весь процесс оплаты пиццы на трех уровнях:
1. **HTTP уровень** - все HTTP запросы, которые отправляет бот
2. **Updates уровень** - все обновления (updates), которые получает бот через getUpdates
3. **SQL уровень** - все SQL запросы, выполняемые в базе данных SQLite
4. **UX уровень** - что видит пользователь в чате с ботом

---

## Предварительное состояние

**UX:** Пользователь видит сообщение:
```
🍕 **Your Order Summary:**

**Pizza:** Margherita
**Size:** Medium (30cm)
**Drink:** Coca-Cola

Is everything correct?

[✅ Ok]  [🔄 Start again]
```

**State в БД:** `WAIT_FOR_ORDER_APPROVE`

---

## Этап 1: Пользователь нажимает "✅ Ok"

### UX уровень
Пользователь видит:
- Кнопка "✅ Ok" подсвечивается (визуальный фидбек)

### Update уровень
Бот получает через `getUpdates`:
```json
{
  "update_id": 123456789,
  "callback_query": {
    "id": "callback_query_id_123",
    "from": {
      "id": 12345,
      "is_bot": false,
      "first_name": "Иван",
      "username": "ivan_user"
    },
    "message": {
      "message_id": 100,
      "chat": {
        "id": 12345,
        "type": "private"
      },
      "text": "🍕 **Your Order Summary:**...",
      "reply_markup": {...}
    },
    "data": "order_approve"
  }
}
```

### SQL уровень
1. **get_user** - получение состояния пользователя:
```sql
SELECT id, telegram_id, created_at, state, order_json
FROM users
WHERE telegram_id = 12345;
```

2. **persist_update** - сохранение update в БД (UpdateDatabaseLogger):
```sql
INSERT INTO telegram_events (payload)
VALUES ('{"update_id": 123456789, "callback_query": {...}}');
```

### HTTP уровень
Бот отправляет следующие HTTP запросы:

1. **answerCallbackQuery** - подтверждение получения callback:
```http
POST https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery
Content-Type: application/json

{
  "callback_query_id": "callback_query_id_123"
}
```

2. **deleteMessage** - удаление сообщения с summary:
```http
POST https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteMessage
Content-Type: application/json

{
  "chat_id": 12345,
  "message_id": 100
}
```

3. **sendInvoice** - отправка инвойса для оплаты:
```http
POST https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendInvoice
Content-Type: application/json

{
  "chat_id": 12345,
  "title": "Pizza Order",
  "description": "Pizza: Margherita, Size: Medium (30cm), Drink: Coca-Cola",
  "payload": "{\"telegram_id\":12345,\"pizza_name\":\"Margherita\",\"pizza_size\":\"Medium (30cm)\",\"drink\":\"Coca-Cola\"}",
  "provider_token": "{YOOKASSA_TOKEN}",
  "currency": "RUB",
  "prices": [
    {
      "label": "Pizza: Margherita (Medium (30cm))",
      "amount": 65000
    },
    {
      "label": "Drink: Coca-Cola",
      "amount": 10000
    }
  ]
}
```

---

## Этап 2: Пользователь видит инвойс и нажимает "Pay"

### UX уровень
Пользователь видит в чате:
- **Удаляется** предыдущее сообщение с summary
- **Появляется** платежное окно (invoice) от Telegram:
  - Заголовок: "Pizza Order"
  - Описание: "Pizza: Margherita, Size: Medium (30cm), Drink: Coca-Cola"
  - Детали оплаты:
    - Pizza: Margherita (Medium (30cm)) - 650,00 ₽
    - Drink: Coca-Cola - 100,00 ₽
    - **Итого: 750,00 ₽**
  - Кнопка **"Pay 750 ₽"**

Пользователь нажимает кнопку "Pay 750 ₽".

---

## Этап 3: Пользователь подтверждает оплату в платежной системе

### UX уровень
Пользователь видит:
- Окно платежной системы YooKassa
- Поля для ввода платежных данных (или выбор сохраненного метода)
- Пользователь вводит данные и подтверждает оплату

---

## Этап 4: Telegram отправляет pre_checkout_query

### Update уровень
Бот получает через `getUpdates`:
```json
{
  "update_id": 123456790,
  "pre_checkout_query": {
    "id": "pre_checkout_query_id_456",
    "from": {
      "id": 12345,
      "is_bot": false,
      "first_name": "Иван",
      "username": "ivan_user"
    },
    "currency": "RUB",
    "total_amount": 75000,
    "invoice_payload": "{\"telegram_id\":12345,\"pizza_name\":\"Margherita\",\"pizza_size\":\"Medium (30cm)\",\"drink\":\"Coca-Cola\"}"
  }
}
```

### SQL уровень
1. **get_user** - получение состояния пользователя:
```sql
SELECT id, telegram_id, created_at, state, order_json
FROM users
WHERE telegram_id = 12345;
```

2. **persist_update** - сохранение pre_checkout_query в БД:
```sql
INSERT INTO telegram_events (payload)
VALUES ('{"update_id": 123456790, "pre_checkout_query": {...}}');
```

### HTTP уровень
Бот отправляет:
```http
POST https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerPreCheckoutQuery
Content-Type: application/json

{
  "pre_checkout_query_id": "pre_checkout_query_id_456",
  "ok": true
}
```

### UX уровень
Пользователь видит:
- Обработка платежа...
- Успешное завершение транзакции в платежной системе
- Telegram автоматически отправляет сообщение о успешной оплате

---

## Этап 5: Telegram отправляет successful_payment update

### Update уровень
Бот получает через `getUpdates`:
```json
{
  "update_id": 123456791,
  "message": {
    "message_id": 101,
    "from": {
      "id": 12345,
      "is_bot": false,
      "first_name": "Иван",
      "username": "ivan_user"
    },
    "chat": {
      "id": 12345,
      "type": "private"
    },
    "date": 1640995200,
    "successful_payment": {
      "currency": "RUB",
      "total_amount": 75000,
      "invoice_payload": "{\"telegram_id\":12345,\"pizza_name\":\"Margherita\",\"pizza_size\":\"Medium (30cm)\",\"drink\":\"Coca-Cola\"}",
      "telegram_payment_charge_id": "charge_id_789",
      "provider_payment_charge_id": "yookassa_charge_id_456"
    }
  }
}
```

### SQL уровень
1. **get_user** - получение состояния пользователя:
```sql
SELECT id, telegram_id, created_at, state, order_json
FROM users
WHERE telegram_id = 12345;
```

2. **persist_update** - сохранение successful_payment в БД:
```sql
INSERT INTO telegram_events (payload)
VALUES ('{"update_id": 123456791, "message": {"successful_payment": {...}}}');
```

3. **update_user_state** - обновление состояния на ORDER_FINISHED:
```sql
UPDATE users
SET state = 'ORDER_FINISHED'
WHERE telegram_id = 12345;
```

### HTTP уровень
Бот отправляет:
```http
POST https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage
Content-Type: application/json

{
  "chat_id": 12345,
  "text": "✅ **Order Confirmed!**\n🍕 **Your Order:**\n• Pizza: Margherita\n• Size: Medium (30cm)\n• Drink: Coca-Cola\n\nThank you for your payment! Your pizza will be ready soon.\n\nSend /start to place another order.",
  "parse_mode": "Markdown"
}
```

### UX уровень
Пользователь видит в чате:
```
✅ **Order Confirmed!**
🍕 **Your Order:**
• Pizza: Margherita
• Size: Medium (30cm)
• Drink: Coca-Cola

Thank you for your payment! Your pizza will be ready soon.

Send /start to place another order.
```

---

## Итоговое состояние

### SQL уровень - Финальное состояние БД

**Таблица `users`:**
```sql
SELECT * FROM users WHERE telegram_id = 12345;
```
Результат:
- `state`: `'ORDER_FINISHED'`
- `order_json`: (остается прежним с деталями заказа)

**Таблица `telegram_events`:**
Содержит 3 записи:
1. Callback query с `order_approve`
2. Pre-checkout query
3. Successful payment message

### HTTP уровень - Итого отправлено запросов
1. `answerCallbackQuery` - 1 запрос
2. `deleteMessage` - 1 запрос
3. `sendInvoice` - 1 запрос
4. `answerPreCheckoutQuery` - 1 запрос
5. `sendMessage` - 1 запрос

**Всего: 5 HTTP запросов**

### Updates уровень - Итого получено updates
1. Callback query update (`order_approve`)
2. Pre-checkout query update
3. Successful payment update (внутри message)

**Всего: 3 update'а**

---

## Последовательность обработчиков (Handlers)

Для каждого update вызываются следующие handlers в порядке регистрации:

### Update 1: callback_query с order_approve
1. ✅ `UpdateDatabaseLogger` - сохраняет update в БД → `CONTINUE`
2. ✅ `EnsureUserExists` - проверяет существование пользователя → `CONTINUE`
3. ❌ `MessageStart` - не обрабатывает (не /start)
4. ❌ `PizzaSelectionHandler` - не обрабатывает (state не WAIT_FOR_PIZZA_NAME)
5. ❌ `PizzaSizeHandler` - не обрабатывает (state не WAIT_FOR_PIZZA_SIZE)
6. ❌ `PizzaDrinksHandler` - не обрабатывает (state не WAIT_FOR_DRINKS)
7. ✅ `OrderApprovalApprovedHandler` - **обрабатывает** → `STOP`

### Update 2: pre_checkout_query
1. ✅ `UpdateDatabaseLogger` - сохраняет update → `CONTINUE`
2. ✅ `EnsureUserExists` - проверяет пользователя → `CONTINUE`
3. ❌ `MessageStart` - не обрабатывает
4. ❌ `PizzaSelectionHandler` - не обрабатывает
5. ❌ `PizzaSizeHandler` - не обрабатывает
6. ❌ `PizzaDrinksHandler` - не обрабатывает
7. ❌ `OrderApprovalApprovedHandler` - не обрабатывает
8. ❌ `OrderApprovalRestartHandler` - не обрабатывает
9. ✅ `PreCheckoutQueryHandler` - **обрабатывает** → `STOP`

### Update 3: successful_payment
1. ✅ `UpdateDatabaseLogger` - сохраняет update → `CONTINUE`
2. ✅ `EnsureUserExists` - проверяет пользователя → `CONTINUE`
3. ❌ `MessageStart` - не обрабатывает
4. ❌ `PizzaSelectionHandler` - не обрабатывает
5. ❌ `PizzaSizeHandler` - не обрабатывает
6. ❌ `PizzaDrinksHandler` - не обрабатывает
7. ❌ `OrderApprovalApprovedHandler` - не обрабатывает
8. ❌ `OrderApprovalRestartHandler` - не обрабатывает
9. ❌ `PreCheckoutQueryHandler` - не обрабатывает
10. ✅ `SuccessfulPaymentHandler` - **обрабатывает** → `STOP`

---

## Обработка ошибок

Если происходит ошибка на любом этапе:

### HTTP ошибки (не 2XX статус)
В `_make_request` метод перехватывает `HTTPError`:
- Печатает: `HTTP Error {code}: {response_body}`
- Пробрасывает исключение дальше

### Ошибки в handlers
Если handler выбрасывает исключение:
- Исключение не перехватывается автоматически
- Бот продолжает работать (long polling продолжается)
- Ошибка логируется в консоль (если настроено логирование)

---

## Важные детали

1. **Порядок handlers важен** - handlers вызываются в порядке регистрации
2. **Handler возвращает STOP** - останавливает дальнейшую обработку update
3. **UpdateDatabaseLogger всегда первый** - сохраняет все updates в БД
4. **State не меняется до успешной оплаты** - остается `WAIT_FOR_ORDER_APPROVE` до `ORDER_FINISHED`
5. **Payload содержит JSON строку** - порядок деталей передается в `invoice_payload`

