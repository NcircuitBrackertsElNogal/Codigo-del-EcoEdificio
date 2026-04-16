#include <WiFi.h>
#include <PubSubClient.h>

// --- CONFIGURACIÓN ---
const char* ssid     = "TU_WIFI";
const char* password = "TU_PASSWORD";
const char* mqtt_server = "broker.emqx.io"; // Broker gratuito público

WiFiClient espClient;
PubSubClient client(espClient);
String deviceID;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }

  // ID ÚNICO: Usamos la MAC para que nadie más use nuestro canal
  deviceID = WiFi.macAddress();
  deviceID.replace(":", "");
  
  Serial.println("\nID Único del dispositivo: " + deviceID);
  client.setServer(mqtt_server, 1883);
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Intentando conexión MQTT...");
    // Intentamos conectar con el ID único
    if (client.connect(deviceID.c_str())) {
      Serial.println("conectado");
    } else {
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  // Datos simulados
  float t = 25.5 + (random(-10, 10) / 10.0);
  
  // Construimos el mensaje JSON con el ID
  String payload = "{\"id\":\"" + deviceID + "\", \"temp\":" + String(t) + "}";
  
  // Publicamos en un tópico único basado en el ID
  String topic = "ecoedificio/data/" + deviceID;
  client.publish(topic.c_str(), payload.c_str());

  Serial.println("Publicado en " + topic + ": " + payload);
  delay(5000); // Enviar cada 5 segundos
}