setup:
	curl https://pyenv.run | bash
	pyenv install 3.10
	pyenv local 3.10
	python -m pip install poetry
	python -m poetry install
	sudo apt install nginx

poetry:
	python -m poetry ${command}

install-dependencies:
	make poetry command=install

add:
	make poetry command="add ${dependency}"

poetry-run:
	make poetry command="run ${command}"

manage:
	make poetry-run command="python music_tracker/manage.py ${command}"

statics:
	make manage command=collectstatic

runserver:
	make manage command=runserver

superuser:
	make manage command=createsuperuser

env:
	echo "run bash env.sh"

pre-commit:
	make poetry-run command="pre-commit"

conf:
	# Run make env first
	envsubst < music_tracker/music_tracker_nginx.conf > /etc/nginx/sites-available/music_tracker_nginx.conf

conf-symlink:
	sudo ln -s /etc/nginx/sites-available/music_tracker_nginx.conf /etc/nginx/sites-enabled/

uwsgi:
	make poetry-run command="uwsgi --socket :${DJANGO_PORT} --chdir music_tracker/ --module music_tracker.wsgi &"

start:
	service nginx restart
	make uwsgi

find-uwsgi:
	ps -u root | grep uwsgi

.PHONY: setup, poetry, install-dependencies, add, manage, statics, runserver, superuser, env, conf, uwsgi, start
