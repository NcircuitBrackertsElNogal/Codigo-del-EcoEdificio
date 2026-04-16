#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

// Configuración del LCD: Dirección 0x27, 16 columnas y 2 filas
LiquidCrystal_I2C lcd(0x27, 16, 2); 

const int pinSolar = A0;

// --- AJUSTE DE RESISTENCIAS (Divisor de Voltaje) ---
float R1 = 10000.0; // Resistencia de 10k ohm
float R2 = 1000.0;  // Resistencia de 1k ohm

void setup() {
  lcd.init();
  lcd.backlight();

  // ==========================================
  //         PANTALLA DE PRESENTACIÓN
  // ==========================================
  lcd.setCursor(0, 0);
  lcd.print("    PROYECTO    "); // Espacios para centrar
  lcd.setCursor(0, 1);
  lcd.print("  ECO-EDIFICIO  ");
  delay(2500); // Pausa de 2.5 segundos
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(" MONITOREO SOLAR");
  lcd.setCursor(0, 1);
  lcd.print("V. 1.0 - ACTIVO");
  delay(2500);
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("INICIANDO SENSOR");
  lcd.setCursor(0, 1);
  for (int i = 0; i < 16; i++) {
    lcd.print("."); // Animación de carga de puntitos
    delay(100);
  }
  
  lcd.clear();
  // ==========================================
}

void loop() {
  // Lectura del sensor
  int valorADC = analogRead(pinSolar);
  
  // Cálculo de voltajes
  float voltajePin = (valorADC * 5.0) / 1023.0;
  float voltajePanel = voltajePin * ((R1 + R2) / R2);

  // Mostrar resultados en el LCD
  lcd.setCursor(0, 0);
  lcd.print("ESTADO: OK      "); // Indica que el sistema corre
  
  lcd.setCursor(0, 1);
  lcd.print("PANEL: ");
  lcd.print(voltajePanel, 2);
  lcd.print(" V    "); // Espacios para evitar basura visual

  delay(500); // Refresca cada medio segundo
}