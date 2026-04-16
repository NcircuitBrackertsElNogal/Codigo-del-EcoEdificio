import tkinter as tk
from tkinter import messagebox, filedialog
import paho.mqtt.client as mqtt
import json
import ast
import threading
import time

class RemoteWeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor Meteorológico Cloud - EcoEdificio")
        self.root.geometry("800x600")
        self.root.configure(bg="#2c3e50")

        # --- CONFIGURACIÓN MQTT ---
        self.BROKER = "broker.emqx.io"
        self.ID_AUTORIZADO = "TU_ID_AQUI" # <--- PEGA AQUÍ EL ID DE TU ESP32
        self.TOPIC = f"ecoedificio/data/{self.ID_AUTORIZADO}"
        
        self.temp_history = [0] * 50
        self.hum_history = [0] * 50
        self.FILE_SIGNATURE = "ECO-EDIFICIO-DATA-v1"
        self.running = True

        self.setup_ui()
        
        # Iniciar conexión MQTT en hilo separado
        threading.Thread(target=self.init_mqtt, daemon=True).start()
        self.update_canvas()

    def setup_ui(self):
        # Etiquetas de datos
        self.frame = tk.Frame(self.root, bg="#2c3e50")
        self.frame.pack(pady=15)
        
        self.lbl_t = tk.Label(self.frame, text="Temp: --°C", font=("Arial", 22, "bold"), fg="#e74c3c", bg="#2c3e50")
        self.lbl_t.pack(side=tk.LEFT, padx=30)
        
        self.lbl_h = tk.Label(self.frame, text="Hum: --%", font=("Arial", 22, "bold"), fg="#3498db", bg="#2c3e50")
        self.lbl_h.pack(side=tk.LEFT, padx=30)
        
        # Estado de conexión
        self.lbl_status = tk.Label(self.root, text="Conectando a la nube...", font=("Arial", 9), fg="white", bg="#34495e")
        self.lbl_status.pack(fill=tk.X)
        
        # Gráfico Black
        self.canvas = tk.Canvas(self.root, width=700, height=300, bg="black", highlightthickness=0)
        self.canvas.pack(pady=10)
        
        # Botones de acción
        btn_f = tk.Frame(self.root, bg="#2c3e50")
        btn_f.pack(pady=20)
        tk.Button(btn_f, text="Exportar Informe .eco", command=self.export_eco, bg="#27ae60", fg="white", width=20).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_f, text="Cargar Histórico .eco", command=self.import_eco, bg="#f39c12", fg="white", width=20).pack(side=tk.LEFT, padx=10)

    def init_mqtt(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        try:
            self.client.connect(self.BROKER, 1883, 60)
            self.client.loop_forever()
        except Exception as e:
            self.lbl_status.config(text=f"Error de red: {e}", fg="#e74c3c")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.lbl_status.config(text=f"NUBE ACTIVA | Escuchando ID: {self.ID_AUTORIZADO}", fg="#2ecc71")
            self.client.subscribe(self.TOPIC)
        else:
            self.lbl_status.config(text="Fallo de autenticación en Broker", fg="#e74c3c")

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            if data['id'] == self.ID_AUTORIZADO:
                t = float(data['temp'])
                h = float(data['hum'])
                # Actualizar interfaz desde el hilo principal
                self.root.after(0, self.update_data, t, h)
        except:
            pass

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
            self.canvas.create_line(points, fill=color, width=2, smooth=True)

    def update_canvas(self):
        if not self.running: return
        self.canvas.delete("all")
        # Rejilla de fondo
        for i in range(0, 301, 50):
            self.canvas.create_line(0, i, 700, i, fill="#1a252f")
        
        self.plot(self.temp_history, "#e74c3c", (0, 50))
        self.plot(self.hum_history, "#3498db", (0, 100))
        self.root.after(100, self.update_canvas)

    def import_eco(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos Eco", "*.eco")])
        if path:
            try:
                with open(path, "r") as f:
                    lines = f.readlines()
                    if lines[0].strip() == self.FILE_SIGNATURE:
                        self.temp_history = ast.literal_eval(lines[1].strip())
                        self.hum_history = ast.literal_eval(lines[2].strip())
                        messagebox.showinfo("Éxito", "Historial cargado correctamente.")
            except:
                messagebox.showerror("Error", "Archivo corrupto.")

    def export_eco(self):
        path = filedialog.asksaveasfilename(defaultextension=".eco", filetypes=[("Archivos Eco", "*.eco")])
        if path:
            with open(path, "w") as f:
                f.write(f"{self.FILE_SIGNATURE}\n{self.temp_history}\n{self.hum_history}")
            messagebox.showinfo("Guardado", "Informe generado con éxito.")

    def on_closing(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RemoteWeatherApp(root)
    root.mainloop()