#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

// Configuración del LCD: Dirección 0x27, 16 columnas y 2 filas
LiquidCrystal_I2C lcd(0x27, 16, 2); 

// --- CONFIGURACIÓN DE PINES ---
const int pinV1 = A2;     
const int pinV2 = A3; 

const int numLecturas = 20;   
int lecturas1[numLecturas];    
int lecturas2[numLecturas];
int indice = 0;
float total1 = 0;
float total2 = 0;

// --- AJUSTE DE CALIBRACIÓN ---
float factorVelocidad = 6.0;  
float voltajeOffset = 0.4;    

void setup() {
  lcd.init();
  lcd.backlight();
  
  // Mensaje de inicio rápido
  lcd.setCursor(0, 0);
  lcd.print("SISTEMA DUAL");
  lcd.setCursor(0, 1);
  lcd.print("INICIALIZANDO...");
  
  for (int i = 0; i < numLecturas; i++) {
    lecturas1[i] = 0;
    lecturas2[i] = 0;
  }
  
  delay(1500);
  lcd.clear();
}

void loop() {
  // 1. FILTRO DE PROMEDIO MÓVIL
  total1 -= lecturas1[indice];
  total2 -= lecturas2[indice];
  
  lecturas1[indice] = analogRead(pinV1);
  lecturas2[indice] = analogRead(pinV2);
  
  total1 += lecturas1[indice];
  total2 += lecturas2[indice];
  
  indice = (indice + 1) % numLecturas;

  // 2. CÁLCULOS DE VELOCIDAD (KM/H)
  float vel1 = obtenerKMH(total1 / (float)numLecturas);
  float vel2 = obtenerKMH(total2 / (float)numLecturas);

  // 3. MOSTRAR AMBOS EN PANTALLA SIMULTÁNEAMENTE
  // Fila 0: Anemómetro 1
  lcd.setCursor(0, 0);
  lcd.print("A1: ");
  lcd.print(vel1, 1);
  lcd.print(" km/h      "); // Espacios extra para limpiar residuos de números largos

  // Fila 1: Anemómetro 2
  lcd.setCursor(0, 1);
  lcd.print("A2: ");
  lcd.print(vel2, 1);
  lcd.print(" km/h      ");

  delay(200); // Actualización fluida
}

// Función auxiliar para procesar la señal
float obtenerKMH(float promedioRaw) {
  float voltaje = (promedioRaw * 5.0) / 1023.0;
  float ms = 0;
  if (voltaje > voltajeOffset) {
    ms = (voltaje - voltajeOffset) * factorVelocidad;
  }
  return ms * 3.6;
}
