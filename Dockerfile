FROM python:3.9

# Установка CMake
RUN apt-get update && apt-get -y upgrade
RUN python -m pip install --upgrade pip

WORKDIR /vympel.music

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "app.py" ]
