import yaml
import paramiko
import socket
import sqlite3
# from speechkit import Session, SpeechSynthesis
from sqlighter import SQLighter
import vk_api
import requests
import zipfile
import os

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

#
# def zip_photo(path):
#     # Имя файла ZIP-архива
#     zipfilename = 'example.zip'
#
#     # Создаем новый ZIP-архив
#     zipf = zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED)
#
#     # Добавляем все файлы и папки в ZIP-архив
#     for root, dirs, files in os.walk(path):
#         for file in files:
#             ziph.write(os.path.join(root, file))
#
#     # Закрываем ZIP-архив
#     zipf.close()
#
#     for root, dirs, files in os.walk(path):
#         for file in files:
#             ziph.write(os.path.join(root, file))


def upload_photo():
    db = SQLighter(database='vympel.one',
                   user='postgres',
                   password=os.environ['admin_password'],
                   host='192.168.0.100',
                   port=5432)
    uploaded_photo = list(zip(*db.get_uploaded_photo()))[0]
    # авторизация
    vk_session = vk_api.VkApi(token=os.environ['vk_token'])
    vk = vk_session.get_api()

    # идентификатор группы
    group_id = 1771052

    # идентификаторы альбомов группы текущего года
    album_ids = [292215594, 292215662, 292215665, 292215667]
    config = config_read()
    # путь к папке с фотографиями
    folder_path = config['photo-path']

    def into_folder(folder_path):
        # import os
        #
        # folder_path = "/path/to/folder"
        #
        # # Получаем список файлов в папке
        # files = os.listdir(folder_path)
        #
        # # Отбираем только файлы с расширением .jpg
        # jpg_files = [f for f in files if f.endswith(".jpg")]
        #
        # # Сортируем файлы по времени создания
        # jpg_files_sorted = sorted(jpg_files, key=lambda f: os.stat(os.path.join(folder_path, f)).st_mtime)

        files = os.listdir(folder_path)
        for file in files:
            if f"{folder_path + '/' + file}".replace(config['photo-path'], '') not in uploaded_photo:
                if os.path.isdir(folder_path + '/' + file) \
                        and file != '2023' \
                        and file != 'педсостав' \
                        and file != 'скрины' \
                        and file != 'фотографирование':
                    into_folder(folder_path + '/' + file)
                else:
                    if file.lower().endswith('jpg') or file.lower().endswith('jpeg'):
                        # проверяем, является ли файл фотографией
                        if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                            print(folder_path + '/' + file)
                            if '1 поток' in folder_path:
                                album_id = album_ids[0]
                                # загружаем фотографию в альбом группы
                                upload_url = vk.photos.getUploadServer(group_id=group_id, album_id=album_id)[
                                    'upload_url']

                                with open(folder_path + '/' + file, 'rb') as photo:
                                    response = vk_session.http.post(upload_url, files={'photo': ('photo.jpg', photo)})
                                    photo_data = \
                                        vk.photos.save(group_id=group_id, album_id=album_id,
                                                       server=response.json()['server'],
                                                       photos_list=response.json()['photos_list'],
                                                       hash=response.json()['hash'])[0]
                                    # выводим ссылку на загруженную фотографию
                                    print(f"{folder_path + '/' + file}".replace(config['photo-path'], ''))
                                    db.add_uploaded_photo(f"{folder_path + '/' + file}".replace(config['photo-path'], ''),
                                                          'https://vk.com/photo{}_{}'.format(photo_data['owner_id'],
                                                                                             photo_data['id']))

                            elif '2 поток' in folder_path:
                                album_id = album_ids[1]
                                # загружаем фотографию в альбом группы
                                upload_url = vk.photos.getUploadServer(group_id=group_id, album_id=album_id)[
                                    'upload_url']

                                with open(folder_path + '/' + file, 'rb') as photo:
                                    response = vk_session.http.post(upload_url, files={'photo': ('photo.jpg', photo)})
                                    photo_data = \
                                        vk.photos.save(group_id=group_id, album_id=album_id,
                                                       server=response.json()['server'],
                                                       photos_list=response.json()['photos_list'],
                                                       hash=response.json()['hash'])[0]
                                    # выводим ссылку на загруженную фотографию
                                    print(f"{folder_path + '/' + file}".replace(config['photo-path'], ''))
                                    db.add_uploaded_photo(f"{folder_path + '/' + file}".replace(config['photo-path'], ''),
                                                          'https://vk.com/photo{}_{}'.format(photo_data['owner_id'],
                                                                                             photo_data['id']))

                            elif '3 поток' in folder_path:
                                album_id = album_ids[2]
                                # загружаем фотографию в альбом группы
                                upload_url = vk.photos.getUploadServer(group_id=group_id, album_id=album_id)[
                                    'upload_url']

                                with open(folder_path + '/' + file, 'rb') as photo:
                                    response = vk_session.http.post(upload_url, files={'photo': ('photo.jpg', photo)})
                                    photo_data = \
                                        vk.photos.save(group_id=group_id, album_id=album_id,
                                                       server=response.json()['server'],
                                                       photos_list=response.json()['photos_list'],
                                                       hash=response.json()['hash'])[0]
                                    # выводим ссылку на загруженную фотографию
                                    print(f"{folder_path + '/' + file}".replace(config['photo-path'], ''))
                                    db.add_uploaded_photo(f"{folder_path + '/' + file}".replace(config['photo-path'], ''),
                                                          'https://vk.com/photo{}_{}'.format(photo_data['owner_id'],
                                                                                             photo_data['id']))

                            elif '4 поток' in folder_path:
                                album_id = album_ids[3]
                                # загружаем фотографию в альбом группы
                                upload_url = vk.photos.getUploadServer(group_id=group_id, album_id=album_id)[
                                    'upload_url']

                                with open(folder_path + '/' + file, 'rb') as photo:
                                    response = vk_session.http.post(upload_url, files={'photo': ('photo.jpg', photo)})
                                    photo_data = \
                                        vk.photos.save(group_id=group_id, album_id=album_id,
                                                       server=response.json()['server'],
                                                       photos_list=response.json()['photos_list'],
                                                       hash=response.json()['hash'])[0]
                                    # выводим ссылку на загруженную фотографию db.add_uploaded_photo(f"{folder_path +
                                    print(f"{folder_path + '/' + file}".replace(config['photo-path'], ''))
                                    db.add_uploaded_photo(f"{folder_path + '/' + file}".replace(config['photo-path'], ''),
                                                          'https://vk.com/photo{}_{}'.format(photo_data['owner_id'],
                                                                                             photo_data['id']))

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
        try:
            upload_photo()
            break
        except:
            print('повтор')
