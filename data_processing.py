import os
import shutil
import socket
import sqlite3
import zipfile
from time import sleep
import time
import requests
import telegram
from watchdog.events import *
from watchdog.observers import Observer
import netifaces
import paramiko
import vk_api
import yaml
from PIL.ExifTags import TAGS
from pillow_heif import register_heif_opener
from PIL import Image
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from sqlighter import SQLighter

load_dotenv()


def get_local_ip():
    interfaces = netifaces.interfaces()
    for iface in interfaces:
        addresses = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addresses:
            for link in addresses[netifaces.AF_INET]:
                return link['addr']

    return None


def closest_disco_date(dates):
    current_datetime = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
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


def update_config_key(key, new_value):
    config = config_read()

    keys = key.split('.')
    sub_config = config
    for k in keys[:-1]:
        sub_config = sub_config.get(k, {})

    if keys[-1] in sub_config:
        sub_config[keys[-1]] = new_value
    else:
        print(f"Ключ '{key}' не найден в конфигурации.")
        return

    with open('config.yml', 'w', encoding='utf-8') as file:
        yaml.dump(config, file, allow_unicode=True)


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


def path_monitor(path=config_read()[f"monitor-path"].format(year=year, shift=shift)):
    token = os.environ['TG_BOT_TOKEN']
    bot = telegram.Bot(token=token)

    class PathHandler(FileSystemEventHandler):
        def on_created(self, event):
            path = event.src_path.replace(config_read()[f"monitor-path"] + "\\", "")
            if 'TeraCopy' not in path and 'crdownload' not in path and '~$' not in path and 'Thumbs.db' not in path:
                for telegram_id in config_read()['admin-telegram-id']:
                    bot.send_message(telegram_id, f'<b>{path}</b>'.replace('\\', '/'), parse_mode='html')

        # def on_modified(self, event):
        #     path = event.src_path.replace(config_read()[f"monitor-path"] + "\\", "")
        #     if 'TeraCopy' not in path:
        #         for telegram_id in config_read()['admin-telegram-id']:
        #             bot.send_message(telegram_id, f'изменено:\n<b>{path}\n</b>', parse_mode='html')

    path_handler = PathHandler()
    observer = Observer()
    observer.schedule(path_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def copy_files(source_folder, destination_folder):
    # Создаем папку назначения, если она не существует
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Копируем все файлы из исходной папки в папку назначения
    for item in os.listdir(source_folder):
        source_item = os.path.join(source_folder, item)
        destination_item = os.path.join(destination_folder, item)

        if os.path.isdir(source_item):
            shutil.copytree(source_item, destination_item)
        else:
            shutil.copy2(source_item, destination_item)


def clear_folder(folder_path):
    # Удаляем все содержимое папки
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Не удалось удалить {file_path}. Причина: {e}')
    else:
        os.makedirs(folder_path)


def parse_music_folder():
    # Пути к папкам
    source_folder1 = r'Z:\музыка\дискотека 2024'
    source_folder2 = r'Z:\музыка\медляки'
    destination_folder = r'Z:\музыка\голосование'

    try:
        clear_folder(destination_folder)
    except:
        pass

    # Копируем файлы из первой папки
    copy_files(source_folder1, destination_folder)

    # Копируем файлы из второй папки
    copy_files(source_folder2, destination_folder)

    path = fr'{config_read()["music-path"]}'
    songs = next(os.walk(path), (None, None, []))[2]

    for song in songs:
        try:
            if song.endswith('.mp3'):
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
        if config_read()['photo-use-shift']:
            folder_path = f"{config_read()['photo-path']}/{config_read()['year']}/{config_read()['shift']} поток"
        else:
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
    update_config_key('is-uploading', False)




def delete_photo(photo_link, album_id, owner_id, hash_value, cookies):
    url = "https://vk.com/al_photos.php"
    headers = {
        "Host": "vk.com",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Origin": "https://vk.com",
        "Referer": f"https://vk.com/album{owner_id}_{album_id}?act=edit",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": cookies
    }

    # Извлечение идентификатора фотографии
    photo_id = photo_link.split('/')[-1].replace('photo', '')
    data = {
        "act": "delete_photos",
        "al": "1",
        "album_id": album_id,
        "hash": hash_value,
        "owner_id": owner_id,
        "photos": photo_id
    }

    print(data)  # Печать данных для проверки
    response = requests.post(url, headers=headers, data=data)
    return response


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


if __name__ == "__main__":
    # Пример использования функции
    # data = db.get_specific_uploaded_photos('/2024/3 поток/08_день (спартакиада)9999999')
    # photo_links = [item[0] for item in data]
    # print(photo_links)
    # album_id = "301347182"
    # owner_id = "-1771052"
    # hash_value = "cbea8c6c5b5956b435"
    # cookies = ''
    # for photo_link in photo_links:
    #     response = delete_photo(photo_link, album_id, owner_id, hash_value, cookies)
    #     print(f"Response for {photo_link}: {response.text}")
    # print(response.text)
    print(config_read()['is-uploading'])