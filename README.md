# Guess Chan
To set up the project:
```
docker compose build
docker compose up
```
And navigate to http://127.0.0.1:8000/

For local debug start only `postgres` service from docker-compose.yml and
run django server locally:
```
python manage.py setup
python manage.py runserver
```
