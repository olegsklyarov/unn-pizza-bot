# Aiogram

План
- Введение: зачем, какую проблему решает?
- 

## Что такое Aiogram?

Aiogram — высокоуровневая асинхронная Python-библиотека для разработки Telegram-ботов.

Основана на:
- asyncio
- строгой типизации (pydantic)
- удобной декларативной маршрутизации (Handlers + Filters)
- встроенном FSM

Отличие от вашего “ручного” подхода:
- Обёртка над всех HTTP запросами → не пишем вручную getUpdates/sendMessage.
- Маршрутизация событий → фильтрация и разбор Update (свой Dispatcher + Handlers)
- Свой State менеджмент (FSM)
- Свой Long Polling
- Расширяемость за счёт middleware, роутеров, кастомных фильтров.

Ценность:
- Вы уже умеете писать всё вручную.
- Aiogram убирает рутину → скорость разработки ×5–×10.
- Подходит для продакшена: стабильность, сообщество, тонкая настройка.

## Long polling в aiogram

```python
await dp.start_polling(bot)
```

внутри:
- делает цикл getUpdates
- отдаёт апдейты в Dispatcher
- обрабатывает исключения
- соблюдает rate limits

Фактически — ваш собственный long polling → но спрятан за 3 строками.

🔥 aiogram снимает необходимость думать про `offset`, `timeout`.

## Фильтрация updates: аналогия с их dispatcher/handlers

- Aiogram сам определяет тип Update.
- Внутри работает цепочка фильтров (как if-условия поверх ваших Handlers).
- Гибкие фильтры: набор готовый плюс кастомные
- Каждый @dp.message() = подписка Observer, но уже **декларативно**.

## Dependancy Injection
https://docs.aiogram.dev/en/v3.22.0/dispatcher/dependency_injection.html

follow SOLID’s principles:
- dependency inversion
- single responsibility 

Реализует встроенный в aiogram Dispatcher - смотрим на примерах

## Middleware
https://docs.aiogram.dev/en/v3.22.0/dispatcher/middlewares.html

- Outer scope - before processing filters (<router>.<event>.outer_middleware(...))
- Inner scope - after processing filters but before handler (<router>.<event>.middleware(...))

🔥 Удобно для логирование всех входящих запросов

Не забываем про параметр `allowed_updates` в getUpdates
https://core.telegram.org/bots/api#getupdates

aiogram по умолчанию сам собирает список событий и формирует `allowed_updates` исходя из текущего набора handler'ов. Если нужно логировать вообще всех входящие, то вручную определяем `allowed_updates`!

## FSM в aiogram — управление состояниями
https://docs.aiogram.dev/en/v3.22.0/dispatcher/finite_state_machine/index.html

Aiogram предоставляет встроенную конечную автоматную модель:
- набор состояний
- автоматическое хранение состояний в памяти или Redis
- привязка handler к конкретному состоянию
- Каждое состояние — чёткий этап диалога.
- Aiogram сам обеспечивает маршрутизацию по состояниям.
- Небольшое количество кода позволяет строить сложные многошаговые диалоги.

# Postgres

https://hub.docker.com/_/postgres


https://www.postgresql.org/docs/current/app-pg-isready.html
```bash
(docker) $ pg_isready -U postgres
```

https://www.postgresql.org/docs/current/app-psql.html

```bash
$ psql  -U postgres -h localhost -p 5432
(REPL)
\q - quit
\l - list of all databases
\c pizza_bot - connect to pizza_bot database
\dt - list tables in database
\x - enable extended display
```

https://hub.docker.com/_/python

# Настройка YooKassa (тестовые платежи)

Инструкция: https://yookassa.ru/docs/support/payments/onboarding/integration/cms-module/telegram

Создайте тестовый магазин https://yookassa.ru/docs/support/merchant/payments/implement/test-store (потребуется действующий номер сотового и email)

## Подключите своего бота к боту ЮKassa

1. Открыть чат-бот @BotFather -> /mybots -> <Ваш бот> -> Payments -> "🇷🇺 ЮKassa" -> "Connect ЮKassa Test"

После нажатия, будет открыт:

2. @YooKassaTestBot -> Войти и выдать доступ

Откроется страница https://yookassa.ru/oauth/v2/authorize ...
Нажмите "Разрешить" -> "Выдать доступ" -> "Продолжить"
Подтвердите доступ к ЮKassa (введите смс-код)
Готово — теперь можно проводить тестовые платежи.

3. Получить секретный токен `YOOKASSA_TOKEN` для Вашего бота в разделе Payments через BotFather

## Ссылки
https://core.telegram.org/bots/payments

Тестовые банковские карты
https://yookassa.ru/developers/payment-acceptance/testing-and-going-live/testing#test-bank-card
