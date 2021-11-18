from app import app

# gunicorn --workers=2 --threads=2 --bind 0.0.0.0:8080 wsgi:app --daemon