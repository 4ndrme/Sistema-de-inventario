```markdown
# Sistema de Gestión de Almacenes (WMS) Industrial

## Descripción del Sistema
Este proyecto es un Sistema de Gestión de Almacenes (WMS) de grado industrial diseñado para centralizar, controlar y auditar el flujo de inventario[cite: 3, 4]. Desarrollado con una arquitectura basada en eventos, el sistema mitiga los riesgos de discrepancias físicas y despachos no autorizados mediante la aplicación de reglas de negocio estrictas y validaciones en tiempo real[cite: 3, 4]. 

El núcleo del sistema utiliza Programación Orientada a Objetos (POO) y el patrón de Herencia de Tabla Única (Single Table Inheritance) para clasificar dinámicamente el inventario en productos físicos, perecibles y digitales, aplicando polimorfismo para alertas automáticas de caducidad y quiebre de stock[cite: 3, 4]. Toda la trazabilidad está respaldada por un motor transaccional que cumple con las propiedades ACID[cite: 3, 4].

## Arquitectura y Stack Tecnológico
* **Backend:** Python 3.12, Flask 3.0.x[cite: 3, 4].
* **Base de Datos:** Microsoft SQL Server (Motor) y SQL Server Management Studio 19 (Gestión)[cite: 3, 4].
* **ORM:** SQLAlchemy (Mapeo relacional e inyección de dependencias).
* **Frontend:** HTML5, Tailwind CSS 3.4, Flowbite y Jinja2[cite: 3, 4].
* **Exportación de Datos:** `openpyxl` para reportes de auditoría en Excel.

## Requerimientos Previos
Para ejecutar este proyecto en un entorno local, asegúrate de tener instalado:
* [Python 3.12+](https://www.python.org/downloads/)
* [Microsoft SQL Server](https://www.microsoft.com/es-es/sql-server/sql-server-downloads) (Express o Developer)
* Git

## Instalación y Despliegue Local

**1. Clonar el repositorio**
```bash
git clone [https://github.com/tu-usuario/wms-industrial.git](https://github.com/tu-usuario/wms-industrial.git)
cd wms-industrial

```

**2. Creación y activación del Entorno Virtual (Recomendado)**
Para evitar conflictos de dependencias, el proyecto debe ejecutarse dentro de su propio entorno virtual.

* En Windows:

```bash
python -m venv venv
.\venv\Scripts\activate

```

**3. Instalación de Dependencias**
Garantiza que la instalación ocurra estrictamente dentro del entorno virtual utilizando la ruta directa del ejecutable local:

```bash
.\venv\Scripts\python.exe -m pip install -r requirements.txt

```

## Configuración del Servidor y Base de Datos

El sistema delega la persistencia de datos y la integridad transaccional a SQL Server. Para enlazar la aplicación con tu servidor local, sigue estos pasos:

**1. Configuración de Variables de Entorno**
Crea un archivo llamado `.env` en la raíz del proyecto y configura tus credenciales. Usa la siguiente plantilla:

```env
# Conexión a Base de Datos (Ejemplo con autenticación de Windows/Trusted Connection)
DATABASE_URL=mssql+pyodbc://@TU_SERVIDOR/NombreDeTuBaseDeDatos?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes

# Configuración SMTP para alertas de stock y caducidad
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion

```

**2. Inicialización de la Base de Datos**
El sistema requiere una tabla inicial de configuraciones y usuarios base. Ejecuta el script de preparación para crear las tablas, el procedimiento almacenado crítico (`sp_ProcesarMovimiento`) y el registro del Administrador:

```bash
python init_db.py

```

*Nota técnica:* El procedimiento almacenado `sp_ProcesarMovimiento` es vital; encapsula la lógica de restas de stock y registro de historial en un bloque `TRY...CATCH` para prevenir inconsistencias de red.

## Guía de Uso Rápido

Una vez configurado el servidor, levanta la aplicación:

```bash
flask run

```

Accede en tu navegador a `http://127.0.0.1:5000`.

### Control de Accesos (RBAC)

El sistema utiliza un decorador `@requiere_rol` para segmentar los accesos. Al inicializar la base de datos, se generarán automáticamente cuentas de prueba:

* **Supervisor:** Tiene control total. Puede registrar nuevos materiales, modificar umbrales críticos de stock (Configuración del Sistema) y descargar reportes estadísticos en Excel.
* **Auditor:** Perfil de solo lectura enfocado en la trazabilidad. Accede al historial inmutable de movimientos y exportación de inventario.
* **Operador:** Perfil transaccional. Su interfaz se limita exclusivamente a despachar e ingresar stock.

## Autores

* Proyecto desarrollado para la **Escuela Politécnica Nacional**.
* Autores: [Tu Nombre] y [Nombre de tu Compañero].

```

```
