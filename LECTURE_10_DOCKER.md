Цель:
1. Запустить чат-бот на VPS при помощи Docker.

План
- Написать Dockerfile для создания docker образа чат бота
- Отделяем PostgreSQL от бота. Заменяем docker-compose.yml на Makefile.
  - Создать volume для postgres
  - Создать network для взаимодействия контейнера PostgreSQL и конейнера с чат-ботом
  - Команда для запуска, остановки и удаления контейнера PostgreSQL
- Команда для сборки (docker build) образа чат-бота (учитываем платформы macOS / amd64)
- Создаем учетку на https://hub.docker.com
- Создаем репозиторий на docker hub
- Публикуем образ бота в docker hub
- Арендуем VDS
- Устанаваливаем rootless docker
- Запускаем бот, образы скачиваем из docker hub

Схема деплоя чат-бота: локальный ноут, гитхам, докер хаб, VDS.


3 дня теста на VPS
https://sweb.ru/web/testvps/

https://www.1gb.ru/price_free_hv.php



Reading assignment

1. https://docs.docker.com/get-started/introduction/build-and-push-first-image
