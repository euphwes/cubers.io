web: gunicorn app:app --log-file=-
worker: huey_consumer.py app.huey -k process -w 8