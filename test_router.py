"""Caso de prueba manual para el controlador TP-Link."""

import sys
import time

# Aseguramos que Python pueda encontrar el módulo dentro de 'src'
from redes_project.router_control import TPLinkController


def ejecutar_prueba():
    print("=" * 50)
    print(" INICIANDO PRUEBA AISLADA DEL CONTROLADOR TP-LINK ")
    print("=" * 50)

    # 1. Instanciar el controlador
    controlador = TPLinkController()

    # 2. Definir una MAC de prueba
    # (Usa la MAC de tu teléfono conectado al Wi-Fi para ver el resultado real)
    mac_prueba = "B8:A8:25:8E:C2:40"

    print(f"\n[PASO 1] Intentando AGREGAR la MAC {mac_prueba} a la lista negra...")
    exito_bloqueo = controlador.agregar_a_lista_negra(mac_prueba)

    if exito_bloqueo:
        print("\n[OK] El router procesó la solicitud de bloqueo.")
        print("-> Revisa tu teléfono. Debería haberse desconectado del Wi-Fi.")
    else:
        print("\n[ERROR] No se pudo agregar la MAC. Revisa los selectores o las credenciales.")
        sys.exit(1)

    # Esperamos 10 segundos para que verifiques el bloqueo antes de removerlo
    print("\nEsperando 10 segundos antes de levantar el castigo...")
    time.sleep(10)

    print(f"\n[PASO 2] Intentando REMOVER la MAC {mac_prueba} de la lista negra...")
    exito_desbloqueo = controlador.remover_de_lista_negra(mac_prueba)

    if exito_desbloqueo:
        print("\n[OK] El router removió la MAC de la lista negra con éxito.")
        print("-> Tu teléfono ya debería poder reconectarse a la red.")
    else:
        print("\n[ERROR] Falló la remoción de la lista negra.")

    print("\n" + "=" * 50)
    print(" PRUEBA FINALIZADA ")
    print("=" * 50)

if __name__ == "__main__":
    ejecutar_prueba()
