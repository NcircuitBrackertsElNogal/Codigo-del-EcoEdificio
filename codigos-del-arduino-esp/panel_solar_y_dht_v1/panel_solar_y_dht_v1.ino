#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

//Este es el codigo el cual unifica la lectura de paneles solares y lectura de humedad y temperatura mediante un sensor dht11.
//El sensor debe ser alimetado con NO MAS DE 5.5v, Y no menos de 5.0v, La lectura podría salir defectuosa o no procesada
//Los paneles deben ser conectado con el positivo (o poder) al pin A0, Y el común a GND
//Suerte.

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

  delay(1500); // Actualización cada 1 segundo y medio
}
