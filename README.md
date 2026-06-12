# Sistema de Gestión de Acceso Wi-Fi

Este proyecto implementa un sistema de control de acceso a redes inalámbricas basado en **FreeRADIUS**, una base de datos SQLite y una interfaz de usuario en Python. El backend está diseñado para ser agnóstico y ejecutarse en Linux (con soporte optimizado para Fedora y derivadas de Debian), donde verifica de forma dinámica las dependencias del sistema, administra el ciclo de vida del servicio (`radiusd` o `freeradius`), y arranca un planificador asíncrono que gestiona expiraciones y penalizaciones.

## 🚀 Flujo general del sistema

1. **Verificación:** La aplicación arranca y comprueba mediante el backend que el binario de FreeRADIUS esté disponible en el `$PATH` del sistema, identificando si opera bajo el nombre de `radiusd` (Fedora/RHEL) o `freeradius` (Debian/Ubuntu).
2. **Inicialización:** Se vincula la base de datos local `radius_keys.db` y se utiliza la vista `radcheck` para que FreeRADIUS pueda consultar en tiempo real los usuarios activos y sus credenciales.
3. **Despliegue del Motor:** La aplicación eleva privilegios mediante `sudo` de forma controlada para iniciar el demonio de red (`systemctl start`).
4. **Control e Interfaz:** Se levanta la interfaz gráfica (GUI) construida con CustomTkinter para administrar la creación de llaves de acceso.
5. **Monitoreo (Guardián):** Un hilo asíncrono en segundo plano (`scheduler.py`) inspecciona periódicamente los tokens. Al expirar un tiempo de acceso, se conecta al router mediante la automatización de Playwright y expulsa/bloquea la dirección MAC asociada.
6. **Liberación:** Tras cumplirse el tiempo de penalización en la lista negra, el guardián remueve la MAC del router y limpia el registro de la base de datos local.

---

## 📦 Requisitos del Sistema

* **Python 3.12** o superior.
* **Linux** (Probado y optimizado nativamente en **Fedora Linux**).
* Privilegios de **`sudo`** configurados para el usuario que ejecuta la aplicación (necesario para la gestión de servicios mediante `systemctl`).
* Navegador **Chromium** instalado y accesible para las tareas de automatización de Playwright.

---

## 🔧 Instalación y Configuración del Entorno (Fedora)

Antes de ejecutar la aplicación, es indispensable preparar el entorno de red de Linux para asegurar que el motor FreeRADIUS no aborte su ejecución debido a políticas estrictas de cifrado o permisos de archivos.

### 1. Instalar dependencias del sistema operativo

Instala el servidor RADIUS junto a las utilidades de desarrollo y clientes de prueba:

```bash
sudo dnf install freeradius freeradius-utils
```

### 2. Inicializar los Certificados de Seguridad (Obligatorio)

FreeRADIUS incluye por defecto el módulo EAP-TLS activo. Si las llaves criptográficas de desarrollo no están generadas, el servicio fallará en el arranque (`exit-code`). Para crearlas, ejecuta el script de inicialización elevando privilegios a root:

```bash
sudo -i
cd /etc/raddb/certs/
./bootstrap
exit
```

### 3. Crear el Enlace Simbólico de Compatibilidad

Dado que la aplicación y otros submódulos de red pueden buscar el binario bajo la nomenclatura estándar de Debian (`freeradius`), crea un enlace simbólico apuntando al binario nativo de Fedora (`radiusd`):

```bash
sudo ln -s /usr/sbin/radiusd /usr/bin/freeradius
```

### 4. Configurar Permisos de la Base de Datos Local

La base de datos del proyecto se aloja en el espacio local de trabajo dentro de la carpeta del proyecto (por ejemplo: `~/Escritorio/redes-project/radius_keys.db`).

Para que tanto tu usuario de desarrollo como el demonio de red de Fedora (`radiusd`) tengan capacidades de lectura y escritura simultánea sobre el archivo `.db`, utiliza las variables del sistema (`$USER` y `~`) para ajustar el propietario del grupo y los permisos de forma universal:

```bash
sudo chown $USER:radiusd ~/Escritorio/redes-project/radius_keys.db
sudo chmod 660 ~/Escritorio/redes-project/radius_keys.db
```

