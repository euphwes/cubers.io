FROM python:3.9.13-alpine3.16

WORKDIR /app
COPY . .

RUN apk add npm gcc musl-dev libpq-dev zlib-dev jpeg-dev
RUN npm install -g yarn less

RUN pip install -r requirements.txt

CMD ["flask", "run", "--host=0.0.0.0"]