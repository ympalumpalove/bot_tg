FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y python3-venv && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv venv

RUN . /app/venv/bin/activate && pip install --upgrade pip && pip install telebot pandas openpyxl requests

CMD ["sh", "-c", ". /app/venv/bin/activate && python main_test.py"]
