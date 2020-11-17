#!/bin/sh

python manage.py reset_db --noinput -c
rm interact/migrations/* -rf
python manage.py migrate
python manage.py makemigrations interact
python manage.py migrate interact
