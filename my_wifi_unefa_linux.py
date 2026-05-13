import sqlite3
import customtkinter as ctk
import subprocess
import secrets
import string
from datetime import datetime
from tkinter import messagebox

# 1. GESTIÓN DE DATOS (SQLITE)

DB_NAME = "radius_keys.db"

def init_db():
    """Crea la base de datos y aplica el modo WAL para evitar bloqueos."""
    conn = sqlite3.connect(DB_NAME)
    # --- MEJORA: MODO WAL ---
    # Esto permite que FreeRADIUS lea el archivo mientras Python escribe.
    conn.execute('PRAGMA journal_mode=WAL;')
    
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS keys 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       access_key TEXT UNIQUE, 
                       password TEXT, 
                       status TEXT,
                       fecha_inicio TEXT,
                       duracion_minutos INTEGER)''')
    conn.commit()
    conn.close()

def generar_contraseña_segura(longitud=8):
    """Genera una contraseña aleatoria."""
    caracteres = string.ascii_letters + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(longitud))

def registrar_llave(user_id, minutos):
    """Guarda usuario y contraseña con formato de fecha compatible con SQLite strftime."""
    password = generar_contraseña_segura()
    try:
        # --- MEJORA: FORMATO DE FECHA ---
        # Usamos el formato YYYY-MM-DD HH:MM:SS para que FreeRADIUS lo entienda perfectamente.
        inicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = sqlite3.connect(DB_NAME)
        # Aseguramos modo WAL en cada conexión
        conn.execute('PRAGMA journal_mode=WAL;')
        
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO keys (access_key, password, status, fecha_inicio, duracion_minutos) 
                          VALUES (?, ?, ?, ?, ?)""", 
                       (user_id, password, "active", inicio, minutos))
        conn.commit()
        conn.close()
        return password
    except sqlite3.IntegrityError:
        return None
    except Exception as e:
        print(f"Error en la base de datos: {e}")
        return None

# 2. INTERFAZ GRÁFICA (CUSTOMTKINTER)

class AppGestionWifi(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("UNEFA - Gestión Wi-Fi")
        self.geometry("400x450")

        self.label_titulo = ctk.CTkLabel(self, text="Generador de Acceso", font=("Arial", 22, "bold"))
        self.label_titulo.pack(pady=30)

        self.key_entry = ctk.CTkEntry(self, placeholder_text="Nombre de Usuario / ID", width=300, height=40)
        self.key_entry.pack(pady=10)

        self.tiempos_map = {"30 Minutos": 30, "1 Hora": 60, "2 Horas": 120}
        self.time_menu = ctk.CTkOptionMenu(self, values=list(self.tiempos_map.keys()), width=300)
        self.time_menu.pack(pady=10)
        self.time_menu.set("1 Hora")

        self.btn_activar = ctk.CTkButton(self, text="GENERAR ACCESO", 
                                         fg_color="#27ae60", height=45,
                                         command=self.procesar_registro)
        self.btn_activar.pack(pady=30)

    def procesar_registro(self):
        user_id = self.key_entry.get().strip()
        minutos = self.tiempos_map[self.time_menu.get()]

        if not user_id:
            messagebox.showwarning("Atención", "Ingrese un nombre de usuario.")
            return

        password = registrar_llave(user_id, minutos)
        
        if password:
            messagebox.showinfo("Acceso Creado", 
                                f"Usuario: {user_id}\n"
                                f"Contraseña: {password}\n\n"
                                "Entregue estos datos al invitado.")
            self.key_entry.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Este nombre de usuario ya está registrado o hubo un error de conexión.")


# 3. EJECUCIÓN

if __name__ == "__main__":
    # Apariencia oscura como pediste
    ctk.set_appearance_mode("dark")  
    
    # Inicializar DB y Motor
    init_db()
    iniciar_backend_red()
    
    app = AppGestionWifi()
    app.mainloop()