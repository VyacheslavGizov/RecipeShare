## Описание проекта:
Данное приложение особенно будет интересно кошатникам и позволяет пользователям делиться достижениями
своего питомца с такими же котолюбами. Приложение предоставляет интерфейс для выполнения следующих операций:
- Регистрация новых и аутентификация зарегистрированных пользователей;
- Аутентифицированным пользователям проект позволяет добавлять новых питомцев на сайт;
- Информацию о собственных котах можно изменить или вовсе удалить с сайта;
- А на чужих котов можно только смотреть.
Для каждого нового котика нужно обязательно указать его имя, год рождения и выбрать цвет. Опционально можно загрузить фотографию
своего питомца, для котиков без фотографии будет выводиться изображение по умолчанию.Для каждого котика можно указать
его достижения — одно или сразу несколько. Их можно выбрать из уже доступных. Для быстрого поиска достижений можно воспользоваться
поисковой строкой. Если нужного достижения не найдётся в списке, то его тут же можно туда добавить.

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
Для того, чтобы развернуть проект на ubuntu необходимо:
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

DB_HOST=db  # Адрес, по которому Django будет соединяться с БД. В данном случае имя еонтейнера с БД.
DB_PORT=5432  # Порт, по которому Django будет обращаться к базе данных

USE_SQLITE=False  # Если True, то будет использована БД salite

SECRET_KEY=<секретный_ключ_Django>
DEBUG=False  # Для отладки True
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
#        proxy_pass http://127.0.0.1:9000;  # WSGI-сервер на слушает порт 9000
#
#    }
#}
sudo nginx -t  # Проверка корректности настроек
sudo systemctl start nginx  # Запуск nginx
```
- Разместить в директории проекта файл docker-compose.production.yml и выполнить:
```
sudo docker compose -f docker-compose.production.yml up -d  # Запуск контейнеров
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate  # Миграции
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic  # Сбор статики
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/  # Перемещение статики
```
- Или с использованием workflow main.yml выполнив push в ветку main.

## Авторы:
- [ЯП](https://github.com/yandex-praktikum);
- [Vyacheslav Gizov(Backend)](https://github.com/VyacheslavGizov).