import secrets
import sqlite3
import string
from datetime import datetime

DB_NAME = "radius_keys.db"


def init_db():
    """Crea la base de datos y aplica el modo WAL para evitar bloqueos."""
    conn = sqlite3.connect(DB_NAME)
    # --- MEJORA: MODO WAL ---
    # Esto permite que FreeRADIUS lea el archivo mientras Python escribe.
    conn.execute("PRAGMA journal_mode=WAL;")

    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            access_key          TEXT    UNIQUE,
            password            TEXT,
            status              TEXT,
            fecha_inicio        TEXT,
            duracion_minutos    INTEGER
        )
    """)
    conn.commit()
    conn.close()


def generar_contraseña_segura(longitud=8):
    """Genera una contraseña aleatoria."""
    caracteres = string.ascii_letters + string.digits
    return "".join(secrets.choice(caracteres) for _ in range(longitud))


def registrar_llave(user_id, minutos):
    """Guarda usuario y contraseña con formato de fecha compatible con SQLite strftime."""
    password = generar_contraseña_segura()
    try:
        # --- MEJORA: FORMATO DE FECHA ---
        # Usamos el formato YYYY-MM-DD HH:MM:SS para que FreeRADIUS lo entienda perfectamente.
        inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DB_NAME)
        # Aseguramos modo WAL en cada conexión
        conn.execute("PRAGMA journal_mode=WAL;")

        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO keys (
                access_key,
                password,
                status,
                fecha_inicio,
                duracion_minutos
            ) VALUES (
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (user_id, password, "active", inicio, minutos),
        )
        conn.commit()
        conn.close()
        return password
    except sqlite3.IntegrityError:
        return None
    except Exception as e:
        print(f"Error en la base de datos: {e}")
        return None
