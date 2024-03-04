# Пулим изменения
pull:
	git pull

# Рестартим контейнер (не перезапускаем)
restart:
	docker compose restart

# Запускаем контейнер
up:
	docker compose up -d

# Останавливаем контейнер
down:
	docker compose down

# Перезапускаем контейнер
redeploy: down up

# Пулим изменения, перезапускаем контейнер
update: pull static restart

# Собираем статику
static:
	docker compose run faceswap python manage.py collectstatic --no-input
	sudo chown www-data:www-data -R faceswap/media
	sudo chown www-data:www-data -R faceswap/static
	sudo chmod o+r faceswap/media faceswap/static  

# Создаем суперпользователя
superuser:
	docker compose run faceswap python manage.py createsuperuser

# Активируем виртуальное окружение
venv:
	source .venv/bin/activate

# Собираем контейнер
build:
	docker compose build
