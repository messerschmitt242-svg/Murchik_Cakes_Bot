# Murchik Cakes Bot

Telegram-бот і Telegram Mini App для кондитерської **Murchik Cakes**. Проєкт поєднує класичного Telegram-бота для адміністрування з вебкаталогом Mini App для покупців: перегляд десертів, кошик, промокоди, оформлення замовлень, доставка, оплата, відгуки та багатомовність.

---

## Зміст

- [Можливості](#можливості)
- [Структура проєкту](#структура-проєкту)
- [Технології](#технології)
- [Змінні середовища](#змінні-середовища)
- [Локальний запуск](#локальний-запуск)
- [Запуск Mini App API](#запуск-mini-app-api)
- [Деплой на Railway](#деплой-на-railway)
- [Налаштування Telegram Mini App](#налаштування-telegram-mini-app)
- [Адміністрування](#адміністрування)
- [База даних](#база-даних)
- [Кешування фото Telegram](#кешування-фото-telegram)
- [Важливі правила замовлення](#важливі-правила-замовлення)
- [Рекомендації для продакшну](#рекомендації-для-продакшну)

---

## Можливості

### Для користувача

- Перегляд каталогу десертів у Telegram Mini App.
- Системне сортування товарів за назвою.
- Сторінка деталей товару з фото, описом, ціною, порцією та відгуками.
- Додавання товарів у кошик.
- Керування кількістю товарів у кошику через `+`, `−` та видалення.
- Підтвердження перед видаленням товару з кошика.
- Промокод застосовується до замовлення цілком, а не до кожного товару окремо.
- Оформлення замовлення з полями:
  - імʼя;
  - телефон;
  - дата;
  - спосіб доставки;
  - спосіб оплати;
  - коментар.
- Валідація оформлення замовлення:
  - імʼя не може бути порожнім;
  - телефон повинен містити 9 цифр;
  - дата не може бути минулою або некоректною;
  - дата має враховувати мінімальний термін виконання;
  - доставка та оплата мають бути обрані.
- Вікно підтвердження перед створенням замовлення.
- Перегляд розділу **Мої замовлення**.
- Можливість ініціювати скасування замовлення через контактну інформацію.
- Контакти з клікабельним номером телефону.
- Відгуки про кондитерську та товари.
- Багатомовність: українська, російська, польська, англійська.
- Loading screen, skeleton-завантаження та lazy loading фото.

### Для адміністратора

- Адмін-панель у Telegram-боті.
- Перегляд активних замовлень.
- Перегляд усіх замовлень.
- Зміна статусів замовлень.
- Скасування замовлень зі статусом **Прийнято**.
- Автоматичне повідомлення адміністраторів про нове замовлення.
- Додавання продуктів.
- Видалення продуктів.
- Оновлення фото продукту.
- Створення та видалення промокодів.
- Перегляд відгуків.
- Оновлення перекладів продуктів.
- Очищення тестових даних без видалення каталогу продуктів.

---

## Структура проєкту

```text
Murchik_Cakes_Bot-MiniApp/
├── assets/                  # Зображення, схеми, службові медіафайли
├── backend/                 # FastAPI backend для Telegram Mini App
│   ├── __init__.py
│   └── main.py
├── data/                    # Локальна директорія для SQLite/Volume
├── database/                # Робота з базою даних
│   ├── cart_db.py
│   ├── custom_orders_db.py
│   ├── db.py
│   ├── favorites_db.py
│   ├── maintenance_db.py
│   ├── orders_db.py
│   ├── products_db.py
│   ├── promo_db.py
│   ├── reviews_db.py
│   └── user_settings_db.py
├── handlers/                # Telegram bot handlers
│   ├── add_product.py
│   ├── admin_orders.py
│   ├── admin_panel.py
│   ├── cart.py
│   ├── contacts.py
│   ├── custom_order.py
│   ├── delete_product.py
│   ├── favorites.py
│   ├── language.py
│   ├── my_orders.py
│   ├── products.py
│   ├── promo.py
│   ├── reviews.py
│   ├── start.py
│   └── update_photos.py
├── keyboards/               # Клавіатури Telegram-бота
│   └── main_menu.py
├── webapp/                  # Telegram Mini App frontend
│   ├── app.js
│   ├── index.html
│   ├── murchik-cat.jpg
│   └── styles.css
├── config.py                # Змінні середовища та admin config
├── locales.py               # Тексти інтерфейсу
├── main.py                  # Запуск Telegram-бота
├── requirements.txt         # Python-залежності
├── utils_dates.py           # Перевірка дат замовлення
├── utils_translation.py     # Переклади назв/описів товарів
├── Procfile                 # Railway worker для бота
├── Procfile.bot             # Railway worker для бота
└── Procfile.api             # Railway web service для FastAPI
```

---

## Технології

- **Python** — основна мова backend та Telegram-бота.
- **python-telegram-bot** — робота з Telegram Bot API.
- **FastAPI** — API для Telegram Mini App.
- **Uvicorn** — запуск FastAPI server.
- **SQLite** — локальна база за замовчуванням.
- **PostgreSQL** — підтримується через `DATABASE_URL`, зручно для Railway.
- **HTML/CSS/JavaScript** — frontend Telegram Mini App.
- **Railway** — рекомендований хостинг для 24/7 роботи.

---

## Змінні середовища

Створи `.env` локально або додай змінні у Railway.

```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=123456789,987654321
ADMIN_USERNAME=your_admin_username
WEBAPP_URL=https://your-miniapp-domain.up.railway.app
DATABASE_URL=postgresql://user:password@host:port/dbname
SQLITE_DB_PATH=/data/database.db
```

### Опис

| Змінна | Обовʼязкова | Опис |
|---|---:|---|
| `BOT_TOKEN` | Так | Токен Telegram-бота з BotFather |
| `ADMIN_IDS` | Так | Telegram ID адміністраторів через кому |
| `ADMIN_USERNAME` | Ні | Username адміністратора без `@` або з `@` |
| `WEBAPP_URL` | Так для Mini App | Публічний URL вебдодатку |
| `DATABASE_URL` | Ні | PostgreSQL URL, якщо використовується PostgreSQL |
| `SQLITE_DB_PATH` | Ні | Шлях до SQLite бази, за замовчуванням `/data/database.db` |

> Важливо: кожен адміністратор з `ADMIN_IDS` має хоча б один раз відкрити бота, інакше Telegram може не дозволити надіслати йому повідомлення.

---

## Локальний запуск

### 1. Клонувати репозиторій

```bash
git clone https://github.com/messerschmitt242-svg/Murchik_Cakes_Bot.git
cd Murchik_Cakes_Bot
git checkout MiniApp
```

### 2. Створити віртуальне середовище

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Встановити залежності

```bash
pip install -r requirements.txt
```

### 4. Створити `.env`

```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=123456789
ADMIN_USERNAME=your_username
WEBAPP_URL=http://localhost:8000
SQLITE_DB_PATH=./data/database.db
```

### 5. Запустити Telegram-бота

```bash
python main.py
```

---

## Запуск Mini App API

Mini App frontend розташований у папці `webapp/`, а API — у `backend/main.py`.

Локальний запуск:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Після запуску:

```text
http://localhost:8000
```

Health-check:

```text
http://localhost:8000/api/health
```

---

## Деплой на Railway

Для стабільної роботи краще створити **два Railway-сервіси** з одного репозиторію:

1. **Bot Worker** — запускає Telegram-бота.
2. **API Web Service** — запускає FastAPI + Mini App.

### Bot Worker

Start command:

```bash
python main.py
```

або використовуй:

```text
Procfile.bot
```

### API Web Service

Start command:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

або використовуй:

```text
Procfile.api
```

### Railway Variables

Додай в обидва сервіси:

```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=123456789,987654321
ADMIN_USERNAME=your_admin_username
WEBAPP_URL=https://your-api-service.up.railway.app
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### Volume для SQLite

Якщо використовується SQLite, потрібен Railway Volume:

```text
/data
```

Без Volume база може очищатися після redeploy.

Для продакшну рекомендовано PostgreSQL через `DATABASE_URL`.

---

## Налаштування Telegram Mini App

### 1. Створити бота

У BotFather:

```text
/newbot
```

Отримай `BOT_TOKEN`.

### 2. Привʼязати Web App URL

У BotFather використовуй налаштування Menu Button або Web App:

```text
/setmenubutton
```

Вкажи URL API-сервісу Railway, наприклад:

```text
https://your-api-service.up.railway.app
```

### 3. Команди бота

Рекомендований список команд:

```text
start - Запуск бота
admin - Адмін-панель
id - Показати мій Telegram ID
```

---

## Адміністрування

### Як отримати Telegram ID

Напиши боту:

```text
/id
```

Додай отриманий ID у `ADMIN_IDS`.

### Адмін-панель

У головному меню бота для адміністратора залишається кнопка:

```text
🛠 Адмін-панель
```

Через неї доступні:

- активні замовлення;
- усі замовлення;
- додавання продукту;
- видалення продукту;
- оновлення фото продукту;
- промокоди;
- відгуки;
- оновлення перекладів;
- очищення тестових даних.

### Статуси замовлення

Основні статуси:

1. `Прийнято`
2. `Готується`
3. `Готове до видачі`
4. `Завершено`
5. `Скасовано`

Якщо замовлення має статус `Прийнято`, адміністратор може скасувати його з адмін-панелі.

---

## База даних

Проєкт підтримує SQLite та PostgreSQL.

### SQLite

За замовчуванням використовується:

```text
/data/database.db
```

Для локального запуску можна задати:

```env
SQLITE_DB_PATH=./data/database.db
```

### PostgreSQL

Якщо задано `DATABASE_URL`, проєкт працює з PostgreSQL.

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
```

Основні таблиці:

- `products` — каталог продуктів;
- `cart` — кошики користувачів;
- `orders` — звичайні замовлення;
- `custom_orders` — індивідуальні замовлення;
- `promo_codes` — промокоди;
- `favorites` — обране;
- `reviews` — відгуки;
- `user_settings` — мова користувача.

---

## Кешування фото Telegram

Telegram `file_id` не є прямим публічним URL для браузера. Тому Mini App використовує endpoint:

```text
/api/telegram-photo?file_id=...
```

Backend:

- отримує `file_path` через Telegram Bot API;
- завантажує файл;
- кешує `file_id -> file_path`;
- кешує байти зображення;
- віддає браузеру зображення з `Cache-Control` headers.

Це зменшує кількість запитів до Telegram і прискорює Mini App, особливо після зміни мови або повторного відкриття каталогу.

---

## Важливі правила замовлення

- Мінімальний строк виконання — **4 дні**.
- Дата замовлення не може бути минулою.
- Телефон має містити **9 цифр**.
- Доставка та оплата мають бути вибрані.
- Перед створенням замовлення користувач бачить підтвердження з підсумком.
- Доступні способи доставки:
  - `Самовивіз`
  - `Кур'єр Glovo (дорого)`
- Доступні способи оплати:
  - `Готівкою`
  - `Переказ BLIK`

---

## Промокоди

Промокод застосовується до всього замовлення.

Приклад:

```text
Товари: 180.00 zł
Промокод: -10%
Знижка: 18.00 zł
Разом: 162.00 zł
```

Адміністратор може створювати та видаляти промокоди через адмін-панель.

---

## Відгуки

Підтримуються два типи відгуків:

- відгук про кондитерську;
- відгук про конкретний продукт.

Відгуки по товарах використовуються для рейтингу в каталозі.

---

## Переклади

Підтримувані мови:

- Українська;
- Русский;
- Polski;
- English.

Назви та описи товарів можуть автоматично адаптуватися через `utils_translation.py`.

Мова зберігається окремо для кожного користувача у таблиці `user_settings`.

---

## API endpoints

Основні endpoint-и Mini App:

```text
GET    /api/health
GET    /api/bootstrap/{user_id}
GET    /api/order-rules
GET    /api/categories
GET    /api/products
GET    /api/products/{product_id}
GET    /api/telegram-photo
GET    /api/cart/{user_id}
POST   /api/cart/add
POST   /api/cart/qty
DELETE /api/cart/{user_id}/{product_id}
POST   /api/cart/promo
POST   /api/orders
GET    /api/orders/{user_id}
POST   /api/custom-orders
GET    /api/favorites/{user_id}
POST   /api/favorites/toggle
GET    /api/reviews
GET    /api/reviews/product/{product_id}
POST   /api/reviews
GET    /api/language/{user_id}
POST   /api/language
```

---

## Очищення тестових даних

Адмін-функція очищає тестові дані, але залишає каталог продуктів.

Очищується:

- кошики;
- замовлення;
- індивідуальні замовлення;
- відгуки;
- обране;
- промокоди.

Не очищується:

- каталог продуктів;
- фото продуктів.

---

## Рекомендації для продакшну

- Використовувати PostgreSQL замість SQLite для продакшну.
- Не запускати одночасно локальний бот і Railway worker з одним токеном.
- Регулярно робити backup бази даних.
- Перевірити коректність `ADMIN_IDS` перед запуском.
- Переконатися, що всі адміністратори відкрили бота хоча б один раз.
- Використовувати окремий Railway service для API та окремий worker для бота.
- Не зберігати `.env` у GitHub.
- Перед великими змінами робити backup бази.

---

## Типові проблеми

### Адміну не приходить повідомлення про нове замовлення

Перевір:

1. `ADMIN_IDS` містить правильний Telegram ID.
2. Адмін хоча б один раз відкрив бота.
3. `BOT_TOKEN` однаковий у bot worker та API service.
4. API service має доступ до інтернету.
5. У Railway logs немає `ADMIN NOTIFY ERROR`.

### Фото довго завантажуються

Перевір:

1. Чи заданий `BOT_TOKEN` в API service.
2. Чи працює endpoint `/api/telegram-photo`.
3. Чи не очищається кеш після кожного redeploy.
4. Чи фото були завантажені саме через цього бота.

### Telegram показує Conflict error

Не запускай одночасно два процеси бота з одним токеном:

```text
Conflict: terminated by other getUpdates request
```

Зупини локальний запуск, якщо бот уже працює на Railway.

---

## Автор

Проєкт: **Murchik Cakes Bot**

GitHub: `messerschmitt242-svg/Murchik_Cakes_Bot`

---

## Статус

Проєкт готовий до тестування та подальшого розвитку:

- PostgreSQL migration;
- більш глибока аналітика замовлень;
- автоматичні нагадування клієнтам;
- реактивація клієнтів;
- інтеграція з платіжним провайдером;
- розширення Mini App.
