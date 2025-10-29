setup:
	curl -LsSf https://astral.sh/uv/install.sh | sh
	uv python install 3.12
	uv sync
	sudo apt install nginx

sync:
	uv sync

install-dependencies:
	uv sync

install-python:
	uv python install 3.12

add:
	uv add ${dependency}

uv-run:
	uv run ${command}

manage:
	make uv-run command="python music_tracker/manage.py ${command}"

statics:
	make manage command=collectstatic

runserver:
	make manage command=runserver

superuser:
	make manage command=createsuperuser

makemigrations:
	make manage command=makemigrations

migrate:
	make manage command=migrate

env:
	echo "run bash env.sh"

pre-commit:
	make uv-run command="pre-commit"

conf:
	# Run make env first
	envsubst < music_tracker/music_tracker_nginx.conf > /etc/nginx/sites-available/music_tracker_nginx.conf

conf-symlink:
	sudo ln -s /etc/nginx/sites-available/music_tracker_nginx.conf /etc/nginx/sites-enabled/

uwsgi:
	make uv-run command="uwsgi --socket :${DJANGO_PORT} --chdir music_tracker/ --module music_tracker.wsgi &"

start:
	service nginx restart
	make uwsgi

find-uwsgi:
	ps -u root | grep uwsgi

.PHONY: setup, sync, install-dependencies, install-python, add, manage, statics, runserver, superuser, env, pre-commit, conf, conf-symlink, uwsgi, start, find-uwsgi
