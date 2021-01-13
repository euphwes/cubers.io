web: gunicorn app:app --log-file=-
worker: huey_consumer.py app.huey -k thread -w 4