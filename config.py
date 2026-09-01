import os
import urllib.parse
from dotenv import load_dotenv

# Inicialización de variables de entorno
load_dotenv()
class Config:
    # --- CONFIGURACIÓN DE SEGURIDAD ---
    SECRET_KEY = os.getenv("SECRET_KEY", "llave-secreta-desarrollo")

    # --- PARÁMETROS DE CONEXIÓN (SQL SERVER) ---
    DB_SERVER = os.getenv("DB_SERVER", r"DESKTOP-3285T7A\SQLEXPRESS01")
    DB_NAME = os.getenv("DB_NAME", "inventario_wms") # Nota: Considerar cambiar el nombre a 'inventario_wms' si es posible
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # --- MOTOR DE AUTENTICACIÓN DINÁMICA ---
    if DB_USER and DB_PASSWORD:
        # Autenticación nativa de SQL Server
        params = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD}"
    else:
        # Autenticación integrada de Windows (Trusted Connection)
        params = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};Trusted_Connection=yes;"

    # --- INTEGRACIÓN CON SQLALCHEMY ---
    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(params)}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False