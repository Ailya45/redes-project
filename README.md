# Sistema de Gestión de Acceso Wi-Fi

Este proyecto implementa un sistema de control de acceso a redes inalámbricas utilizando el protocolo **RADIUS**. Combina una interfaz gráfica multiplataforma para la gestión de usuarios y un motor de autenticación robusto en Linux (WSL en Windows o nativo en Linux).

## 🚀 Descripción del Flujo

1. **Interfaz gráfica:** Una App en Python (CustomTkinter) genera llaves de acceso y las guarda en una base de datos SQLite compartida.
2. **Motor RADIUS:** El servidor FreeRADIUS monitorea la base de datos y autoriza las conexiones del Router.
3. **Hardware:** El Router actúa como cliente NAS, solicitando validación mediante WPA2-Enterprise.

---

## 💻 Apartado 1: Instalación y ejecución de la aplicación de gestión

La aplicación puede ejecutarse en **Windows** (con WSL activado para FreeRADIUS) o directamente en **Linux**. Se ofrecen dos métodos para ponerla en marcha.

### 1.1 Requisitos previos comunes

- **Python 3.10 o superior**
- Acceso a terminal (PowerShell en Windows, Bash en Linux)
- WSL instalado si estás en Windows (ver Apartado 2)
- FreeRADIUS configurado en WSL/Linux (ver Apartado 2)  
  _La aplicación verifica la presencia de FreeRADIUS antes de abrir la interfaz gráfica. Si no lo encuentra, mostrará un error y no arrancará._

### 1.2 Método A: Usar UV (si ya lo tienes instalado)

[UV](https://docs.astral.sh/uv/) es un gestor de paquetes y entornos ultrarrápido. Si aún no lo tienes, puedes instalarlo con `pip install uv`, pero **estas instrucciones asumen que ya está disponible** en tu sistema.

1. Clona o descarga el proyecto y navega a la carpeta raíz (donde se encuentra `pyproject.toml`).
   ```bash
   git clone https://github.com/Ailya45/redes-project.git
   cd redes-project 
   ```
2. Ejecuta la aplicación:
   ```bash
   uv run start
   ```
   _(El comando `start` está definido en `[project.scripts]` del archivo `pyproject.toml`)_

### 1.3 Método B: Python vanilla (con pip y venv)

1. Clona o descarga el proyecto y navega a la carpeta raíz (donde se encuentra `pyproject.toml`).
   ```bash
   git clone https://github.com/Ailya45/redes-project.git
   cd redes-project 
   ```
2. Crea y activa un entorno virtual (opcional pero recomendado):

   ```powershell
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Instala el proyecto en modo editable (esto lee las dependencias de `pyproject.toml`):
   ```bash
   pip install -e .
   ```
4. Ejecuta la aplicación:
   ```bash
   python -m redes_project.main
   ```

---

## 🐧 Apartado 2: Configuración de FreeRADIUS (Linux / WSL)

Abre la terminal de Ubuntu (o tu distribución WSL) y sigue estos pasos:

### 2.1 Instalación de FreeRADIUS

```bash
sudo apt update
sudo apt install freeradius freeradius-utils freeradius-sqlite3 -y
```

### 2.2 Vinculación con la Base de Datos de Windows

1. Editar el módulo SQL:
   ```bash
   sudo nano /etc/freeradius/3.0/mods-available/sql
   ```
2. Modificar la sección `sqlite` (mapeando `C:` como `/mnt/c/`):

   ```conf
   driver = "rlm_sql_sqlite"

   sqlite {
       # Ejemplo: si tu ruta en Windows es C:\Users\Bermys\Proyecto
       filename = "/mnt/c/Users/TU_USUARIO/RUTA_PROYECTO/radius_keys.db"
   }
   ```

### 2.3 Lógica de Expulsión Automática

Editar el archivo de consultas para que el servidor calcule el tiempo restante:

```bash
sudo nano /etc/freeradius/3.0/mods-config/sql/main/sqlite/queries.conf
```

Buscar `authorize_reply_query` y reemplazar por:

```sql
authorize_reply_query = "SELECT id, access_key, 'Session-Timeout' AS attribute, \
((duracion_minutos * 60) - (strftime('%%s','now', 'localtime') - strftime('%%s', fecha_inicio))) AS value, \
'=' AS op FROM keys WHERE access_key = '%%{User-Name}'"
```

### 2.4 Alta del Router (Cliente NAS)

```bash
sudo nano /etc/freeradius/3.0/clients.conf
```

Añadir al final:

```conf
client router_unefa {
    ipaddr = *
    secret = unefa2026
}
```

### 2.5 Activación y Modo Debug

Activar el módulo SQL:

```bash
# Crear enlace simbólico para activar SQL
sudo ln -s /etc/freeradius/3.0/mods-available/sql /etc/freeradius/3.0/mods-enabled/

# Detener servicio de fondo e iniciar en modo visual
sudo service freeradius stop
sudo freeradius -X
```

---

## 🛠 Solución de Problemas

- **Address already in use:** El servicio se inició solo. Usa `sudo service freeradius stop`.
- **Permisos:** Si FreeRADIUS no puede leer la base de datos, otorga permisos amplios (solo en desarrollo):
  ```bash
  sudo chmod 777 "/mnt/c/Ruta/A/Tu/Archivo.db"
  ```
- **Prueba rápida (sin router):** Abre otra terminal de WSL y escribe:
  ```bash
  radtest usuario contraseña localhost 0 unefa2026
  ```
- **La aplicación no inicia y muestra `[ERROR CRÍTICO]`:**  
  Indica que FreeRADIUS no fue encontrado. Asegúrate de haber instalado FreeRADIUS en WSL o en Linux nativo y de que el binario `freeradius` esté accesible. En Windows, verifica que WSL esté correctamente instalado y que la distribución Linux tenga FreeRADIUS. La aplicación no arrancará hasta que esta dependencia esté resuelta.
