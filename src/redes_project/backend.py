import platform
import subprocess

# 1. MOTOR DE RED (WSL + FREERADIUS)
# ------------------------------------------------------------

class DependenciaFaltanteError(Exception):
    """Excepción personalizada para indicar que falta un componente crítico."""
    pass

def verificar_dependencias():
    """
    Comprueba que las herramientas necesarias (WSL en Windows y FreeRADIUS)
    estén accesibles. Si falta algo esencial, lanza DependenciaFaltanteError.
    """
    sistema = platform.system().lower()
    print(">>> Verificando dependencias del motor de red...")

    if sistema == "windows":
        # Chequeamos si WSL está instalado
        try:
            subprocess.run(["wsl", "--version"], capture_output=True, text=True, check=True)
            print("   ✓ WSL detectado.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise DependenciaFaltanteError(
                "WSL no está instalado o no se encuentra en el PATH.\n"
                "Instálalo desde PowerShell como administrador: wsl --install"
            )

        # Dentro de WSL, verificamos si freeradius está instalado
        try:
            subprocess.run(["wsl", "which", "freeradius"],
                           capture_output=True, text=True, check=True)
            print("   ✓ FreeRADIUS encontrado en WSL.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise DependenciaFaltanteError(
                "FreeRADIUS no se encontró dentro de WSL.\n"
                "Ejecuta 'sudo apt install freeradius' en tu distribución."
            )

    elif sistema == "linux":
        # Verificamos si freeradius está en el sistema
        try:
            subprocess.run(["which", "freeradius"], capture_output=True, text=True, check=True)
            print("   ✓ FreeRADIUS encontrado en el sistema.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise DependenciaFaltanteError(
                "FreeRADIUS no está instalado.\n"
                "Instálalo con: sudo apt install freeradius"
            )
    else:
        raise DependenciaFaltanteError(
            f"Sistema operativo '{sistema}' no soportado para la validación automática."
        )


def iniciar_backend_red():
    """Lanza FreeRADIUS en el entorno adecuado (WSL o Linux) de forma silenciosa."""
    sistema = platform.system().lower()
    try:
        if sistema == "windows":
            # Nota: Se usa 'sudo service freeradius start' para modo producción/segundo plano.
            subprocess.run(["wsl", "sudo", "service", "freeradius", "start"],
                           check=True, capture_output=True, text=True)
            print(">>> Motor FreeRADIUS iniciado en WSL.")
        elif sistema == "linux":
            try:
                subprocess.run(["sudo", "systemctl", "start", "freeradius"],
                               check=True, capture_output=True, text=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                subprocess.run(["sudo", "service", "freeradius", "start"],
                               check=True, capture_output=True, text=True)
            print(">>> Motor FreeRADIUS iniciado en Linux.")
        else:
            print(">>> No se pudo determinar el sistema para iniciar FreeRADIUS.")
    except Exception as e:
        print(f">>> Aviso: No se pudo iniciar FreeRADIUS. ¿WSL activo? ¿Permisos sudo? Error: {e}")
