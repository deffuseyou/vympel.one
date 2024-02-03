import shutil
import shutil
import socket
import sqlite3
import subprocess
import zipfile
import paramiko
import pyttsx3
import vk_api
import yaml
import yt_dlp
from PIL.ExifTags import TAGS
from pillow_heif import register_heif_opener
import os
from sqlighter import SQLighter


def closest_disco_date(dates):
    current_datetime = datetime.now()
    converted_dates = [datetime.strptime(date, "%d.%m.%Y") for date in dates]

    # Удалите даты, которые предшествуют текущей дате
    converted_dates = [date for date in converted_dates if date >= current_datetime]

    if not converted_dates:
        return "пока неизвестно"

    closest_date = min(converted_dates, key=lambda x: abs(x - current_datetime))
    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
              'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

    return closest_date.strftime("%d {month}").format(month=months[closest_date.month - 1]).lstrip('0')



def config_read():
    config = yaml.load(open('config.yml'), Loader=yaml.SafeLoader)
    return config

year = config_read()['year']
shift = config_read()['shift']
db = SQLighter(database=config_read()['db']['database'],
               user=config_read()['db']['user'],
               password=os.environ['ADMIN_PASSWORD'],
               host=config_read()['db']['host'],
               port=config_read()['db']['port'])

def is_connected():
    try:
        socket.create_connection(("1.1.1.1", 80))
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


def transmit_message(text):
    engine = pyttsx3.init()
    engine.setProperty('voice', engine.getProperty('voices')[0].id)
    engine.say(text)
    engine.runAndWait()


def parse_music_folder():
    path = fr'{config_read()["music-path"]}'
    songs = next(os.walk(path), (None, None, []))[2]

    for song in songs:
        try:
            db.add_song(song.replace('.mp3', ''))
            print(f'Песня "{song.replace(".mp3", "")}" добавлена')
        except sqlite3.IntegrityError:
            pass


def download_and_play_karaoke(search_query):
    ydl = yt_dlp.YoutubeDL({'format': "bv*+ba/b",
                            'outtmpl': 'z:\\лагерь\\караоке\\%(title)s.%(ext)s'})

    ydl.download(f"ytsearch:{search_query}")

    with yt_dlp.YoutubeDL() as ydl:
        search_results = ydl.extract_info(f"ytsearch:{search_query}", download=False)
        if 'entries' in search_results:
            first_video = search_results['entries'][0]
            video_title = first_video['title']
            video_link = first_video['id']
            title = f'{video_title}.webm'
    subprocess.call(['C:\Program Files\MPC-HC\mpc-hc64.exe', f'z:/караоке/{title}'])

import pyautogui


def ctrl_click():
    # Координаты щелчка
    x = 100
    y = 100

    # Перемещаем курсор по указанным координатам и кликаем левой кнопкой мыши
    pyautogui.moveTo(x, y)
    pyautogui.click()

    # Нажимаем правый Ctrl
    pyautogui.keyDown('ctrlright')
    pyautogui.keyUp('ctrlright')


def zip_photo():
    subfolders = [f.path for f in os.scandir(config_read()[f'now-photo-path']) if f.is_dir()]

    for subfolder in subfolders:
        if any(os.scandir(subfolder)):
            archive_name = os.path.join(config_read()[f'archives-path'], os.path.basename(subfolder))
            archive_path = archive_name + '.zip'
            print(archive_path)
            if os.path.exists(archive_path):
                try:
                    with zipfile.ZipFile(archive_path, 'r') as archive:
                        print(len(os.listdir(subfolder)), len(archive.namelist()))
                        if abs(len(os.listdir(subfolder)) - len(archive.namelist())) > 1:
                            shutil.make_archive(archive_name, 'zip', subfolder)
                            print(f'Дополнен архив {archive_name}')
                except zipfile.BadZipFile:
                    os.remove(archive_path)
                    zip_photo()
            else:
                print('нет файла')
                shutil.make_archive(archive_name, 'zip', subfolder)
                print(f'Создан архив {archive_name}')


