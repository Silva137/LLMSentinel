python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py load_data
python manage.py runserver 0.0.0.0:8000