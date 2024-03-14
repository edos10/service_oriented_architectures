# Main service

В этой директории находится главный сервис, он же main.

Как запускать сервис:

1) сначала поднимаем БД в папке dev/database-dev командой 
```bash
docker-compose build
docker-compose up
```
2) затем то же самое в папке sev/services-dev
```bash
docker-compose build
docker-compose up
```
3) и наконец заходим в папку mainservice и делаем миграции:
```bash
docker run --rm --network="socnet-network" -v "$(pwd)/migrations":/app liquibase/liquibase:4.19.0 --defaultsFile=/app/dev.properties update
```

Теперь сервис можно дергать по localhost:5000 

:)
