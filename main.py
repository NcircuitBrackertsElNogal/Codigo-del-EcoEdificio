import tkinter as tk
from tkinter import messagebox, filedialog
import serial
import serial.tools.list_ports
import threading
import time
import ast
import sys

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor Meteorológico RF - EcoEdificio")
        self.root.geometry("800x600")
        self.root.configure(bg="#2c3e50")

        # Variables de datos
        self.temp_history = [0] * 50
        self.hum_history = [0] * 50
        self.FILE_SIGNATURE = "ECO-EDIFICIO-DATA-v1"
        self.ser = None
        self.running = True 

        # Protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 1. Montar la interfaz primero (ESTÉTICA ORIGINAL)
        self.setup_ui()
        
        # 2. Iniciar la búsqueda del Arduino después de que la ventana sea visible
        self.root.after(1000, self.start_detection)

    def setup_ui(self):
        # Frame de etiquetas
        self.frame = tk.Frame(self.root, bg="#2c3e50")
        self.frame.pack(pady=15)
        
        self.lbl_t = tk.Label(self.frame, text="Temp: --°C", font=("Arial", 22, "bold"), fg="#e74c3c", bg="#2c3e50")
        self.lbl_t.pack(side=tk.LEFT, padx=30)
        
        self.lbl_h = tk.Label(self.frame, text="Hum: --%", font=("Arial", 22, "bold"), fg="#3498db", bg="#2c3e50")
        self.lbl_h.pack(side=tk.LEFT, padx=30)
        
        # Barra de estado
        self.lbl_status = tk.Label(self.root, text="Iniciando...", font=("Arial", 9), fg="white", bg="#34495e")
        self.lbl_status.pack(fill=tk.X)
        
        # Gráfico
        self.canvas = tk.Canvas(self.root, width=700, height=300, bg="black", highlightthickness=0)
        self.canvas.pack(pady=10)
        
        # Botones
        btn_f = tk.Frame(self.root, bg="#2c3e50")
        btn_f.pack(pady=20)
        tk.Button(btn_f, text="Generar Informe .eco", command=self.export_eco, bg="#27ae60", fg="white", width=20).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_f, text="Abrir Archivo .eco", command=self.import_eco, bg="#f39c12", fg="white", width=20).pack(side=tk.LEFT, padx=10)

    def start_detection(self):
        """Lanza el hilo de búsqueda para no congelar la GUI"""
        threading.Thread(target=self.detect_arduino_logic, daemon=True).start()
        self.update_canvas()

    def detect_arduino_logic(self):
        self.lbl_status.config(text="Buscando sensor en puertos disponibles...", fg="#f1c40f")
        ports = list(serial.tools.list_ports.comports())
        
        for p in ports:
            # Filtro básico para no colgarse con Bluetooth
            if "Bluetooth" in p.description: continue
            
            try:
                # Intento de conexión
                test_ser = serial.Serial(p.device, 9600, timeout=1)
                time.sleep(2) # Tiempo para que Arduino inicie
                
                # Leer una línea para validar datos "temp,hum"
                line = test_ser.readline().decode('utf-8', errors='ignore').strip()
                
                if ',' in line:
                    self.ser = test_ser
                    self.lbl_status.config(text=f"CONECTADO: {p.device}", fg="#2ecc71")
                    # Iniciar bucle de lectura real
                    threading.Thread(target=self.read_loop, daemon=True).start()
                    return
                else:
                    test_ser.close()
            except:
                continue
        
        # Si termina el bucle y no hay sensor:
        self.lbl_status.config(text="MODO VISOR - Sensor no detectado", fg="#e67e22")

    def read_loop(self):
        while self.running and self.ser:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if ',' in line:
                        t, h = map(float, line.split(','))
                        self.root.after(0, self.update_data, t, h)
            except:
                break
            time.sleep(0.1)

    def update_data(self, t, h):
        self.temp_history.append(t); self.temp_history.pop(0)
        self.hum_history.append(h); self.hum_history.pop(0)
        self.lbl_t.config(text=f"Temp: {t:.1f}°C")
        self.lbl_h.config(text=f"Hum: {h:.1f}%")

    def plot(self, data, color, y_range):
        if not data: return
        w, h = 700, 300
        min_y, max_y = y_range
        points = []
        for i, val in enumerate(data):
            x = i * (w / (len(data)-1))
            div = (max_y - min_y) if (max_y - min_y) != 0 else 1
            y = h - ((val - min_y) / div * h)
            points.append(x); points.append(y)
        if len(points) > 3:
            self.canvas.create_line(points, fill=color, width=2)

    def update_canvas(self):
        if not self.running: return
        self.canvas.delete("all")
        # Rejilla
        for i in range(0, 301, 50):
            self.canvas.create_line(0, i, 700, i, fill="#1a252f")
        # Líneas
        self.plot(self.temp_history, "#e74c3c", (0, 50))
        self.plot(self.hum_history, "#3498db", (0, 100))
        self.root.after(100, self.update_canvas)

    def import_eco(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos Eco", "*.eco")])
        if path:
            try:
                with open(path, "r") as f:
                    lines = f.readlines()
                    self.temp_history = ast.literal_eval(lines[1].strip())
                    self.hum_history = ast.literal_eval(lines[2].strip())
                    self.update_data(self.temp_history[-1], self.hum_history[-1])
            except:
                messagebox.showerror("Error", "Archivo inválido.")

    def export_eco(self):
        path = filedialog.asksaveasfilename(defaultextension=".eco", filetypes=[("Archivos Eco", "*.eco")])
        if path:
            with open(path, "w") as f:
                f.write(f"{self.FILE_SIGNATURE}\n{self.temp_history}\n{self.hum_history}")

    def on_closing(self):
        self.running = False
        if self.ser: self.ser.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()