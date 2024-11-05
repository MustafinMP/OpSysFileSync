FROM ubuntu:latest
LABEL authors="musta"

FROM python:3.12

# установка рабочей директории в контейнере
WORKDIR /code

# копирование файла зависимостей в рабочую директорию
COPY requirements.txt .

# установка зависимостей
RUN pip install -r requirements.txt

# копирование содержимого локальной директории src в рабочую директорию
COPY src/ .

CMD [ "python", "./main.py" ]