import os

for i in os.listdir(r'Z:\лагерь\караоке'):
    print(i.replace('.webm', '').replace('.mp4', '').replace('(Караоке)', '').replace('(Караоке Транскрипция)', '').replace('(Karaoke)', '').replace('(Karaoke version)', ''))

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
