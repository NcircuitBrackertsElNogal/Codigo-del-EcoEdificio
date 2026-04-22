#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// --- CONFIGURACIÓN WIFI Y MQTT ---
const char* ssid     = "TU_SSID";
const char* password = "TU_CLAVE";
const char* mqtt_server = "broker.emqx.io";

// --- CONFIGURACIÓN ANEMÓMETRO ---
const int pinAnem1 = 35; 

// --- LCD ---
LiquidCrystal_I2C lcd(0x27, 16, 2);

WiFiClient espClient;
PubSubClient client(espClient);
String deviceID;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  
  lcd.init();
  lcd.backlight();
  
  // Mensaje que pediste
  Serial.println("\n--------------------------------------");
  Serial.println("DHT11 NO CONECTADO");
  Serial.println("INICIANDO MEDICIÓN DEL VIENTO");
  Serial.println("--------------------------------------");

  lcd.print("Eco-Edificio");
  lcd.setCursor(0,1);
  lcd.print("Viento Activo");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  deviceID = WiFi.macAddress();
  deviceID.replace(":", "");
  
  client.setServer(mqtt_server, 1883);
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Conectando MQTT...");
    if (client.connect(deviceID.c_str())) {
      Serial.println("¡Listo!");
    } else {
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  // Lectura del Anemómetro (Viento)
  int valorViento = analogRead(pinAnem1);
  // Mapeo: 0-4095 es la lectura del ESP32, 0-30 es la velocidad en m/s
  float viento = map(valorViento, 0, 4095, 0, 30); 

  // Mostrar en LCD
  lcd.setCursor(0, 0);
  lcd.print("VIENTO: " + String(viento, 1) + " m/s  ");
  lcd.setCursor(0, 1);
  lcd.print("ID:" + deviceID);

  // Crear JSON solo con Viento (Temp y Hum en 0)
  String payload = "{";
  payload += "\"id\":\"" + deviceID + "\",";
  payload += "\"temp\":0.0,";
  payload += "\"hum\":0.0,";
  payload += "\"wind\":" + String(viento, 1);
  payload += "}";

  // Publicar
  client.publish("ecoedificio/data/principal", payload.c_str());

  Serial.print("Reporte: ");
  Serial.println(payload);
  
  delay(2000);
}
