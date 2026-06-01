# Resale Radar MVP

Telegram-сервис для подборки товаров из Китая и Японии под перепродажу на Авито.

## Состав проекта

- `bot/` — Telegram Bot на aiogram: `/start`, меню, поддержка, покупка-заглушка, кнопка Mini App.
- `backend/` — FastAPI API, SQLAlchemy-модели, Alembic, seed тестовых товаров, отправка инструкций через Telegram Bot API.
- `frontend/` — Telegram Mini App на React + Vite.
- `docker-compose.yml` — PostgreSQL, backend, frontend, bot.

## MVP-функции

- Пользователь открывает бота и видит меню: открыть приложение, купить доступ, поддержка.
- Mini App проверяет доступ пользователя через `is_premium`.
- Без доступа показывается экран оплаты-заглушки.
- Для теста есть кнопка `Активировать демо-доступ`.
- После доступа пользователь выбирает страну, площадку и категорию.
- API показывает только товары, где `seller_is_suspicious = false`.
- Карточка товара содержит фото, бренд, цены, доставку, прибыль, риск, ссылку и кнопку инструкции.
- Кнопка `Получить инструкцию` вызывает backend, backend отправляет инструкцию пользователю в Telegram.
- В базе создаются 20 тестовых товаров: 10 из Китая и 10 из Японии. Подозрительные товары сидируются, но не отображаются.

## Запуск через Docker

1. Скопируй переменные окружения:

```bash
cp .env.example .env
```

2. Вставь `BOT_TOKEN` в `.env`.

3. Запусти проект:

```bash
docker compose up --build
```

4. Проверь сервисы:

- Backend: `http://localhost:8000/docs`
- Mini App в браузере: `http://localhost:5173?telegram_id=1001`

Для реального открытия Mini App из Telegram нужен HTTPS-адрес. На локальной машине можно поднять туннель, указать его в `MINI_APP_URL` и перезапустить `bot`.

## Автономный бесплатный деплой

Самая простая бесплатная схема:

- Supabase Free — PostgreSQL.
- Render Free — backend FastAPI и Telegram webhook.
- Cloudflare Pages — Mini App frontend.

Минусы бесплатной схемы: Render может засыпать после простоя, первый ответ иногда занимает около минуты. Для настоящих продаж лучше VPS.

### 1. GitHub

Создай репозиторий на GitHub и загрузи туда проект.

### 2. Supabase

1. Создай проект в Supabase.
2. Открой `Project Settings` -> `Database`.
3. Скопируй connection string для PostgreSQL.
4. Используй вариант с паролем и доменом Supabase. Для Render обычно нужен URL вида:

```text
postgresql+psycopg://USER:PASSWORD@HOST:5432/postgres
```

### 3. Render

1. Создай новый Blueprint/Web Service из GitHub-репозитория.
2. Render увидит `render.yaml`.
3. Укажи переменные:

```env
DATABASE_URL=postgresql+psycopg://...
BOT_TOKEN=новый_токен_бота
MINI_APP_URL=https://адрес-cloudflare-pages
CORS_ORIGINS=https://адрес-cloudflare-pages
```

`TELEGRAM_WEBHOOK_SECRET` Render может сгенерировать сам.

После деплоя Render даст backend URL, например:

```text
https://resale-radar-api.onrender.com
```

### 4. Cloudflare Pages

1. Создай Pages project из того же GitHub-репозитория.
2. Root directory: `frontend`.
3. Build command:

```bash
npm install && npm run build
```

4. Build output directory:

```text
dist
```

5. Environment variable:

```env
VITE_API_BASE_URL=https://твой-backend.onrender.com
```

После деплоя Cloudflare даст HTTPS-ссылку. Ее нужно поставить в Render как `MINI_APP_URL` и `CORS_ORIGINS`.

### 5. Telegram webhook

В локальном терминале выполни:

```bash
export BOT_TOKEN="новый_токен_бота"
export BACKEND_URL="https://твой-backend.onrender.com"
export TELEGRAM_WEBHOOK_SECRET="секрет_из_Render"
bash scripts/set_webhook.sh
```

Проверка:

```bash
bash scripts/check_webhook.sh
```

### 6. BotFather Mini App

В `@BotFather`:

```text
/mybots
Bot Settings
Menu Button
Configure menu button
```

URL: Cloudflare Pages HTTPS-ссылка.

Название кнопки:

```text
Открыть приложение
```

## Локальный запуск без Docker

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Bot:

```bash
cd bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m main
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## База данных

Таблицы:

- `users`
- `items`
- `favorites`
- `instructions`

Alembic лежит в `backend/alembic`. В MVP backend также создает таблицы и сидит демо-данные при старте, чтобы проект запускался сразу.

## Будущие подключения

Подготовлены интерфейсы для:

- парсеров Goofish, Mercari, Yahoo Auctions;
- анализа цен Авито;
- курсов валют;
- автоматических уведомлений;
- платной подписки.
