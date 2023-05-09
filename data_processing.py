import yaml
import paramiko
import socket
import os
import sqlite3
# from speechkit import Session, SpeechSynthesis
from sqlighter import SQLighter


def config_read():
    config = yaml.load(open('config.yml'), Loader=yaml.SafeLoader)
    return config


def is_connected():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False


# def message_read(message):
#     oauth_token = "AQAAAAAsHJkgAAhjwXshft5QgUuRkX0Wubhjlk"
#     catalog_id = "b1gd129pp9ha0vnvf5g7"
#
#     # Экземпляр класса `Session` можно получать из разных данных
#     session = Session.from_yandex_passport_oauth_token(oauth_token, catalog_id)
#
#     # Создаем экземпляр класса `SpeechSynthesis`, передавая `session`,
#     # который уже содержит нужный нам IAM-токен
#     # и другие необходимые для API реквизиты для входа
#     synthesizeAudio = SpeechSynthesis(session)
#
#     # Метод `.synthesize()` позволяет синтезировать речь и сохранять ее в файл
#     synthesizeAudio.synthesize(
#         'out.wav', text='Привет мир!',
#         voice='oksana', format='lpcm', sampleRateHertz='16000'
#     )
#
#     # `.synthesize_stream()` возвращает объект типа `io.BytesIO()` с аудиофайлом
#     audio_data = synthesizeAudio.synthesize_stream(
#         text='Привет мир, снова!',
#         voice='oksana', format='lpcm', sampleRateHertz='16000'
#     )


def parse_music_folder():
    db = SQLighter(database='vympel.one',
                   user='postgres',
                   password=os.environ['admin_password'],
                   host='192.168.0.100',
                   port=5432)

    path = fr'{config_read()["music-path"]}'
    songs = next(os.walk(path), (None, None, []))[2]

    for song in songs:
        try:
            db.add_song(song.replace('.mp3', ''))
            print(f'Песня "{song.replace(".mp3", "")}" добавлена')
        except sqlite3.IntegrityError:
            pass


def add_ip(ip_address):
    config = config_read()
    # Подключение к удаленному серверу
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=config['router']['ip'],
                       username=config['router']['user'],
                       password=config['router']['password'])

    # Открытие файла для дозаписи
    sftp_client = ssh_client.open_sftp()
    with sftp_client.open(config['whitelist-path'], 'a+') as file:
        # Запись данных в файл
        file.write(f'{ip_address}\n')
        # Выполнение команды перезагрузки фаервола
        ssh_client.exec_command('/etc/init.d/firewall restart')

    # Копирование содержимого в локальный файл
    with sftp_client.open(config['whitelist-path'], 'r') as file:
        content = file.read().decode('utf-8').split('\n')
        print(content)

    # Отключение от сервера
    sftp_client.close()
    ssh_client.close()
