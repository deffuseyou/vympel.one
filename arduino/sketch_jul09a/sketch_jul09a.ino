#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Замените значения SSID и пароля на соответствующие для вашей Wi-Fi сети
const char* ssid = "vympel";
const char* password = "";

// Замените значения на адрес вашего MQTT сервера и порт
const char* mqtt_server = "vympel.one";
const int mqtt_port = 1883;

// Замените значения на имя пользователя и пароль, если они используются на вашем MQTT сервере
const char* mqtt_user = "";
const char* mqtt_password = "";

WiFiClient espClient;
PubSubClient client(espClient);

// Пин, к которому подключена кнопка
const int state_pin = D2;

// Флаг, указывающий, была ли кнопка нажата в последний раз
bool flag = false;
bool wait = false;
bool last_button_state = false;
char* st = "2";

void setup_wifi() {
  delay(10);
  // Подключение к Wi-Fi сети
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  // Попытка переподключения к MQTT серверу
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Создание ID клиента, основанного на метке времени
    // Попытка подключения к серверу
    if (client.connect("button_2", mqtt_user, mqtt_password)) {
      Serial.println("connected");
      // Подписка на топики, если это необходимо
      client.subscribe("buttons/wait");
     } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Ожидание 5 секунд перед новой попыткой подключения
      delay(5000);
    }
  }
}

// Функция обработки полученных сообщений
void callback(char* topic, byte* payload, unsigned int length) {
  // Вывод названия топика
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");

  // Посимвольный вывод сообщения
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

  if ((char)payload[0] == '1') {
    wait = true;
    Serial.println("waiting mode on");
  }
  if ((char)payload[0] == '0') {
    wait = false;
    Serial.println("waiting mode off");
  }
  if ((char)payload[0] == 'a') {
    st = "2";
    Serial.println("режим моей игры");
  }
  if ((char)payload[0] == 'b') {
    st = "4";
    Serial.println("режим сайта");
  }
}
  
void setup() {
  pinMode(state_pin, INPUT_PULLUP);
  Serial.begin(9600);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  reconnect();
}

void loop() {
  // Проверка состояния кнопки
   bool button_state = digitalRead(state_pin) == LOW;
   if (button_state != last_button_state) {
    delay(100);
    last_button_state = button_state;
      // Если состояние кнопки изменилось, отправляем сообщение в топик
      if (button_state) {
        if (flag) {
          if (!wait) {
          client.publish("buttons/wait", "1");
          client.publish("buttons", st);
          Serial.println("ЕСТЬ ПРОБИТИЕ!");
          }
        }
        else {
          client.publish("buttons", st);
          Serial.println("ЕСТЬ ПРОБИТИЕ!");
        }
     }
  }
    client.loop();
}
