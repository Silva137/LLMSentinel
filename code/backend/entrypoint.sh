#!/bin-sh

echo "A aplicar as migrações da base de dados..."
python manage.py makemigrations --no-input   # nao usar em produção, fazer migracoes manualmente
python manage.py migrate --no-input


echo "A carregar os dados iniciais..."
python manage.py load_datasets
#python manage.py sync_llm_models  comentado para evitar apagar modelos que fazer parte da avaliacao experimental.


PORT="${PORT:-8000}"
WORKERS="${WEB_CONCURRENCY:-3}"
THREADS="${GUNICORN_THREADS:-2}"
TIMEOUT="${GUNICORN_TIMEOUT:-300}"

echo "🚀 A iniciar o Gunicorn em 0.0.0.0:${PORT} ..."
#python manage.py runserver 0.0.0.0:8000
exec gunicorn backend.wsgi:application \
  --bind 0.0.0.0:${PORT} \
  --workers ${WORKERS} \
  --threads ${THREADS} \
  --timeout ${TIMEOUT}