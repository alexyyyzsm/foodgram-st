Перейти в папку infra в проекте. 
Выполнить команду поднятия docker контейнеров:
docker compose up -d

Проверить что все контейнеры работают:
docker ps

Потом выполнить следующие команды:
# собираем статику проекта
docker compose exec backend_foodgram python manage.py collectstatic
# статику из контейнера backend_foodgram копируем в том backend_static
docker compose exec backend_foodgram cp -r /app/collected_static/. /backend_static/static/
# применяем миграции к проекту
docker compose exec backend_foodgram python manage.py migrate

# загружаем данные ингредиентов в базу данных
docker compose exec backend_foodgram python manage.py load_data

# создание администратора
docker compose exec backend_foodgram python manage.py createsuperuser

вводим данные для администратора они будут использоваться для входа в админ-панел  по адресу:
http://localhost/admin

Теперь можно открыть проект по адресу в браузере:
http://localhost

Чтобы ознакомиться с API нужно перейти по ссылке:
http://localhost/api/docs/

