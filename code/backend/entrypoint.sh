python manage.py makemigrations --no-input
python manage.py migrate --no-input
#python manage.py sync_llm_models  comentado para evitar apagar modelos que fazer parte da avaliacao experimental.
python manage.py load_datasets
python manage.py runserver 0.0.0.0:8000