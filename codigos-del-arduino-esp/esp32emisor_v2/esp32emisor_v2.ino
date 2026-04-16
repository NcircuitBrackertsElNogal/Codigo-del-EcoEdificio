#include <WiFi.h>
#include <PubSubClient.h>

// --- CONFIGURACIÓN ---
const char* ssid     = "TU_WIFI";
const char* password = "TU_PASSWORD";
const char* mqtt_server = "broker.emqx.io";

// FORMA COMPATIBLE: Declaramos los objetos sin el (1) o (2)
// El compilador los aceptará como objetos de hardware serial vacíos.
HardwareSerial SerialArduA(1); 
HardwareSerial SerialArduB(2);

// Pines para los Arduinos
#define RX1 12
#define TX1 13
#define RX2 16
#define TX2 17

WiFiClient espClient;
PubSubClient client(espClient);
String deviceID;

void setup() {
  Serial.begin(115200); // Monitor Serie PC

  // Aquí es donde realmente asignamos el hardware y los pines.
  // El ESP32 mapeará internamente el objeto a la UART 1 y 2.
  SerialArduA.begin(9600, SERIAL_8N1, RX1, TX1);
  SerialArduB.begin(9600, SERIAL_8N1, RX2, TX2);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    Serial.print("."); 
  }

  deviceID = WiFi.macAddress();
  deviceID.replace(":", "");
  client.setServer(mqtt_server, 1883);

  Serial.println("\nConexión establecida. ID: " + deviceID);
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Intentando conexión MQTT...");
    if (client.connect(deviceID.c_str())) {
      Serial.println("conectado");
    } else {
      Serial.print("falló con estado ");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  String data1 = "";
  String data2 = "";

  // Captura de datos Arduino A
  if (SerialArduA.available()) {
    data1 = SerialArduA.readStringUntil('\n');
    data1.trim();
  }

  // Captura de datos Arduino B
  if (SerialArduB.available()) {
    data2 = SerialArduB.readStringUntil('\n');
    data2.trim();
  }

  // Si hay datos nuevos, publicamos en JSON
  if (data1.length() > 0 || data2.length() > 0) {
    String payload = "{\"id\":\"" + deviceID + "\", \"A1\":\"" + data1 + "\", \"A2\":\"" + data2 + "\"}";
    String topic = "ecoedificio/data/" + deviceID;
    
    client.publish(topic.c_str(), payload.c_str());
    Serial.println("Enviado: " + payload);
  }

  delay(1000); // Pequeña pausa para estabilidad
}
