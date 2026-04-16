#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

// Configuración de la pantalla LCD (Dirección 0x27 y tamaño 16x2)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Configuración del sensor DHT11
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Pin del Panel Solar
const int panelPin = A0;

void setup() {
  // Inicialización
  lcd.init();
  lcd.backlight();
  dht.begin();
  
  // 1. Presentación del proyecto
  lcd.setCursor(0, 0);
  lcd.print("   PROYECTO    ");
  lcd.setCursor(0, 1);
  lcd.print("  ECOEDIFICIO  ");
  delay(3000); // Pausa de 3 segundos
  lcd.clear();
}

void loop() {
  // Lectura de humedad y temperatura
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Lectura del Panel Solar (Conversión simple a voltaje)
  int sensorValue = analogRead(panelPin);
  float voltaje = sensorValue * (5.0 / 1023.0);

  // 2. Mostrar estado del Panel Solar
  lcd.setCursor(0, 0);
  lcd.print("Panel: ");
  lcd.print(voltaje);
  lcd.print("V     "); // Espacios para limpiar residuos de texto

  // 3. Mostrar Temperatura y Humedad
  lcd.setCursor(0, 1);
  lcd.print("T:");
  lcd.print((int)t);
  lcd.print("C  H:");
  lcd.print((int)h);
  lcd.print("%    ");

  delay(1500); // Actualización cada 2 segundos
}
