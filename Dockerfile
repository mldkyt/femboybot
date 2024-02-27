FROM python:3.11-alpine
WORKDIR /app
COPY features /app/features
COPY utils /app/utils
COPY database.py /app
COPY main.py /app/
COPY config.json /app/
COPY requirements.txt /app/

RUN pip install -r /app/requirements.txt

CMD ["python", "/app/main.py"]