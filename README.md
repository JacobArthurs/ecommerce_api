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

- Grant permissions for testing:

  ```bash
  docker exec -it ecommerce-mysql mysql -u root -p

  GRANT ALL PRIVILEGES ON test_ecommerce.* TO 'user'@'%' WITH GRANT OPTION; FLUSH PRIVILEGES;
  ```

- Run tests:

  ```bash
  docker compose exec django-app python manage.py test
  ```
