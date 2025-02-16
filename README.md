<h1 align="center"> Booking </h1>
<p align="center" markdown=1>
   Сделано с ❤️ от <a href="https://github.com/al1enn">AL1EN</a>
</p>

## Выпуск пары ключей RSA (приватный + публичный)

```shell
mkdir -p ./src/certs
```
#### Генерируем приватный RSA ключ размером 2048 бит

```shell
openssl genrsa -out ./src/certs/jwt-private.pem 2048
```
#### Извлекаем публичный ключ из пары ключей
```shell
openssl rsa -in ./src/certs/jwt-private.pem -outform PEM -pubout -out ./src/certs/jwt-public.pem
```
## Запуск с Docker Compose

```sh
make build
```
Затем
```sh
make start
```
## Создание Суперпользователя

Суперюзер создастся при запуске docker. Также можно создать вручную
```sh
cd src
python -m scripts.create_first_superuser
```

## Миграции Базы Данных

> Чтобы создать таблицы, если вы не создали эндпоинты, убедитесь, что вы импортировали модели в src/app/models/__init__.py. Этот шаг важен для создания новых таблиц.

Если вы используете db в docker, вам нужно изменить это в `docker-compose.yml` для запуска миграций:

```sh
  db:
    image: postgres:13
    env_file:
      - ./src/.env
    volumes:
      - postgres-data:/var/lib/postgresql/data
    # -------- замените на комментарий для запуска миграций с docker --------
    expose:
      - "5432"
    # ports:
    #  - 5432:5432
```

Получая:

```sh
  db:
    ...
    # expose:
    #  - "5432"
    ports:
      - 5432:5432
```

Находясь в папке `src`, запустите миграции Alembic:

```sh
poetry run alembic revision --autogenerate
```

И чтобы применить миграцию:

```sh
poetry run alembic upgrade head
```


## Запуск ARQ Worker

Если вы используете `docker compose`, воркер уже запущен.
Вручную запустить можно так:

```sh
cd src
poetry run arq app.core.worker.settings.WorkerSettings
```