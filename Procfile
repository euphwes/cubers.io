web: gunicorn app:CUBERS_APP --log-file=-
worker: huey_consumer.py app.huey -k thread -w 4