# src/redes_project/backend.py
import platform
import subprocess

from .scheduler import iniciar_guardián_expiraciones  # Importaremos esto en el Paso 4


class DependenciaFaltanteError(Exception):
    """Excepción personalizada para indicar que falta un componente crítico."""
    pass

def verificar_dependencias():
    """Comprueba que FreeRADIUS (radiusd) esté accesible en Fedora."""
    sistema = platform.system().lower()
    print(">>> Verificando dependencias del motor de red en Fedora...")

    if sistema == "linux":
        try:
            # En Fedora el binario suele ser /usr/sbin/radiusd
            subprocess.run(["which", "radiusd"], capture_output=True, text=True, check=True)
            print("   ✓ FreeRADIUS (radiusd) encontrado en el sistema.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise DependenciaFaltanteError(
                "FreeRADIUS no está instalado.\n"
                "Instálalo en Fedora con: sudo dnf install freeradius freeradius-utils freeradius-sqlite"
            )
    else:
        raise DependenciaFaltanteError(f"Sistema '{sistema}' no soportado de forma nativa.")

def iniciar_backend_red():
    """Lanza FreeRADIUS y el planificador de expulsiones."""
    try:
        # Iniciar el demonio de FreeRADIUS en Fedora
        subprocess.run(["sudo", "systemctl", "start", "radiusd"], check=True, capture_output=True, text=True)
        print(">>> Motor FreeRADIUS (radiusd) iniciado exitosamente.")

        # --- NUEVO: Lanzar el hilo en segundo plano que monitorea el tiempo ---
        iniciar_guardián_expiraciones()

    except Exception as e:
        print(f">>> Aviso: No se pudo iniciar radiusd o el planificador. Error: {e}")