### 5. Configurar el Firewall de Fedora

Por defecto, Fedora bloquea conexiones externas directas. Si necesitas que el servidor escuche peticiones externas o de dispositivos de la red local, abre los puertos UDP correspondientes al protocolo RADIUS (`1812` para autenticación y `1813` para contabilidad):

```bash
sudo firewall-cmd --add-service=radius --permanent
sudo firewall-cmd --reload
```

---

## 💻 Instalación y Ejecución del Proyecto

Una vez configurado el sistema operativo, clona y despliega la aplicación de Python:

### 1. Clonar el repositorio

```bash
git clone https://github.com/Ailya45/redes-project.git
cd redes-project
```

### 2. Configurar el entorno virtual e instalar dependencias

Se recomienda el uso del gestor moderno `uv` para automatizar la instalación de paquetes en modo editable:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. Ejecutar la aplicación

Puedes iniciar el flujo completo de la GUI y el backend usando el gestor de tareas:

```bash
uv run start
```

O directamente invocando el módulo central de Python:

```bash
python -m redes_project.main
```

---

## 🧠 Comportamiento de los Módulos del Backend

* **`src/redes_project/backend.py`:** Detecta de forma dinámica la distribución a través de `/etc/os-release` y verifica mediante `shutil.which` la presencia de los ejecutables. Controla el aislamiento del arranque enviando señales limpias a `systemctl start` y `systemctl stop` de acuerdo al entorno detectado.
* **`src/redes_project/database.py`:** Mantiene y actualiza de manera local la base de datos SQLite corporativa, estructurando la tabla principal `keys` y desplegando la vista virtualizada `radcheck` para alimentar las consultas de credenciales de FreeRADIUS en formato `Cleartext-Password`.
* **`src/redes_project/scheduler.py`:** Levanta el daemon que gestiona de manera asíncrona la expiración de las sesiones. Al detectar que una sesión caducó, cambia el estado en la base de datos a `blacklisted`, invoca al controlador del router y, una vez cumplido el tiempo de penalización (configurado por defecto en 1.5 minutos para desarrollo), purga el registro de la red de manera transparente.

---

## 🌐 Automatización del Router

El aislamiento del tráfico de red se delega a las directivas de control web programadas en `src/redes_project/router_control.py` mediante **Playwright**:

* `agregar_a_lista_negra(mac_address)`: Accede a la interfaz web administrativa del enrutador por medio de un navegador headless, se autentica de forma segura, navega al panel de seguridad avanzada y añade la dirección MAC a la lista negra global del dispositivo.
* `remover_de_lista_negra(mac_address)`: Localiza el registro de la dirección física dentro de la tabla interactiva de exclusión y remueve su restricción para reactivar el tráfico de manera instantánea.

> ⚠️ **Nota:** Las variables de entorno críticas como `ROUTER_IP`, `USER`, y `PASS` se configuran internamente en el script. Asegúrate de modificarlas para que coincidan con los selectores de la interfaz de tu router físico.

---

## 🧪 Pruebas Internas de Red (La Prueba Reina)

Si deseas verificar de forma aislada que el motor FreeRADIUS responde de manera correcta a las solicitudes de acceso antes de iniciar la interfaz gráfica, puedes utilizar un cliente emulador de terminal enviando credenciales de prueba preconfiguradas en el entorno local (Usuario: `testing`, Contraseña: `password`, Shared Secret: `testing123`):

```bash
radtest testing password localhost 0 testing123
```

El entorno estará configurado de forma óptima cuando la salida del comando retorne una estructura idéntica a esta:

```text
Sent Access-Request Id 84 to 127.0.0.1:1812 length 77
Received Access-Accept Id 84 from 127.0.0.1:1812 length 73
    Reply-Message = "¡Bienvenido a la red de pruebas!"
```

---

## 🛠️ Herramientas de Calidad de Código

El proyecto implementa linters y validadores estáticos estrictos para garantizar la estabilidad del desarrollo. Puedes ejecutar las baterías de pruebas locales mediante:

```bash
uv run lint   # Inspecciona el estilo con Ruff
uv run check  # Validación de tipos estáticos con Pyright
uv run fix    # Aplica autoformateo al código fuente
```