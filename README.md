# Foodgram - «Продуктовый помощник»

## Описание проекта
Foodgram — кулинарная платформа, где пользователи могут делиться своими рецептами, сохранять понравившиеся рецепты других авторов в избранное и следить за обновлениями интересных кулинаров. Для зарегистрированных пользователей доступен удобный сервис "Список покупок", который автоматически формирует перечень необходимых ингредиентов для приготовления выбранных блюд.

## Технологический стек
- Backend: Django, Django REST Framework
- Frontend: React
- База данных: PostgreSQL
- Веб-сервер: Nginx
- Контейнеризация: Docker
- Деплой: Docker Compose

## Предварительные требования
- Установленный Docker
- Установленный Docker Compose


## Настройка окружения (.env)
Перед запуском проекта необходимо создать файл .env в папке infra со следующими переменными:

### Настройки базы данных PostgreSQL
POSTGRES_USER=foodgram_user             # Имя пользователя БД (можно оставить по умолчанию)
POSTGRES_PASSWORD=your_strong_password  # Пароль (обязательно замените на свой)
POSTGRES_DB=foodgram                    # Название базы данных

### Настройки подключения Django
POSTGRES_DB_HOST=db                     # Хост БД (не менять для Docker)
POSTGRES_DB_PORT=5432                   # Порт БД (стандартный для PostgreSQL)
SECRET_KEY=your_secret_key_here         # Секретный ключ Django

### Параметры безопасности
#### Режим разработки (1 - включен, 0 - выключен)
DEBUG=0

#### Разрешенные хосты 
ALLOWED_HOSTS=localhost,127.0.0.1

#### Доверенные источники CSRF 
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1

## Инструкция по развертыванию
Сначала нужно перейти в папку infra в проекте. Затем выполнить команду поднятия docker контейнеров:
**docker compose up -d**

Проверить что все контейнеры работают:
**docker ps** (их должно быть 4)


Потом выполнить следующие команды:

**1) собираем статику проекта** -
   docker compose exec backend_foodgram python manage.py collectstatic
   
**2) статиcку из контейнера backend_foodgram копируем в том backend_static** -
   docker compose exec backend_foodgram cp -r /app/collected_static/. /backend_static/static/

**3) применяем миграции к проекту** -
   docker compose exec backend_foodgram python manage.py migrate

**4) загружаем данные ингредиентов в базу данных** -
   docker compose exec backend_foodgram python manage.py load_data

## Примеры API-запросов
### 1. Получение списка рецептов
GET http://localhost/api/recipes/

#### Ответ
{
  "count": 42,
  "next": "http://localhost/api/recipes/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Паста Карбонара",
      "image": "/media/recipes/images/carbonara.jpg",
      "cooking_time": 15,
      "author": {
        "id": 1,
        "username": "chef_italiano",
        "first_name": "Марио",
        "last_name": "Росси"
      }
    },
    {
      "id": 2,
      "name": "Тирамису",
      "image": "/media/recipes/images/tiramisu.jpg",
      "cooking_time": 120,
      "author": {
        "id": 2,
        "username": "dessert_master",
        "first_name": "Анна",
        "last_name": "Петрова"
      }
    }
  ]
}

### 2. Добавление рецепта в избранное (POST)
POST http://localhost/api/recipes/1/favorite/
Headers:
  Authorization: Bearer ваш_токен

#### Ответ
{
  "id": 1,
  "name": "Паста Карбонара",
  "image": "/media/recipes/images/carbonara.jpg",
  "cooking_time": 15
}

### 3. Регистрация пользователя (POST)
POST http://localhost/api/users/
Body:
{
  "email": "newuser@example.com",
  "username": "newuser",
  "first_name": "Алексей",
  "last_name": "Смирнов",
  "password": "strongpassword123"
}

#### Ответ
{
  "email": "newuser@example.com",
  "id": 4,
  "username": "newuser",
  "first_name": "Алексей",
  "last_name": "Смирнов"
}

### 4. GET http://localhost/api/recipes/download_shopping_cart/
Headers:
  Authorization: Bearer ваш_токен

#### Ответ
Список покупок:

1. Мука - 500 г
2. Яйца - 3 шт
3. Сахар - 200 г
4. Молоко - 1 л
...

## Cоздание администратора
docker compose exec backend_foodgram python manage.py createsuperuser

вводим данные для администратора они будут использоваться для входа в админ-панел  по адресу:
http://localhost/admin

Теперь можно открыть проект по адресу в браузере:
http://localhost

Чтобы ознакомиться с API нужно перейти по ссылке:
http://localhost/api/docs/

## Автор
Янкина Ксения - yankina-k06@bk.ru
Git - https://github.com/alexyyyzsm
