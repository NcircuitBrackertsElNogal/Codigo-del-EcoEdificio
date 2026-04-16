// --- CONFIGURACIÓN DE PINES ---
const int pinViento = A2;     // Pin analógico donde está conectado el sensor
const int numLecturas = 20;   // Cantidad de muestras para suavizar la lectura
int lecturas[numLecturas];    // Array para el promedio móvil
int indiceLectura = 0;
float total = 0;

// --- AJUSTE DE CALIBRACIÓN ---
float factorVelocidad = 6.0;  // Factor de escala (ajustar según tu sensor)
float voltajeOffset = 0.4;    // Voltaje base en reposo (0 m/s)

void setup() {
  // Inicializamos la comunicación con la PC
  Serial.begin(9600);
  
  // Inicializar el array de lecturas en 0
  for (int i = 0; i < numLecturas; i++) {
    lecturas[i] = 0;
  }

  Serial.println("========================================");
  Serial.println("   SISTEMA DE MEDICION: ECOEDIFICIO     ");
  Serial.println("      INICIANDO LECTURA DE VIENTO       ");
  Serial.println("========================================");
  delay(1000);
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

  // 3. IMPRESIÓN EN MONITOR SERIAL
  Serial.print("Voltaje: ");
  Serial.print(voltaje, 2);
  Serial.print("V | ");
  
  Serial.print("Velocidad: ");
}