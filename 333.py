# import os
# import time
#
# for i in os.listdir(r'Z:\лагерь\караоке'):
#     print(i.replace('.webm', '').replace('.mp4', '').replace('(Караоке)', '').replace('(Караоке Транскрипция)', '').replace('(Karaoke)', '').replace('(Karaoke version)', ''))
# import paho.mqtt.client as mqtt
#
# import paho.mqtt.client as mqtt
#
# mqtt_broker = "vympel.one"
# mqtt_port = 1883
# mqtt_topic = "chimer/ota"
# firmware_path = r"Z:\wemos\wemos.ino.d1_mini.bin"
# mqtt_username = "ota"
# mqtt_password = "ato"
#
# # Read the firmware binary file
# with open(firmware_path, "rb") as file:
#     firmware_data = file.read()
#
# # MQTT on_connect callback
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("Connected to MQTT Broker")
#     else:
#         print("Failed to connect, return code {0}".format(rc))
#
# # MQTT on_publish callback
# def on_publish(client, userdata, mid):
#     print("Firmware update sent successfully")
#     # Disconnect after a delay to give ESP8266 time to process the update
#     client.disconnect()
#
# client = mqtt.Client("FirmwareUpdater")
# client.on_connect = on_connect
# client.on_publish = on_publish
#
# # Set username and password for MQTT authentication
# client.username_pw_set(username=mqtt_username, password=mqtt_password)
#
# # Connect to the MQTT broker
# client.connect(mqtt_broker, mqtt_port)
#
# # Publish the firmware binary to the topic "chimer/ota"
# client.publish(mqtt_topic, firmware_data, qos=1)
#
# # Wait for a few seconds (you may need to adjust this delay)
# client.loop_start()
# time.sleep(5)  # Wait for 5 seconds (adjust the delay as needed)
# client.loop_stop()
#
# # Disconnect from the MQTT broker (or let the script terminate naturally)
# client.disconnect()
#
#
# # from playsound import playsound
# # import paho.mqtt.client as mqtt
# #
# #
# # def on_message(client, userdata, message):
# #     print(f'{message.topic}: {message.payload.decode("utf-8")}')
# #     # global status
# #     # topic = message.topic.split('/')
# #     # try:
# #     #     if int(topic[-1]) and status:
# #     #         status = False
# #     #         print(f'{message.payload.decode("utf-8")}')
# #     #         # воспроизвести звук Windows
# #     #         # playsound(r'L:\бабушке\Music\Шансон\М. Круг\#2_Jigan-limon\#2_08_Osenniy dojd.mp3')
# #     # except ValueError:
# #     #     if topic[-1] == 'state':
# #     #         print(f'button {topic[1]} is {message.payload.decode("utf-8")}')
# #     #     elif topic[-1] == 'buttons':
# #     #         status = True
# #     #         print('reset')
# #     # print(status)
# #
# #
# # status = True
# # client = mqtt.Client()
# # client.on_message = on_message
# #
# # client.connect("192.168.0.100", 1883)
# # client.subscribe("buttons/#")
# # client.loop_forever()
import os

import os
import subprocess
from PIL import Image
from PIL.ExifTags import TAGS

import os
import subprocess


def convert_heic_to_jpg(heic_file, jpg_output):
    try:
        # Преобразуйте путь к CP1251
        heic_file = heic_file.encode('cp1251').decode('cp1251')
        jpg_output = jpg_output.encode('cp1251').decode('cp1251')

        subprocess.run(['heif-convert', heic_file, '-q', '100', '-f', 'jpg'])
        return jpg_output
    except Exception as e:
        print(f"Ошибка при конвертации {heic_file} в .jpg: {e}")
        return None


def get_photo_shooting_date(file_path):
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()

        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == 'DateTimeOriginal':
                return value
    except (AttributeError, KeyError, IndexError):
        pass

    return None


def sort_files_by_photo_date(folder_path):
    jpg_files = []
    heic_files = []

    # Разделите файлы на .heic и .jpg
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.heic'):
            heic_files.append(filename)
        elif filename.lower().endswith(('.jpg', '.jpeg')):
            jpg_files.append(filename)

    # Конвертируйте .heic в .jpg и добавьте их к списку .jpg файлов
    for heic_file in heic_files:
        jpg_filename = os.path.splitext(heic_file)[0] + '.jpg'
        jpg_output = os.path.join(folder_path, jpg_filename)
        converted_file = convert_heic_to_jpg(os.path.join(folder_path, heic_file), jpg_output)
        if converted_file:
            jpg_files.append(jpg_filename)

    # Сортировка .jpg файлов по дате съемки
    jpg_files = sorted(jpg_files, key=lambda x: get_photo_shooting_date(os.path.join(folder_path, x)))

    return jpg_files


# Пример использования:
folder_path = r'z:\фото\2024\-1 вымпелevent'  # Укажите путь к вашей папке с фотографиями
sorted_files = sort_files_by_photo_date(folder_path)
for file in sorted_files:
    print(file)