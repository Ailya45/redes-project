import sys

import customtkinter as ctk

from .backend import (
    DependenciaFaltanteError,
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
    except DependenciaFaltanteError as e:
        print(f"\n[ERROR CRÍTICO] {e}\n")
        print("La aplicación no puede iniciar sin el motor de red.")
        sys.exit(1)

    ctk.set_appearance_mode("dark")

    # Inicializar DB
    init_db()

    # Iniciar Motor
    iniciar_backend_red()

    # Lanzar GUI
    app = AppGestionWifi()
    app.mainloop()


if __name__ == "__main__":
    main()
