#!/usr/bin/env bash

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='smilexah').exists():
    User.objects.create_superuser('smilexah', 'smilexah@example.com', 'admin123')
EOF
python -m gunicorn --bind 0.0.0.0:8000 --workers 3 sxodimsdu.wsgi:application
