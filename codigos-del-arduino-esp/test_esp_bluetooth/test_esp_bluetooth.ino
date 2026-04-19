#include <BluetoothSerial.h>

// Comprobar si el Bluetooth está disponible
#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;

void setup() {
  Serial.begin(115200);
  
  // Nombre que aparecerá en tu celular
  SerialBT.begin("ESP32_Proyect"); 
  
  Serial.println("¡El dispositivo ya se puede vincular!");
}

void loop() {
  // Si recibes algo desde el celular, lo muestra en el monitor serie
  if (SerialBT.available()) {
    Serial.write(SerialBT.read());
  }
  
  // Si escribes algo en el monitor serie, lo envía al celular
  if (Serial.available()) {
    SerialBT.write(Serial.read());
  }
  delay(20);
}
