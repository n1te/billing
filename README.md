# Simple billing app

**build and launch:**

`docker-compose up -d --build`

**run migrations:**

`docker-compose exec web python manage.py migrate --noinput`

**run tests:**

`docker-compose exec web pytest`