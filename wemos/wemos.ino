#include <ESP8266WiFi.h>
#include <PubSubClient.h>

const char* ssid = "vympel";
const char* password = "";

String device = "chimer";

const char* mqtt_server = "vympel.one";

int pwr_sw = D3;

WiFiClient espClient;
PubSubClient client(espClient);


void setup_wifi() {
  delay(10);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  randomSeed(micros());
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  if ((char)payload[0] == '1') {
      chime();
      client.publish("chime/status", "activated");
      Serial.println("[DEVICE] пум-пум-пум-пуум");
      }
  } 

// Функция переподключения к серверу
void reconnect() {
  // Цикл пока PC Switcher не подключен к серверу
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Если подключились оставляем LWT  
    if (client.connect(device.c_str(), device.c_str(), "interm", "chime/status", 1, false, "offline")) {
      Serial.println(" connected");
      client.publish("chime/status", "online");
      client.subscribe("chime");
    // Если не удалось подключиться
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}


// Функция эмитации кнопки chime
void chime(){
  digitalWrite(pwr_sw, LOW);
  delay(500);
  digitalWrite(pwr_sw, HIGH);
}


void setup() {
  pinMode(pwr_sw, OUTPUT);
  digitalWrite(pwr_sw, HIGH);

  // Выводим информацио об устройстве
  Serial.begin(9600);
  Serial.println("\n[VYMPEL] device: " + device);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}


// Функция-цикл подключения к mqtt серверу
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
