import os
import time

for i in os.listdir(r'Z:\лагерь\караоке'):
    print(i.replace('.webm', '').replace('.mp4', '').replace('(Караоке)', '').replace('(Караоке Транскрипция)', '').replace('(Karaoke)', '').replace('(Karaoke version)', ''))
import paho.mqtt.client as mqtt

import paho.mqtt.client as mqtt

mqtt_broker = "vympel.one"
mqtt_port = 1883
mqtt_topic = "chimer/ota"
firmware_path = r"Z:\wemos\wemos.ino.d1_mini.bin"
mqtt_username = "ota"
mqtt_password = "ato"

# Read the firmware binary file
with open(firmware_path, "rb") as file:
    firmware_data = file.read()

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
    else:
        print("Failed to connect, return code {0}".format(rc))

# MQTT on_publish callback
def on_publish(client, userdata, mid):
    print("Firmware update sent successfully")
    # Disconnect after a delay to give ESP8266 time to process the update
    client.disconnect()

client = mqtt.Client("FirmwareUpdater")
client.on_connect = on_connect
client.on_publish = on_publish

# Set username and password for MQTT authentication
client.username_pw_set(username=mqtt_username, password=mqtt_password)

# Connect to the MQTT broker
client.connect(mqtt_broker, mqtt_port)

# Publish the firmware binary to the topic "chimer/ota"
client.publish(mqtt_topic, firmware_data, qos=1)

# Wait for a few seconds (you may need to adjust this delay)
client.loop_start()
time.sleep(5)  # Wait for 5 seconds (adjust the delay as needed)
client.loop_stop()

# Disconnect from the MQTT broker (or let the script terminate naturally)
client.disconnect()


# from playsound import playsound
# import paho.mqtt.client as mqtt
#
#
# def on_message(client, userdata, message):
#     print(f'{message.topic}: {message.payload.decode("utf-8")}')
#     # global status
#     # topic = message.topic.split('/')
#     # try:
#     #     if int(topic[-1]) and status:
#     #         status = False
#     #         print(f'{message.payload.decode("utf-8")}')
#     #         # воспроизвести звук Windows
#     #         # playsound(r'L:\бабушке\Music\Шансон\М. Круг\#2_Jigan-limon\#2_08_Osenniy dojd.mp3')
#     # except ValueError:
#     #     if topic[-1] == 'state':
#     #         print(f'button {topic[1]} is {message.payload.decode("utf-8")}')
#     #     elif topic[-1] == 'buttons':
#     #         status = True
#     #         print('reset')
#     # print(status)
#
#
# status = True
# client = mqtt.Client()
# client.on_message = on_message
#
# client.connect("192.168.0.100", 1883)
# client.subscribe("buttons/#")
# client.loop_forever()
