[![Main Foodgram workflow](https://github.com/VyacheslavGizov/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/VyacheslavGizov/foodgram/actions/workflows/main.yml)

## Описание проекта:

Проект «Фудграм» (foodgram-project.hopto.org) — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
Проект состоит из следующих страниц: 
- главная: содержит первые шесть рецептов, отсортированные по дате, остальные рецепты доступны на следующих страницах;
- страница входа,
- страница регистрации,
- страница рецепта: содержит полное описание рецепта, залогиненные пользователи могут добавить рецепт в избранное список покупок, подписаться на автора рецепта.
- страница пользователя: содержит имя пользователя, все рецепты опубликованные пользователем и кнопку для  подписки/отписки от него;
- страница подписок: доступна только владельцу аккаунта и содержит перечисление авторов, на которых подписан пользователь.
- избранное: добавлять рецепты в избранное может только залогиненный пользователь.
- список покупок: доступен только залогинненым пользователям.
- создание и редактирование рецепта: доступна только залогинненым пользователям, все поля обязательны для заполнения
- страница смены пароля.

Добавить новые теги и ингредиенты может только администратор через админку: foodgram-project.hopto.org/admin

## Ссылки:
- [Проект «Фудграм»](foodgram-project.hopto.org)
- [Документация к API «Фудграм»](https://foodgram-project.hopto.org/api/docs/)

## Стек:
- Django REST
- Docker
- Gunicorn
- JS
- Nginx
- Node.js
- PostgreSQL
- Python 3.9

## Как запустить проект:
### Для того, чтобы развернуть проект на ubuntu, необходимо:
- Установить на сервер Docker и Docker Compose:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin;
```
- В директории проекта создать файл .env с переменными окружения:
```
# Содержимое .env
POSTGRES_DB=<имя_базы_данных>
POSTGRES_USER=<имя_пользователя_базы_данных>
POSTGRES_PASSWORD=<пароль_пользователя_базы_данных>

DB_HOST=db  # Адрес, по которому Django будет соединяться с БД. В данном случае имя контейнера с БД.
DB_PORT=5432  # Порт, по которому Django будет обращаться к БД.

USE_SQLITE=False  # Если True, то будет использована БД sqlite.

SECRET_KEY=<секретный_ключ_Django>
DEBUG=False  # Для отладки True.
ALLOWED_HOSTS=<IP_и/или_доменное имя>
```
- Установить и настроить NGINX:
```
sudo apt install nginx -y
sudo systemctl start nginx
sudo ufw allow 'Nginx Full'  # Настройка firewall
sudo ufw allow OpenSSH
sudo ufw enable  # Включить firewall
# В конфигурационном файле NGINX
sudo nano /etc/nginx/sites-enabled/default
# Указать
#server {
#    listen 80;
#    server_name <доменное_имя>
#    
#    location / {
#        proxy_set_header HOST $host;
#        proxy_pass http://127.0.0.1:9090;  # WSGI-сервер слушает порт 9090
#
#    }
#}
sudo nginx -t  # Проверка корректности настроек. 
sudo systemctl start nginx  # Запуск nginx.
```
- Для запуска контенеров: разместить в директории проекта файл docker-compose.production.yml и выполнить:
```
sudo docker compose -f docker-compose.production.yml up -d  # Запуск контейнеров.
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate  # Миграции.
python manage.py loaddata initial_data.json  # Загрузить ингредиенты, теги и данные администратора в БД.
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic  # Сбор статики.
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/  # Перемещение статики.
```
- Или с использованием workflow main.yml выполнить push в ветку main.

### Для того, чтобы развернуть проект локально, необходимо:
- Установить Node.js версии v21.7.3 c [официального сайта](https://nodejs.org/en/about/previous-releases#looking-for-latest-release-of-a-version-branch), установить зависимости в директории фронтенда и запустить:
```
cd frontend/
npm i 
npm run start 
```
- В другом терминале в виртуальное окружение для бекенда установить django-cors-header:
```
pip install django-cors-headers 
```
- Подключить его в settings.py как приложение:
```
INSTALLED_APPS = [
    ...
    'rest_framework',
    'corsheaders',
    ...
]
```
- В списке MIDDLEWARE зарегистрировать CorsMiddleware выше CommonMiddleware:
```
MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]
```
- Добавить в settings.py 
```
CORS_URLS_REGEX = r'^/api/.*$' 
CORS_ALLOWED_ORIGINS = ['http://localhost:3000',] 
```
- Запустить отладочный веб-сервер:
```
python manage.py runserver
```

## Авторы:
- [ЯП](https://github.com/yandex-praktikum);
- [Vyacheslav Gizov(Backend)](https://github.com/VyacheslavGizov).