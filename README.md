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
