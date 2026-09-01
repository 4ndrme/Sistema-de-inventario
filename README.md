# Sistema de Gestión de Almacenes (WMS) Industrial

Este repositorio contiene el código fuente del Sistema de Gestión de Almacenes (WMS), un proyecto integrador desarrollado para la **Pontificia Universidad catolica del Ecuador**. El sistema está diseñado para centralizar, auditar y controlar el flujo de inventario industrial en tiempo real, mitigando vulnerabilidades de control manual y garantizando la trazabilidad total de las operaciones.

## 📖 Descripción del Sistema

El WMS es una aplicación web transaccional construida con una arquitectura de servidor cliente. Utiliza **Python (Flask)** en el backend y **Microsoft SQL Server** como motor de base de datos. La interfaz de usuario es responsiva, desarrollada con **Tailwind CSS** y **Flowbite**, y renderizada dinámicamente mediante **Jinja2**.

**Características Core:**

* **Transacciones ACID:** Entradas y salidas de inventario gestionadas a través de un Procedimiento Almacenado (`sp_ProcesarMovimiento`) que previene stock negativo y colapsos de concurrencia.
* **Arquitectura Polimórfica:** Uso del patrón *Single Table Inheritance* (Herencia de Tabla Única) vía SQLAlchemy para clasificar dinámicamente el inventario en Productos Físicos, Perecibles y Digitales.
* **Seguridad RBAC:** Control de acceso basado en roles (Supervisor, Auditor, Operador) manejado mediante decoradores de rutas (`@requiere_rol`).
* **Alertas Automatizadas (Event-Driven):** Notificaciones SMTP en tiempo real cuando el stock de un material cae por debajo del umbral crítico definido dinámicamente en la base de datos.
* **Reportes e Inteligencia de Negocios:** Exportación de historiales de auditoría a formato Excel mediante la librería `openpyxl`.

---

## ⚙️ Requerimientos Previos

Para desplegar este sistema en un entorno local o de producción, el equipo host debe contar con:

* **Python:** Versión 3.10 o superior.
* **Base de Datos:** Microsoft SQL Server (2019 o superior) o SQL Server Express.
* **Driver ODBC:** ODBC Driver for SQL Server (versión 17 o superior) instalado en el sistema operativo para permitir la conexión de Python.
* **Git:** Para la clonación del repositorio.

---

## 🚀 Instalación y Configuración del Entorno (Cómo se usa)

Sigue estos pasos para levantar el proyecto desde cero de manera encapsulada, evitando conflictos con librerías globales.

**1. Clonar el repositorio**

```bash
git clone https://github.com/tu-usuario/wms-industrial.git
cd wms-industrial

```

**2. Crear el Entorno Virtual (venv)**
Crea una "burbuja" de aislamiento para las dependencias del proyecto.

```bash
python -m venv venv

```

**3. Activar el Entorno Virtual**

* En Windows:
```bash
.\venv\Scripts\activate

```



**4. Instalar las Dependencias**
Obliga al sistema a instalar las librerías (Flask, SQLAlchemy, openpyxl, pyodbc, etc.) estrictamente dentro del entorno virtual.

```bash
.\venv\Scripts\python.exe -m pip install -r requirements.txt

```

---

## 🔗 Enlace con el Servidor y Base de Datos

El sistema no utiliza credenciales "quemadas" (hardcoded) en el código por razones de seguridad. Toda la conexión se gestiona a través de variables de entorno.

**1. Preparar SQL Server**
Abre Microsoft SQL Server Management Studio (SSMS) y crea una base de datos vacía:

```sql
CREATE DATABASE WMS_Inventario;

```

**2. Configurar el archivo `.env**`
En la raíz del proyecto (al mismo nivel que `app.py`), crea un archivo llamado `.env` e ingresa tus credenciales locales o del servidor:

```ini
# Configuración de Base de Datos (SQL Server)
# Reemplaza 'NOMBRE_SERVIDOR' por el nombre de tu instancia de SQL Server
DATABASE_URL=mssql+pyodbc://usuario:contraseña@NOMBRE_SERVIDOR/WMS_Inventario?driver=ODBC+Driver+17+for+SQL+Server

# Llave secreta de Flask (Para encriptar las cookies de sesión)
SECRET_KEY=tu_llave_secreta_super_segura

# Configuración del servidor de correos (Alertas SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion

```

**3. Inicializar la Base de Datos y el Motor Transaccional**
Antes de arrancar la aplicación, debes construir las tablas y cargar el Procedimiento Almacenado en SQL Server. Ejecuta el script de inicialización:

```bash
python init_db.py

```

*Nota: Este script creará las tablas `productos`, `movimientos`, `usuarios`, `configuracion_sistema`, y cargará el `sp_ProcesarMovimiento` en tu motor SQL.*

---

## 💻 Ejecución del Sistema

Una vez que el entorno esté activado y la base de datos enlazada, arranca el servidor web local:

```bash
flask run
# o alternativamente: python app.py

```

Abre tu navegador web e ingresa a: `[http://127.0.0.1:5000](http://127.0.0.1:5000)`

### Usuarios de Prueba (Por Defecto)

Si el script `init_db.py` se ejecutó correctamente, tendrás los siguientes usuarios generados para probar los distintos niveles de acceso (RBAC):

| Rol | Usuario (Username) | Contraseña | Permisos Principales |
| --- | --- | --- | --- |
| **Supervisor** | `admin_super` | `admin123` | Control total, crear materiales, editar umbrales en ⚙️ Configuración, ver reportes. |
| **Auditor** | `auditor_ext` | `auditor123` | Solo lectura. Puede ver el catálogo, exportar reportes Excel y revisar trazabilidad. |
| **Operador** | `operador_01` | `operador123` | Mover stock (ingresos/despachos). No tiene acceso a reportes ni creación de items. |

## 📁 Estructura Principal del Proyecto

```text
📦 wms-industrial
 ┣ 📂 static/               # Hojas de estilo personalizadas e imágenes
 ┣ 📂 templates/            # Vistas HTML renderizadas con Jinja2
 ┃ ┣ 📜 base.html           # Plantilla maestra (Navbar responsiva)
 ┃ ┣ 📜 dashboard.html      # Catálogo de productos (Polimorfismo visible)
 ┃ ┗ 📜 movimientos.html    # Formulario transaccional de ingresos/despachos
 ┣ 📜 app.py                # Controlador principal de rutas de Flask
 ┣ 📜 models.py             # Clases POO, SQLAlchemy Models y Herencia de Tabla Única
 ┣ 📜 init_db.py            # Script de creación de tablas, SP y usuarios semilla
 ┣ 📜 requirements.txt      # Listado de dependencias (Ej: flask, openpyxl)
 ┗ 📜 .env                  # Variables de entorno (NO subir a GitHub)

```
