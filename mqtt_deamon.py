import paho.mqtt.client as mqtt


# Функция, которая будет вызвана при успешном подключении к брокеру MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    # Подписываемся на топик "buttons/mode1" при успешном подключении
    client.subscribe("buttons/#")


# Функция, которая будет вызвана при получении сообщения в топике
def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + ': ' + msg.payload.decode())


# Создание клиента MQTT
client = mqtt.Client()

# Установка обработчиков событий
client.on_connect = on_connect
client.on_message = on_message

# Подключение к брокеру MQTT (замените "mqtt.example.com" на адрес вашего брокера)
client.connect("vympel.one", 1883)
client.publish("buttons/wait", "0")
# Запуск бесконечного цикла клиента MQTT
client.loop_forever()