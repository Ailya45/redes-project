from tkinter import messagebox

import customtkinter as ctk

from .database import registrar_llave

# 3. INTERFAZ GRÁFICA (CUSTOMTKINTER)

class AppGestionWifi(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("UNEFA - Gestión Wi-Fi")
        self.geometry("400x450")

        self.label_titulo = ctk.CTkLabel(self, text="Generador de Acceso", font=("Arial", 22, "bold"))
        self.label_titulo.pack(pady=30)

        self.key_entry = ctk.CTkEntry(self, placeholder_text="Nombre de Usuario / ID", width=300, height=40)
        self.key_entry.pack(pady=10)

        # Mapa completo de tiempos (del script original)
        self.tiempos_map = {
            "1 Minuto": 1, "5 Minutos": 5, "15 Minutos": 15,
            "30 Minutos": 30, "1 Hora": 60, "2 Horas": 120
        }
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
