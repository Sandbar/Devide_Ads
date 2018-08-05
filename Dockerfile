
FROM python:3.6-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt


EXPOSE 55555


CMD ["python", "my_app.py"]
