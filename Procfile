web: gunicorn cubersio:app --log-file=-
worker: huey_consumer.py cubersio.huey -k thread -w 4