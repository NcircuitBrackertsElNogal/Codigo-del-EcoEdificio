#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const char* ssid     = "Santiago";
const char* password = "15163087";
const char* mqtt_server = "broker.emqx.io";

#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

const int pinPanel = 34;
const int pinAnemometro = 35; // Pin para el viento

LiquidCrystal_I2C lcd(0x27, 16, 2);
WiFiClient espClient;
PubSubClient client(espClient);
String deviceID;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  
  dht.begin();
  lcd.init();
  lcd.backlight();
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);

  deviceID = WiFi.macAddress();
  deviceID.replace(":", "");
  client.setServer(mqtt_server, 1883);
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect(deviceID.c_str())) {
      Serial.println("¡Conectado!");
    } else {
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  float h = dht.readHumidity();
  float t = dht.readTemperature();
  
  // Lectura del Viento (Mapeo de 0 a 30 m/s o km/h según tu sensor)
  int valorViento = analogRead(pinAnemometro);
  float viento = map(valorViento, 0, 4095, 0, 30); 

  if (isnan(h) || isnan(t)) return;

  // LCD Update (Rotando info o simplificada)
  lcd.setCursor(0, 0);
  lcd.print("T:" + String(t,1) + " V:" + String(viento,1) + "m/s ");
  lcd.setCursor(0, 1);
  lcd.print("Hum: " + String(h,0) + "%      ");

  // JSON con campo "wind"
  String payload = "{\"id\":\"" + deviceID + "\",";
  payload += "\"temp\":" + String(t, 1) + ",";
  payload += "\"hum\":" + String(h, 1) + ",";
  payload += "\"wind\":" + String(viento, 1) + "}";

  client.publish("ecoedificio/data/principal", payload.c_str());
  Serial.println("Enviado: " + payload);
  delay(2000);
}
