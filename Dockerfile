
FROM python:3.6

WORKDIR /app

COPY . ./app/

RUN pip install -r requirements.txt


EXPOSE 55555


CMD ["python", "myapp.py"]