def upload_to_album(album_id, file):
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
            upload_to_album(album_id, file)


from PIL import Image
import os
from datetime import datetime, timezone


def get_image_creation_date(image_path):
    if image_path.lower().endswith('.heic'):
        register_heif_opener()
        img = Image.open(image_path)
        exif_data = img.getexif()

        if exif_data is not None:  # Add this check
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == "DateTime":
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S").replace(tzinfo=timezone.utc)
    if image_path.lower().endswith('.jpeg') or image_path.lower().endswith('.jpg'):
        img = Image.open(image_path)
        exif_data = img._getexif()

        if exif_data is not None:  # Add this check
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == "DateTimeOriginal":
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return datetime.fromtimestamp(os.path.getmtime(image_path)).replace(tzinfo=timezone.utc)


def photo_uploader():
    uploaded_photo = list(zip(*db.get_uploaded_photo()))[0]

    # путь к папке с фотографиями
    if config_read()['photo-use-year']:
        folder_path = f"{config_read()['photo-path']}/{config_read()['year']}"
    else:
        folder_path = config_read()['photo-path']


    def into_folder(folder_path):
        album_ids = config_read()['album_ids']
        files = sorted(os.listdir(folder_path), key=lambda x: get_image_creation_date(os.path.join(folder_path, x)))
        for file in files:
            full_path = folder_path + '/' + file
            if f"{full_path}".replace(config_read()['photo-path'], '') not in uploaded_photo:
                if os.path.isdir(full_path) and file not in config_read()['exclude-photo-path']:
                    into_folder(full_path)
                else:
                    if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg') or \
                            file.lower().endswith('.heic'):
                        for album_id in album_ids:
                            key = list(album_id.keys())[0]
                            value = album_id[key]
                            if key in full_path:
                                upload_to_album(*value, full_path)

    into_folder(folder_path)

def give_internet_access(ip_address):
    config = config_read()
    # Подключение к удаленному серверу
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=config['router']['ip'],
                       username=config['router']['user'],
                       password=os.environ['ROUTER_PASSWORD'])

    # Открытие файла для дозаписи
    sftp_client = ssh_client.open_sftp()
    with sftp_client.open(config['whitelist-path'], 'a+') as file:
        # Запись данных в файл
        file.write(f'{ip_address}\n')

        command = f"cat /proc/net/arp | grep '{ip_address}' | " + "awk '{print $4}'"
        stdin, stdout, stderr = ssh_client.exec_command(command)
        mac_address = stdout.read().decode('utf-8').upper().replace('\n', '')

        print([mac_address[:17], ip_address])
        # ssh_client.exec_command(f"uci add dhcp host # =cfg13fe63")
        # ssh_client.exec_command(f"uci set dhcp.@host[-1].ip='{str(ip_address)}'")
        # ssh_client.exec_command(f"uci set dhcp.@host[-1].mac='{mac_address[:17]}'")
        # ssh_client.exec_command("uci commit dhcp")
        # ssh_client.exec_command("/etc/init.d/dnsmasq restart")

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
        text = """Хм, ты кое-кого забыла…
Сегодня отмечается «День ковбоя», «День прокурора» и «День толстяка и толстушки», концерт наверняка посвящён одному из этих праздников.
Настя, а можешь мне что-то рассказать про четвертую лигу? 
Четвёртый по силе дивизион профессионального российского футбола, существовавший в 1994—1997 годах. 
Настя, а почему я ничего не могу найти про ваши лиги в интернете?
Я хочу сама расспросить следующую лигу!
Первая лига спародируйте своего инструктора.
Конечно, что бы выбрали проспать зарядку, душ каждый день или горячие бутерброды с колбасой?
Пятая лига, это самые младшие?
Очень, можно мне остаться с вами и еще лучше узнать ваши лиги?
Включаю лагерный миниклуб """
        transmit_message(text)
        break
