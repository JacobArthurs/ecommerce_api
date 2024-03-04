# Ecommerce API

- Compose up:

  ```bash
  docker compose up -d --build
  ```

- Compose down:

  ```bash
  docker compose down
  ```

- Make migrations:

  ```bash
  docker compose exec django-app python manage.py makemigrations
  ```

- Migrate:

  ```bash
  docker compose exec django-app python manage.py migrate
  ```

- Create superuser:

  ```bash
  docker compose exec django-app python manage.py createsuperuser
  ```
