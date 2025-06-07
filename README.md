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
