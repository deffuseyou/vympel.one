FROM ubuntu:latest
LABEL authors="deffuseyou"

# Используйте официальный образ Python как базовый
FROM python:3.11

# Устанавливаем необходимые пакеты и генерируем локаль
RUN apt-get update && apt-get install -y locales && \
    sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

# Установите переменные окружения для локалей
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU:ru
ENV LC_ALL ru_RU.UTF-8

# Установите рабочую директорию в контейнере
WORKDIR /app

# Скопируйте файлы проекта в рабочую директорию
COPY . /app

# Установите необходимые библиотеки из файла requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Запустите приложение Python при запуске контейнера
CMD ["python", "./app.py"]
