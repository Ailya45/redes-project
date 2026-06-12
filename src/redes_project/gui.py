# src/redes_project/gui.py
from tkinter import messagebox

import customtkinter as ctk

from .database import registrar_llave

# =================================================================
# CONFIGURACIÓN DE LA RED WI-FI (Ajusta esto según tu Router)
# =================================================================
SSID_WIFI = "Red_Unefa_5G"  # <-- Nombre exacto de tu señal Wi-Fi

# =================================================================
# VENTANA EMERGENTE PARA MOSTRAR CREDENCIALES DE ACCESO
# =================================================================
class VentanaCredenciales(ctk.CTkToplevel):
    def __init__(self, parent, usuario, contrasena):
        super().__init__(parent)
        self.title("Credenciales de Acceso")

        # Tamaño optimizado para la lectura de las credenciales
        self.geometry("380x320")
        self.resizable(False, False)

        # Forzar a que la ventana aparezca al frente
        self.lift()
        self.attributes("-topmost", True)

        # Título principal
        self.label_titulo = ctk.CTkLabel(
            self, text="Acceso Wi-Fi Generado",
            font=("Arial", 18, "bold"), text_color="#27ae60"
        )
        self.label_titulo.pack(pady=(25, 5))

        # Recordatorio del SSID
        self.lbl_ssid = ctk.CTkLabel(
            self, text=f"Red: {SSID_WIFI}",
            font=("Arial", 13, "italic"), text_color="#7f8c8d"
        )
        self.lbl_ssid.pack(pady=(0, 15))

        # Ficha contenedor con fuentes grandes y legibles
        self.info_frame = ctk.CTkFrame(self, width=320, height=110)
        self.info_frame.pack(pady=10, padx=20, fill="x")
        self.info_frame.pack_propagate(False)

        self.lbl_user = ctk.CTkLabel(
            self.info_frame,
            text=f"Usuario:  {usuario}",
            font=("Arial", 16, "bold"),
            anchor="w"
        )
        self.lbl_user.pack(pady=(20, 5), padx=25, fill="x")

        self.lbl_pass = ctk.CTkLabel(
            self.info_frame,
            text=f"Contraseña:  {contrasena}",
            font=("Arial", 16, "bold"),
            text_color="#2980b9",
            anchor="w"
        )
        self.lbl_pass.pack(pady=(5, 15), padx=25, fill="x")

        # Botón de cierre
        self.btn_cerrar = ctk.CTkButton(
            self, text="ENTENDIDO", fg_color="#c0392b",
            hover_color="#e74c3c", font=("Arial", 13, "bold"),
            command=self.destroy
        )
        self.btn_cerrar.pack(pady=20)

# =================================================================
# INTERFAZ GRÁFICA PRINCIPAL (VENTANA NORMAL - MOSAICO EN HYPRLAND)
# =================================================================
class AppGestionWifi(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("UNEFA - Gestión Wi-Fi")
        self.geometry("400x450")
        # Dejada sin restricciones de redimensión para que Hyprland la maneje de forma normal

        self.label_titulo = ctk.CTkLabel(self, text="Generador de Acceso", font=("Arial", 22, "bold"))
        self.label_titulo.pack(pady=30)

        self.key_entry = ctk.CTkEntry(self, placeholder_text="Nombre de Usuario / ID", width=300, height=40)
        self.key_entry.pack(pady=10)

        self.tiempos_map = {
            "1 Minuto": 1, "5 Minutos": 5, "15 Minutos": 15,
            "30 Minutos": 30, "1 Hora": 60, "2 Horas": 120
        }
        self.time_menu = ctk.CTkOptionMenu(self, values=list(self.tiempos_map.keys()), width=300)
        self.time_menu.pack(pady=10)
        self.time_menu.set("1 Hora")

        self.btn_activar = ctk.CTkButton(self, text="GENERAR ACCESO",
                                         fg_color="#27ae60", height=45,
                                         font=("Arial", 13, "bold"),
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
            # Invocar la ventana emergente con los datos
            VentanaCredenciales(self, user_id, password)

            # Limpiar el campo de texto de la aplicación principal
            self.key_entry.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Este nombre de usuario ya está registrado o hubo un error de conexión.")
