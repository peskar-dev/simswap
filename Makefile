update:
	git pull
	docker compose up -d

run:
	docker compose up -d

static:
	docker compose run faceswap python manage.py collectstatic --no-input
	sudo chown www-data:www-data -R faceswap/media
	sudo chown www-data:www-data -R faceswap/static
	sudo chmod o+r faceswap/media faceswap/static  

venv:
	source .venv/bin/activate
