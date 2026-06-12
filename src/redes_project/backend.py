"""Funciones de arranque y apagado del backend con FreeRADIUS."""

import platform
import shutil
import subprocess

from .scheduler import iniciar_guardián_expiraciones


class DependenciaFaltanteError(Exception):
    """Excepción personalizada para indicar que falta un componente crítico."""
    pass


def _obtener_configuracion_radius():
    """Detecta el motor de FreeRADIUS instalado y su nombre de servicio en Linux."""
    sistema = platform.system().lower()
    if sistema != "linux":
        raise DependenciaFaltanteError(f"Sistema '{platform.system()}' no soportado de forma nativa.")

    if shutil.which("radiusd"):
        return "radiusd", None
    if shutil.which("freeradius"):
        return "freeradius", None

    try:
        with open("/etc/os-release") as f:
            contenido = f.read().lower()
            if "fedora" in contenido or "rhel" in contenido or "centos" in contenido:
                return "radiusd", "fedora"
            elif any(distro in contenido for distro in ["mint", "ubuntu", "debian"]):
                return "freeradius", "debian"
    except Exception:
        pass

    return "freeradius", "desconocida"


def verificar_dependencias():
    """Comprueba que FreeRADIUS esté instalado e informa sobre la instalación si falta."""
    print(">>> Verificando dependencias del motor de red...")

    servicio, distro = _obtener_configuracion_radius()
    if distro is None:
        print(f"   ✓ FreeRADIUS ({servicio}) encontrado en el sistema.")
        return

    if distro == "fedora":
        instrucciones = "Instálalo en Fedora con: sudo dnf install freeradius freeradius-utils freeradius-sqlite"
    elif distro == "debian":
        instrucciones = "Instálalo en Linux Mint/Ubuntu/Debian con: sudo apt update && sudo apt install freeradius freeradius-utils"
    else:
        instrucciones = (
            "Instálalo según tu distribución:\n"
            "  - Fedora/RHEL: sudo dnf install freeradius freeradius-utils freeradius-sqlite\n"
            "  - Mint/Ubuntu/Debian: sudo apt install freeradius freeradius-utils"
        )

    raise DependenciaFaltanteError(
        f"FreeRADIUS no está instalado en el sistema.\n{instrucciones}"
    )


def iniciar_backend_red():
    """Inicia el servicio FreeRADIUS y arranca el planificador de expiraciones."""
    servicio, _ = _obtener_configuracion_radius()

    print(f">>> Iniciando motor FreeRADIUS ({servicio})...")
    subprocess.run(["sudo", "systemctl", "start", servicio], check=True, capture_output=True, text=True)
    print(f">>> Motor FreeRADIUS ({servicio}) iniciado exitosamente.")

    iniciar_guardián_expiraciones()


def detener_backend_red():
    """Detiene el servicio FreeRADIUS detectado y libera recursos de forma segura."""
    try:
        servicio, _ = _obtener_configuracion_radius()
        print(f">>> Deteniendo motor FreeRADIUS ({servicio})...")
        subprocess.run(["sudo", "systemctl", "stop", servicio], capture_output=True, text=True)
        print(f">>> Motor FreeRADIUS ({servicio}) detenido correctamente.")
    except Exception as e:
        print(f">>> Aviso: No se pudo detener FreeRADIUS automáticamente. Error: {e}")
