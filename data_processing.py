import os
import shutil
import socket
import sqlite3
import zipfile
from time import sleep

import netifaces
import paramiko
import vk_api
import yaml
from PIL.ExifTags import TAGS
from pillow_heif import register_heif_opener

from PIL import Image
import os
from datetime import datetime, timezone, timedelta

from sqlighter import SQLighter


def get_local_ip():
    interfaces = netifaces.interfaces()
    for iface in interfaces:
        addresses = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addresses:
            for link in addresses[netifaces.AF_INET]:
                return link['addr']

    return None


def closest_disco_date(dates):
    current_datetime = datetime.today()
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
    config = yaml.load(open('config.yml', encoding='utf-8'), Loader=yaml.SafeLoader)
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


def parse_music_folder():
    path = fr'{config_read()["music-path"]}'
    songs = next(os.walk(path), (None, None, []))[2]

    for song in songs:
        try:
            db.add_song(song.replace('.mp3', ''))
            print(f'Песня "{song.replace(".mp3", "")}" добавлена')
        except sqlite3.IntegrityError:
            pass


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


def get_heic_datetime(file):
    register_heif_opener()
    img = Image.open(file)
    exif_data = img.getexif()

    if exif_data is not None:  # Add this check
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == "DateTime":
                return int(datetime.strptime(value, "%Y:%m:%d %H:%M:%S").replace(
                    tzinfo=timezone(timedelta(hours=3))).timestamp())


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

    print(folder_path)

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


def give_internet_access(login, ip_address):
    config = config_read()
    # Подключение к удаленному серверу
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=config['router']['ip'],
                       username=config['router']['user'],
                       password=os.environ['ROUTER_PASSWORD'])

    # Открытие файла для дозаписи
    sftp_client = ssh_client.open_sftp()

    with sftp_client.open(config['whitelist-path'], 'r') as file:
        content = file.read().decode('utf-8').split('\n')
    if ip_address not in content:
        with sftp_client.open(config['whitelist-path'], 'a+') as file:
            file.write(f'# {login}\n{ip_address}\n\n')

        stdin, stdout, stderr = ssh_client.exec_command(f"ip neigh show {ip_address} | awk '{{print $5}}'")
        mac_address = stdout.read().decode().strip()

        sleep(0.1)
        ssh_client.exec_command("uci add dhcp host")
        sleep(0.1)
        ssh_client.exec_command(f"uci set dhcp.@host[-1].name='{login.replace(' ', '-')}'")
        sleep(0.1)
        ssh_client.exec_command(f"uci set dhcp.@host[-1].ip='{ip_address}'")
        sleep(0.1)
        ssh_client.exec_command(f"uci set dhcp.@host[-1].mac='{mac_address}'")
        sleep(0.1)
        ssh_client.exec_command("uci set dhcp.@host[-1].leasetime='infinite'")
        sleep(0.1)
        ssh_client.exec_command("uci commit dhcp")
        sleep(0.1)
        ssh_client.exec_command("/etc/init.d/dnsmasq restart")
        sleep(0.1)
        ssh_client.exec_command('/etc/init.d/firewall restart')

        sftp_client.close()
        ssh_client.close()
        return True

    sftp_client.close()
    ssh_client.close()
    return False
