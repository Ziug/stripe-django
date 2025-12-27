# Django + Stripe Payment System

Проект включает в себя базовый функционал покупки товаров, а также реализацию **Корзины (Order)**, **Скидок/Налогов**, **Мультивалютности** и оплаты через **Payment Intent**.



## Функционал


-  **API:** `GET /buy/{id}` — получение Session ID.
-  **Frontend:** `GET /item/{id}` — страница товара с кнопкой покупки.
-  **Модель Item:** Поля (name, description, price).
- **Docker:** Наличие `Dockerfile` и `docker-compose.yml`.
- **Environment Variables:** Ключи конфигурации вынесены в `.env`.
- **Django Admin:** Удобное управление моделями.
- **Модель Order:** Объединение нескольких товаров в один заказ.
- **Скидки и Налоги:** Модели `Discount` и `Tax`, привязка к заказу, динамическое создание купонов в Stripe.
- **Мультивалютность:** Поддержка `USD` и `EUR` с автоматическим выбором Stripe API Keypair.
- **Payment Intent:** Реализация оплаты без редиректа на сайт Stripe (Custom Form).



## ⚙️ Предварительная настройка

**Важно:** Перед запуском необходимо создать файл `.env` в корне проекта (рядом с `manage.py`) и заполнить его вашими ключами.

Пример содержимого `.env`:

```env
# Django settings.py
DEBUG=True
ALLOWED_HOSTS=['*']

# Stripe Keys (USD)
pk_usd=pk_test_...ващ_публичный_ключ_usd...
sk_usd=sk_test_...ваш_секретный_ключ_usd...

# Stripe Keys (EUR)
# Если у вас один аккаунт, продублируйте ключи USD.
# Для корректной работы EUR товаров нужны ключи от аккаунта с поддержкой EUR.
pk_eur=pk_test_...
sk_eur=sk_test_...
```
## Запуск

### Через Docker
Если у вас установлен Docker, запуск выполняется одной командой.

Запустите проект:
```Bash
docker-compose up --build
```
Подготовьте базу данных (в новом окне терминала):

```Bash
### Применяем миграции

docker-compose exec web python manage.py migrate


### Создаем суперпользователя (для доступа в админку)

docker-compose exec web python manage.py createsuperuser

Проект доступен по адресу: http://127.0.0.1:8000/
```
## Ручной запуск через python 
Создайте и активируйте виртуальное окружение:

```Bash
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```
Установите зависимости:
```Bash
pip install -r requirements.txt
```
Подготовьте базу данных:
```Bash
python manage.py migrate
python manage.py createsuperuser
```
Запустите сервер:
```Bash
python manage.py runserver
```
## Инструкция по использованию 
После запуска сервера выполните следующие шаги для проверки функционала:

### 1. Наполнение данными
Для создания тестовых товаров можно перейти по http://127.0.0.1:8000/testing_adding  <br /> 
Для создания скидок и налогов
 - Перейдите в админ паенль: http://127.0.0.1:8000/admin/
 - Создайте объекты Discount (например, 20%) и Tax (например, 13%).
### 2. Сценарии оплаты

Покупка через jlyjuj njdfhf
 - URL: http://127.0.0.1:8000/buy_intent/{id}/
 - Оплата происходит прямо на странице вашего сайта через форму Stripe Elements.

Покупка корзины товаров
 - На странице товара нажмите Add to Order.
 - Добавьте несколько товаров.
 - Перейдите в корзину (вас перекинет автоматически или через URL /order/{id}/).
 - В форме внизу введите ID созданных ранее скидки и налога, нажмите Apply.
 - Нажмите Pay for Order для оплаты всей суммы одним платежом.

## Стек
Python 3.12 <br />
Django 6 <br />
Stripe API <br />
Docker & Docker Compose