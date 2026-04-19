import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from datetime import datetime

def analizar_registro():
    fecha_buscada = ent_fecha.get().strip()
    
    # Función para validar que sean exactamente 2 dígitos
    def validar_digitos(val, nombre):
        if len(val) != 2 or not val.isdigit():
            raise ValueError(f"El campo {nombre} debe tener exactamente 2 números (ej: 05)")
        return val

    try:
        # 1. Validar y obtener horas de los cuadritos
        h1 = validar_digitos(ent_h1.get(), "Hora Inicio")
        m1 = validar_digitos(ent_m1.get(), "Minuto Inicio")
        s1 = validar_digitos(ent_s1.get(), "Segundo Inicio")
        p1 = sel_p1.get() # AM o PM

        h2 = validar_digitos(ent_h2.get(), "Hora Fin")
        m2 = validar_digitos(ent_m2.get(), "Minuto Fin")
        s2 = validar_digitos(ent_s2.get(), "Segundo Fin")
        p2 = sel_p2.get() # AM o PM

        # 2. Convertir formato 12h AM/PM a 24h para buscar en el archivo
        t1_obj = datetime.strptime(f"{h1}:{m1}:{s1} {p1}", "%I:%M:%S %p")
        t_ini = t1_obj.strftime("%H:%M:%S")

        t2_obj = datetime.strptime(f"{h2}:{m2}:{s2} {p2}", "%I:%M:%S %p")
        t_fin = t2_obj.strftime("%H:%M:%S")

        tiempos, vientos = [], []

        # 3. Lectura del archivo
        with open("log_eco.txt", "r", encoding="utf-8") as f:
            for linea in f:
                if "FECHA" in linea or not linea.strip(): continue
                partes = linea.strip().split(",")
                if len(partes) >= 3:
                    f_arc, h_arc, v_arc = partes[0], partes[1], partes[2]
                    
                    if f_arc == fecha_buscada and t_ini <= h_arc <= t_fin:
                        tiempos.append(h_arc)
                        vientos.append(float(v_arc))

        if not vientos:
            messagebox.showinfo("Buscador", "No se hallaron datos en ese rango.")
            return

        # 4. Gráfica
        plt.figure(figsize=(10, 5))
        plt.plot(tiempos, vientos, color='#2ecc71', marker='o', label="Viento (m/s)")
        plt.title(f"Reporte: {fecha_buscada} ({t_ini} a {t_fin})")
        plt.xticks(rotation=45, fontsize=8)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    except ValueError as ve:
        messagebox.showerror("Error de Formato", str(ve))
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema: {e}")

# --- INTERFAZ ---
app = tk.Tk()
app.title("Analizador Eco-Edificio 12h")
app.geometry("480x500")
app.configure(bg="#121212")

estilo_lbl = {"bg": "#121212", "fg": "white", "font": ("Arial", 10)}
estilo_ent = {"width": 3, "justify": "center", "font": ("Consolas", 12)}

tk.Label(app, text="SELECTOR DE HISTORIAL (12H)", font=("Arial", 14, "bold"), bg="#121212", fg="#2ecc71").pack(pady=20)

# FECHA
tk.Label(app, text="FECHA (DD/MM/YY):", **estilo_lbl).pack()
ent_fecha = tk.Entry(app, width=12, justify="center"); ent_fecha.insert(0, "18/04/26"); ent_fecha.pack(pady=5)

# FILA INICIO
tk.Label(app, text="DESDE:", **estilo_lbl).pack(pady=10)
f_ini = tk.Frame(app, bg="#121212")
f_ini.pack()
ent_h1 = tk.Entry(f_ini, **estilo_ent); ent_h1.insert(0, "02"); ent_h1.pack(side=tk.LEFT, padx=2)
tk.Label(f_ini, text=":", **estilo_lbl).pack(side=tk.LEFT)
ent_m1 = tk.Entry(f_ini, **estilo_ent); ent_m1.insert(0, "05"); ent_m1.pack(side=tk.LEFT, padx=2)
tk.Label(f_ini, text=":", **estilo_lbl).pack(side=tk.LEFT)
ent_s1 = tk.Entry(f_ini, **estilo_ent); ent_s1.insert(0, "00"); ent_s1.pack(side=tk.LEFT, padx=2)
sel_p1 = tk.StringVar(value="PM")
tk.OptionMenu(f_ini, sel_p1, "AM", "PM").pack(side=tk.LEFT, padx=5)

# FILA FIN
tk.Label(app, text="HASTA:", **estilo_lbl).pack(pady=10)
f_fin = tk.Frame(app, bg="#121212")
f_fin.pack()
ent_h2 = tk.Entry(f_fin, **estilo_ent); ent_h2.insert(0, "02"); ent_h2.pack(side=tk.LEFT, padx=2)
tk.Label(f_fin, text=":", **estilo_lbl).pack(side=tk.LEFT)
ent_m2 = tk.Entry(f_fin, **estilo_ent); ent_m2.insert(0, "06"); ent_m2.pack(side=tk.LEFT, padx=2)
tk.Label(f_fin, text=":", **estilo_lbl).pack(side=tk.LEFT)
ent_s2 = tk.Entry(f_fin, **estilo_ent); ent_s2.insert(0, "00"); ent_s2.pack(side=tk.LEFT, padx=2)
sel_p2 = tk.StringVar(value="PM")
tk.OptionMenu(f_fin, sel_p2, "AM", "PM").pack(side=tk.LEFT, padx=5)

tk.Button(app, text="BUSCAR Y GRAFICAR", command=analizar_registro, bg="#9b59b6", fg="white", font=("Arial", 11, "bold"), height=2, width=25).pack(pady=40)

app.mainloop()