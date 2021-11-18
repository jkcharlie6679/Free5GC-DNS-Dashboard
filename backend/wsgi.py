from app import app

# gunicorn -w 2 -t 2 -b 0.0.0.0:8080 wsgi:app --daemon