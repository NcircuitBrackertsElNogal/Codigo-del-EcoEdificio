#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

// Configuración del LCD: Dirección 0x27, 16 columnas y 2 filas
LiquidCrystal_I2C lcd(0x27, 16, 2); 

const int pinViento = A2;     
const int numLecturas = 20;   
int lecturas[numLecturas];    
int indiceLectura = 0;
float total = 0;

// --- AJUSTE DE CALIBRACIÓN ---
float factorVelocidad = 6.0;  
float voltajeOffset = 0.4;    

void setup() {
  lcd.init();
  lcd.backlight();
  
  // Presentación inicial
  lcd.setCursor(0, 0);
  lcd.print("  ECOEDIFICIO   ");
  lcd.setCursor(0, 1);
  lcd.print(" SISTEMA ACTIVO ");
  
  for (int i = 0; i < numLecturas; i++) {
    lecturas[i] = 0;
  }
  
  delay(2000);
  lcd.clear();
}

void loop() {
  // 1. FILTRO DE PROMEDIO MÓVIL
  total = total - lecturas[indiceLectura];
  lecturas[indiceLectura] = analogRead(pinViento);
  total = total + lecturas[indiceLectura];
  indiceLectura = (indiceLectura + 1) % numLecturas;

  float promedioRaw = total / (float)numLecturas;
  float voltaje = (promedioRaw * 5.0) / 1023.0; 
  
  // 2. CÁLCULO DE VELOCIDAD
  float velocidadMS = 0;
  if (voltaje > voltajeOffset) {
    velocidadMS = (voltaje - voltajeOffset) * factorVelocidad;
  }
  
  float velocidadKMH = velocidadMS * 3.6;

  // 3. MOSTRAR EN PANTALLA LCD
  
  // Fila 0: Voltaje y m/s juntos
  lcd.setCursor(0, 0);
  lcd.print(voltaje, 1);
  lcd.print("V ");
  lcd.setCursor(6, 0); // Salto a la mitad de la fila
  lcd.print("| ");
  lcd.print(velocidadMS, 1);
  lcd.print(" m/s   ");

  // Fila 1: Velocidad en km/h
  lcd.setCursor(0, 1);
  lcd.print("VEL: ");
  lcd.print(velocidadKMH, 1);
  lcd.print(" km/h      ");

  delay(300); 
}