import tkinter as tk
from tkinter import messagebox
import json
import threading
import paho.mqtt.client as mqtt
import time
from datetime import datetime
import os

class MonitorEcoEdificio:
    def __init__(self, root):
        self.root = root
        self.root.title("Eco-Edificio Control Panel - Sistema de Telemetría")
        self.root.geometry("950x800")
        self.root.configure(bg="#121212")

        self.archivo_log = "log_eco.txt"
        self.temp_history = [0] * 50
        self.hum_history = [0] * 50
        self.wind_history = [0] * 50
        self.id_actual = ""
        
        self.conectado = False
        self.setup_ui()
        self.update_canvas()

    def setup_ui(self):
        # --- Barra Superior ---
        top = tk.Frame(self.root, bg="#1e1e1e", pady=15)
        top.pack(fill=tk.X)
        
        tk.Label(top, text="ID ESP32:", fg="white", bg="#1e1e1e").pack(side=tk.LEFT, padx=10)
        self.ent_id = tk.Entry(top, font=("Consolas", 11), width=15, bg="#2d2d2d", fg="#00ff00", insertbackground="white")
        self.ent_id.pack(side=tk.LEFT, padx=5)

        self.btn_con = tk.Button(top, text="CONECTAR", command=self.conectar, bg="#2ecc71", fg="white", font=("Arial", 9, "bold"))
        self.btn_con.pack(side=tk.LEFT, padx=5)

        self.btn_des = tk.Button(top, text="DESCONECTAR", command=self.desconectar, bg="#e74c3c", fg="white", state="disabled", font=("Arial", 9, "bold"))
        self.btn_des.pack(side=tk.LEFT, padx=5)

        # --- Indicadores Gigantes ---
        mid = tk.Frame(self.root, bg="#121212")
        mid.pack(pady=30)
        self.lbl_t = tk.Label(mid, text="0.0°C", fg="#ff4444", bg="#121212", font=("Courier", 35, "bold"))
        self.lbl_t.pack(side=tk.LEFT, padx=25)
        self.lbl_h = tk.Label(mid, text="0.0%", fg="#4444ff", bg="#121212", font=("Courier", 35, "bold"))
        self.lbl_h.pack(side=tk.LEFT, padx=25)
        self.lbl_w = tk.Label(mid, text="0.0m/s", fg="#2ecc71", bg="#121212", font=("Courier", 35, "bold"))
        self.lbl_w.pack(side=tk.LEFT, padx=25)

        # --- Gráfico en Tiempo Real ---
        self.canvas = tk.Canvas(self.root, width=850, height=350, bg="#000000", highlightbackground="#333")
        self.canvas.pack(pady=10)

        # --- Barra de Estado ---
        self.status = tk.Label(self.root, text="Listo para capturar telemetría", bg="#000", fg="gray", anchor="w")
        self.status.pack(side="bottom", fill="x")

    def conectar(self):
        self.id_actual = self.ent_id.get().strip().upper()
        if not self.id_actual:
            messagebox.showwarning("ID Requerido", "Ingresa el ID del ESP32 para iniciar el registro.")
            return

        # Crear encabezado si el archivo es nuevo
        if not os.path.exists(self.archivo_log):
            with open(self.archivo_log, "w", encoding="utf-8") as f:
                f.write("FECHA,HORA,VIENTO,TEMP,HUM\n")

        self.conectado = True
        self.btn_con.config(state="disabled")
        self.btn_des.config(state="normal")
        self.ent_id.config(state="disabled")
        self.status.config(text=f"REGISTRANDO: {self.id_actual} - Los datos se guardan automáticamente", fg="#00ff00")
        
        threading.Thread(target=self.mqtt_worker, daemon=True).start()

    def desconectar(self):
        self.conectado = False
        self.btn_con.config(state="normal")
        self.btn_des.config(state="disabled")
        self.ent_id.config(state="normal")
        self.status.config(text="Registro detenido", fg="gray")

    def mqtt_worker(self):
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_message = self.on_message
        try:
            client.connect("broker.emqx.io", 1883, 60)
            client.subscribe("ecoedificio/data/principal")
            client.loop_forever()
        except:
            self.status.config(text="Error de red / Broker no disponible", fg="red")

    def on_message(self, client, userdata, msg):
        if not self.conectado: return
        try:
            data = json.loads(msg.payload.decode())
            # Filtro por ID introducido por el usuario
            if str(data.get("id")).upper() == self.id_actual:
                t = float(data.get("temp", 0))
                h = float(data.get("hum", 0))
                w = float(data.get("wind", 0))
                
                # --- GUARDADO EN TXT (FORMATO COMPATIBLE CON ANALIZADOR) ---
                ahora = datetime.now()
                # Fecha: DD/MM/YY | Hora: HH:MM:SS (24h para el archivo)
                linea = f"{ahora.strftime('%d/%m/%y,%H:%M:%S')},{w},{t},{h}\n"
                
                with open(self.archivo_log, "a", encoding="utf-8") as f:
                    f.write(linea)
                    f.flush() # Guardado inmediato en disco

                # Actualizar pantalla
                self.root.after(0, self.update_data, t, h, w)
        except:
            pass

    def update_data(self, t, h, w):
        self.temp_history.append(t); self.temp_history.pop(0)
        self.hum_history.append(h); self.hum_history.pop(0)
        self.wind_history.append(w); self.wind_history.pop(0)
        self.lbl_t.config(text=f"{t:.1f}°C")
        self.lbl_h.config(text=f"{h:.1f}%")
        self.lbl_w.config(text=f"{w:.1f}m/s")

    def update_canvas(self):
        self.canvas.delete("all")
        # Cuadrícula decorativa
        for i in range(0, 851, 85): self.canvas.create_line(i, 0, i, 350, fill="#111")
        
        # Dibujar líneas de sensores
        self.draw_line(self.temp_history, "#ff4444", (0, 50))
        self.draw_line(self.hum_history, "#4444ff", (0, 100))
        self.draw_line(self.wind_history, "#2ecc71", (0, 30))
        self.root.after(100, self.update_canvas)

    def draw_line(self, data, color, scale):
        w, h = 850, 350
        pts = []
        for i, val in enumerate(data):
            x = i * (w / 49)
            y = h - ((val - scale[0]) / (scale[1] - scale[0]) * h)
            pts.extend([x, y])
        if len(pts) >= 4: self.canvas.create_line(*pts, fill=color, width=2)

if __name__ == "__main__":
    root = tk.Tk(); app = MonitorEcoEdificio(root); root.mainloop()