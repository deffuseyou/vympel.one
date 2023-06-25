import os
import shutil
import socket
import sqlite3
import subprocess

import paramiko
import vk_api
import yaml
import yt_dlp

# from speechkit import Session, SpeechSynthesis
from sqlighter import SQLighter
from collections import Counter


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


def transform_tuple(tuple_input):
    count_dict = {}
    transformed_tuple = []

    # Подсчет количества вхождений элементов в кортеже
    for element in tuple_input:
        if element not in count_dict:
            count_dict[element] = 1
        else:
            count_dict[element] += 1

    # Добавление элементов в преобразованный кортеж согласно правилам
    for element in tuple_input:
        if count_dict[element] % 2 != 0:  # Удаление элемента, если встречается четное число раз
            transformed_tuple.append(element)

    return transformed_tuple


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
                   password=os.environ['ADMIN_PASSWORD'],
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


def download_and_play_karaoke(search_query, ip):
    ydl = yt_dlp.YoutubeDL({'format': "bv*+ba/b",
                            'outtmpl': 'z:\\караоке\\%(title)s.%(ext)s'})

    ydl.download(f"ytsearch:{search_query}")

    with yt_dlp.YoutubeDL() as ydl:
        search_results = ydl.extract_info(f"ytsearch:{search_query}", download=False)
        if 'entries' in search_results:
            first_video = search_results['entries'][0]
            video_title = first_video['title']
            video_link = first_video['id']
            title = f'{video_title}.webm'

    ssh = paramiko.SSHClient()
    ssh.connect(ip, username='admin', password=os.environ['ADMIN_PASSWORD'])
    ssh.exec_command(fr'c:\Program Files\MPC-HC\mpc-hc64.exe "z:\лагерь\караоке\{title}"')
    ssh.close()


def zip_photo():
    subfolders = [f.path for f in os.scandir(config_read()['now-photo-path']) if f.is_dir()]

    for subfolder in subfolders:
        if any(os.scandir(subfolder)):
            archive_name = os.path.join(config_read()['files-path'], os.path.basename(subfolder))

            shutil.make_archive(archive_name, 'zip', subfolder)
            print(f'Создан архив {archive_name}')


def upload_to_album(album_id, file, db):
    vk_session = vk_api.VkApi(token=os.environ['VK_TOKEN'])
    vk = vk_session.get_api()

    # идентификатор группы
    group_id = 1771052

    upload_url = vk.photos.getUploadServer(group_id=group_id, album_id=album_id)[
        'upload_url']

    print(file)
    with open(file, 'rb') as photo:
        try:
            response = vk_session.http.post(upload_url, files={'photo': ('photo.jpg', photo)})
            photo_data = \
                vk.photos.save(group_id=group_id, album_id=album_id,
                               server=response.json()['server'],
                               photos_list=response.json()['photos_list'],
                               hash=response.json()['hash'])[0]
            # выводим ссылку на загруженную фотографию
            print(f"{file}".replace(config_read()['photo-path'], ''))
            print(photo_data)
            db.add_uploaded_photo(f"{file}".replace(config_read()['photo-path'], ''),
                                  'https://vk.com/photo{}_{}'.format(photo_data['owner_id'],
                                                                     photo_data['id']))
        except Exception as e:
            print(e)
            upload_to_album(album_id, file, db)


def photo_uploader():
    db = SQLighter(database='vympel.one',
                   user='postgres',
                   password=os.environ['ADMIN_PASSWORD'],
                   host='192.168.0.100',
                   port=5432)
    uploaded_photo = list(zip(*db.get_uploaded_photo()))[0]

    config = config_read()
    # путь к папке с фотографиями
    folder_path = config['photo-path']

    def into_folder(folder_path):
        album_ids = config_read()['album_ids']
        files = sorted(os.listdir(folder_path), key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))
        for file in files:
            if f"{folder_path + '/' + file}".replace(config['photo-path'], '') not in uploaded_photo:
                if os.path.isdir(folder_path + '/' + file) \
                        and file != 'педсостав' \
                        and file != 'скрины' \
                        and file != 'фотографирование':
                    into_folder(folder_path + '/' + file)
                else:
                    if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                        for album_id in album_ids:
                            key = list(album_id.keys())[0]
                            value = album_id[key]
                            if key in folder_path + '/' + file:
                                upload_to_album(*value, folder_path + '/' + file, db)

    into_folder(folder_path)


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

        command = f"cat /proc/net/arp | grep '{ip_address}' | " + "awk '{print $4}'"
        stdin, stdout, stderr = ssh_client.exec_command(command)
        mac_address = stdout.read().decode('utf-8').upper()

        ssh_client.exec_command(f"uci set dhcp.@host[-1].ip = f'{ip_address}'")
        ssh_client.exec_command(f"uci set dhcp.@host[-1].mac = f'{mac_address}'")
        ssh_client.exec_command("uci commit dhcp")
        ssh_client.exec_command("/etc/init.d/dnsmasq restart")

        # Выполнение команды перезагрузки фаервола
        ssh_client.exec_command('/etc/init.d/firewall restart')

    # Копирование содержимого в локальный файл
    with sftp_client.open(config['whitelist-path'], 'r') as file:
        content = file.read().decode('utf-8').split('\n')
        print(content)

    # Отключение от сервера
    sftp_client.close()
    ssh_client.close()


if __name__ == '__main__':
    while True:
        photo_uploader()
        break
