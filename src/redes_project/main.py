import contextlib

import customtkinter as ctk

from .backend import (
    detener_backend_red,
    iniciar_backend_red,
    verificar_dependencias,
)
from .database import init_db
from .gui import AppGestionWifi

# 4. EJECUCIÓN


def main():
    # --- Validación de entorno (NUEVA - Bloqueante) ---
    try:
        verificar_dependencias()



        ctk.set_appearance_mode("dark")

    # Inicializar DB
        init_db()

    # Iniciar Motor
        iniciar_backend_red()

    # Lanzar GUI
        app = AppGestionWifi()

        def al_cerrar_ventana():
            print("\n>>> Cerrando interfaz gráfica y liberando recursos de red...")
            with contextlib.suppress(Exception):
                detener_backend_red()
            app.destroy()

        app.protocol("WM_DELETE_WINDOW", al_cerrar_ventana)
        app.mainloop()

    except Exception as error:
        print(f"\n>>> [ERROR] {error}")

    finally:
        # Esto se ejecuta si cierras el programa con Ctrl+C en la terminal
        print("\n>>> [SISTEMA] Aplicación finalizada. Deteniendo motor FreeRADIUS de forma segura...")
        with contextlib.suppress(Exception):
            detener_backend_red()


if __name__ == "__main__":
    main()
