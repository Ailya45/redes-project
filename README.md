# Sistema de Gestión de Acceso Wi-Fi

Este proyecto implementa un sistema de control de acceso a redes inalámbricas utilizando el protocolo **RADIUS**. Combina una interfaz gráfica en Windows para la gestión de usuarios y un motor de autenticación robusto en Linux (WSL).

## 🚀 Descripción del Flujo

1. **Windows:** Una App en Python (CustomTkinter) genera llaves de acceso y las guarda en una base de datos SQLite compartida.
2. **WSL (Linux):** El servidor FreeRADIUS monitorea la base de datos y autoriza las conexiones del Router.
3. **Hardware:** El Router actúa como cliente NAS, solicitando validación mediante WPA2-Enterprise.

---

## 💻 Apartado 1: Configuración en Windows

### 1. Requisitos Previos

- Instalación de **Python 3.10+**.
- Instalación de la librería de interfaz:
  ```bash
  pip install customtkinter
  ```

### 2. Activación de WSL (Windows Subsystem for Linux)

Para ejecutar el motor de red, es necesario activar Linux dentro de Windows:

1. Abrir PowerShell como Administrador.
2. Ejecutar el comando:

```powershell
wsl --install
```

3. **Reiniciar la computadora**. Al volver, se abrirá una terminal de Ubuntu; configura tu usuario y contraseña de Linux.

### 3. Preparación de la Base de Datos

El archivo `radius_keys.db` es el puente entre ambos sistemas.

- Asegúrate de que el código Python esté en una ruta sin espacios complejos si es posible (ej. `C:\Proyectos\Wifi\`).
- Copia la ruta de Windows para usarla en el siguiente apartado.

---

## 🐧 Apartado 2: Configuración en Linux (WSL)

Abre la terminal de Ubuntu y sigue estos pasos:

### 1. Instalación de FreeRADIUS

```bash
sudo apt update
sudo apt install freeradius freeradius-utils freeradius-sqlite3 -y
```

### 2. Vinculación con la Base de Datos de Windows

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

### 3. Lógica de Expulsión Automática

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

### 4. Alta del Router (Cliente NAS)

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

### 5. Activación y Modo Debug

Activar el módulo

```bash
# Crear enlace simbólico para activar SQL
sudo ln -s /etc/freeradius/3.0/mods-available/sql /etc/freeradius/3.0/mods-enabled/

# Detener servicio de fondo e iniciar modo visual
sudo service freeradius stop
sudo freeradius -X
```

---

## 🛠 Solución de Problemas

- **Address already in use:** El servicio se inició solo. Usa `sudo service freeradius stop`.
- **Permisos:** Si FreeRADIUS no puede leer la DB, usa:
  `sudo chmod 777 "/mnt/c/Ruta/A/Tu/Archivo.db"`
- **Prueba rápida (sin router):** Abre otra terminal de WSL y escribe:
  `radtest usuario contraseña localhost 0 unefa2026`
