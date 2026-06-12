"""Gestión de la base de datos y compatibilidad con FreeRADIUS."""

import secrets
import sqlite3
import string
from datetime import datetime
from pathlib import Path

DB_NAME = Path("/var/lib/radiusd/radius_keys.db")


def init_db():
    """Crea la base de datos, la vista para FreeRADIUS, tablas dummy y configura WAL."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME.as_posix(), timeout=30)
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()

        # 1. Crear tu tabla nativa si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS keys (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                access_key          TEXT    UNIQUE,
                password            TEXT,
                status              TEXT,
                fecha_inicio        TEXT,
                duracion_minutos    INTEGER,
                mac_address         TEXT    DEFAULT NULL
            )
        """)

        # 2. CREAR LA VISTA TRADUCTORA PARA FREERADIUS (radcheck)
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS radcheck AS
            SELECT
                id,
                access_key AS username,
                'Cleartext-Password' AS attribute,
                ':=' AS op,
                password AS value
            FROM keys
            WHERE status = 'active';
        """)

        # 3. CREAR TABLAS DUMMY PARA EVITAR ERRORES DE COMPATIBILIDAD
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS radreply (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT,
                attribute   TEXT,
                op          TEXT,
                value       TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS radusergroup (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT,
                groupname   TEXT,
                priority    INTEGER
            )
        """)

        conn.commit()
        print("[DB SYSTEM] Base de datos optimizada con tablas de compatibilidad RADIUS.")
    except Exception as e:
        print(f"[DB INIT ERROR] No se pudo inicializar la base de datos: {e}")
    finally:
        if conn:
            conn.close()

def registrar_llave(user_id, minutos):
    """Guarda usuario y contraseña garantizando el cierre de la conexión pase lo que pase."""
    password = generar_contraseña_segura()
    conn = None  # Inicializamos la variable fuera para que exista en el bloque 'finally'
    try:
        inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Conexión robusta con 30 segundos de tolerancia a esperas
        conn = sqlite3.connect(DB_NAME.as_posix(), timeout=30)
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO keys (
                access_key, password, status, fecha_inicio, duracion_minutos
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, password, "active", inicio, minutos),
        )
        conn.commit()
        print(f"[DB SYSTEM] ✓ Usuario '{user_id}' insertado correctamente.")
        return password

    except sqlite3.IntegrityError:
        print(f"[DB AVISO] Intento de registro duplicado: El usuario '{user_id}' ya existe.")
        return None
    except Exception as e:
        print(f"[DB ERROR] Error imprevisto al registrar: {e}")
        return None
    finally:
        # AQUÍ ESTÁ EL BLINDAJE: Esto se ejecuta obligatoriamente en éxitos y en errores
        if conn:
            conn.close()
            print("[DB SYSTEM] Conexión cerrada y liberada de forma segura.")

def generar_contraseña_segura(longitud=8):
    """Genera una contraseña alfanumérica segura de longitud fija."""
    caracteres = string.ascii_letters + string.digits
    return "".join(secrets.choice(caracteres) for _ in range(longitud))
