# fb farm

Проект: автоматизация и управление пулом аккаунтов Facebook (MVP).

Структура проекта:

- docker-compose.yml - локальная среда: Postgres, Redis, worker, web
- Dockerfile - образ приложения
- requirements.txt
- src/ - исходники
- db/schema.sql - схема БД
- .env.example
- README.md

Важно: это начальный skeleton. Перед деплоем заполните .env и выполните миграции/инициализацию базы.
