# src/redes_project/scheduler.py
import sqlite3
import threading
import time
from datetime import datetime

from .router_control import TPLinkController

DB_NAME = "/var/lib/radiusd/radius_keys.db"

def verificar_y_limpiar_expiraciones():

    router = TPLinkController()

    print("\n" + "=" * 65)
    print("[SCHEDULER] Guardián de infraestructura activado (Modo Batch Sincronizado).")
    print(f"[SCHEDULER] Monitoreando DB: {DB_NAME}")
    print("=" * 65 + "\n")

    while True:
        # =================================================================
        # FASE 1: DETECTAR TOKENS EXPIRADOS (CONEXIÓN RELÁMPAGO)
        # =================================================================
        tokens_a_expirar = []
        conn = None
        try:
            conn = sqlite3.connect(DB_NAME, timeout=30)
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()

            cursor.execute("SELECT id, access_key, fecha_inicio, duracion_minutos, mac_address FROM keys WHERE status = 'active'")
            rows = cursor.fetchall()

            ahora = datetime.now()
            for row in rows:
                id_db, user, fecha_inicio_str, duracion, mac = row
                fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d %H:%M:%S")
                minutos_transcurridos = (ahora - fecha_inicio).total_seconds() / 60

                if minutos_transcurridos >= duracion:
                    tokens_a_expirar.append((id_db, user, mac))

        except Exception as e:
            print(f"[SCHEDULER DB ERROR - FASE 1]: {e}")
        finally:
            if conn: conn.close()

        # =================================================================
        # FASE 2: EVICCIONES EN ROUTER Y ACTUALIZACIÓN EN LOTE (BULK UPDATE)
        # =================================================================
        if tokens_a_expirar:
            # 1. Ejecutar las expulsiones físicas con la DB totalmente cerrada (Evita locks de Playwright)
            for id_db, user, mac in tokens_a_expirar:
                print(f"\n[ALERTA-EXPIRACIÓN] El token '{user}' ha cumplido su tiempo límite.")
                if mac:
                    try:
                        router.agregar_a_lista_negra(mac)
                    except Exception as e:
                        print(f"[RPA-ROUTER ERROR] Ocurrió una excepción al intentar bloquear {mac}: {e}")
                else:
                    print(f"[SCHEDULER] El usuario '{user}' no vinculó dispositivo (MAC vacía).")

            # 2. Abrir la DB UNA SOLA VEZ para guardar todos los cambios del lote
            try:
                conn = sqlite3.connect(DB_NAME, timeout=30)
                conn.execute("PRAGMA journal_mode=WAL;")
                cursor = conn.cursor()
                ahora_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                for id_db, user, mac in tokens_a_expirar:
                    cursor.execute("UPDATE keys SET status = 'blacklisted', fecha_inicio = ? WHERE id = ?", (ahora_str, id_db))

                conn.commit()
                print(f"[SCHEDULER] ✓ Éxito: {len(tokens_a_expirar)} tokens migrados a 'blacklisted' en la DB.")
            except Exception as e:
                print(f"[SCHEDULER DB ERROR - BATCH EXPIRAR]: {e}")
            finally:
                if conn: conn.close()

        # =================================================================
        # FASE 3: DETECTAR PENALIZACIONES CONCLUIDAS (CONEXIÓN RELÁMPAGO)
        # =================================================================
        tokens_a_liberar = []
        try:
            conn = sqlite3.connect(DB_NAME, timeout=30)
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            cursor.execute("SELECT id, access_key, fecha_inicio, mac_address FROM keys WHERE status = 'blacklisted'")
            rows = cursor.fetchall()

            ahora = datetime.now()
            for row in rows:
                id_db, user, fecha_bl_str, mac = row
                fecha_bl = datetime.strptime(fecha_bl_str, "%Y-%m-%d %H:%M:%S")
                minutos_en_castigo = (ahora - fecha_bl).total_seconds() / 60

                # Tiempo de ban / castigo (Configurado a 1.5 minutos de prueba)
                if minutos_en_castigo >= 1.5:
                    tokens_a_liberar.append((id_db, user, mac))
        except Exception as e:
            print(f"[SCHEDULER DB ERROR - FASE 3]: {e}")
        finally:
            if conn: conn.close()

        # =================================================================
        # FASE 4: REMOCIÓN EN ROUTER Y ELIMINACIÓN ABSOLUTA DE LA DB
        # =================================================================
        if tokens_a_liberar:
            # 1. Remover de la lista negra del router (DB cerrada para no interferir)
            for id_db, user, mac in tokens_a_liberar:
                print(f"\n[ALERTA-PENALIZACIÓN] El tiempo de castigo para '{user}' ha concluido.")
                if mac:
                    try:
                        router.remover_de_lista_negra(mac)
                    except Exception as e:
                        print(f"[RPA-ROUTER ERROR] Ocurrió una excepción al intentar remover {mac}: {e}")

            # 2. Abrir la DB UNA SOLA VEZ para ELIMINAR los tokens y liberar sus nombres
            try:
                conn = sqlite3.connect(DB_NAME, timeout=30)
                conn.execute("PRAGMA journal_mode=WAL;")
                cursor = conn.cursor()

                for id_db, user, mac in tokens_a_liberar:
                    # AJUSTE: Cambiamos el UPDATE por un DELETE definitivo
                    cursor.execute("DELETE FROM keys WHERE id = ?", (id_db,))
                    print(f"[SCHEDULER] ✓ Registro '{user}' purgado de la base de datos.")

                conn.commit()
                print(f"[SCHEDULER] ✓ Éxito: {len(tokens_a_liberar)} registros eliminados por completo. Identificadores liberados.")
            except Exception as e:
                print(f"[SCHEDULER DB ERROR - BATCH LIBERAR]: {e}")
            finally:
                if conn: conn.close()

        # Escaneo pasivo cada 5 segundos
        time.sleep(5)

# =================================================================
# ENTRADAS DE ORQUESTACIÓN ASÍNCRONA PARA EL BACKEND
# =================================================================

def iniciar_guardián_expiraciones():
    """Lanza el bucle en un hilo separado de forma asíncrona (Para integración con la GUI)."""
    hilo = threading.Thread(target=verificar_y_limpiar_expiraciones, daemon=True)
    hilo.start()
    print(">>> [SISTEMA] Planificador de control de acceso asíncrono activado en segundo plano.")

if __name__ == "__main__":
    try:
        verificar_y_limpiar_expiraciones()
    except KeyboardInterrupt:
        print("\n[SCHEDULER] Guardián apagado de forma segura por el administrador.")
