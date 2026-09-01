from app import app
from models import db, Usuario, ProductoFisico, ProductoPerecible, ProductoDigital, Movimiento, ConfiguracionSistema
from datetime import datetime, timedelta

def inicializar_datos():
    with app.app_context():
        print("Limpiando y recreando la base de datos...")
        db.drop_all() 
        db.create_all()

        # --- 1. CONFIGURACIÓN GLOBAL INICIAL ---
        print("Generando parámetros del sistema...")
        config_inicial = ConfiguracionSistema(
            correo_alertas="tucorreo@ejemplo.com", 
            dias_alerta_caducidad=30,
            umbral_stock_critico=50
        )
        db.session.add(config_inicial)

        # --- 2. CREACIÓN DE USUARIOS ---
        print("Creando usuarios...")
        usuarios = [
            Usuario(username="admin_super", rol="Supervisor"),
            Usuario(username="auditor_ext", rol="Auditor"),
            Usuario(username="operador_01", rol="Operador")
        ]
        
        for u in usuarios:
            u.set_password("123456") # Ajustado a 6 caracteres por tu regla de seguridad
            db.session.add(u)
        
        db.session.commit() 

        # --- 3. CREACIÓN DE PRODUCTOS (Físicos, Perecibles y Digitales) ---
        print("Creando catálogo de materiales...")
        hoy = datetime.utcnow().date()
        
        productos = [
            # Físico Normal
            ProductoFisico(codigo="MAT-F01", nombre="Cascos de Seguridad Nivel 3", tipo="Físico", stock=250),
            # Físico Crítico
            ProductoFisico(codigo="MAT-F02", nombre="Filtros de Aceite Industrial", tipo="Físico", stock=80),
            # Perecible Normal
            ProductoPerecible(codigo="MAT-P01", nombre="Lote Resina Epoxi 50L", tipo="Perecible", stock=300, fecha_caducidad=hoy + timedelta(days=180)),
            # Perecible Crítico
            ProductoPerecible(codigo="MAT-P02", nombre="Adhesivo de Contacto Rápido", tipo="Perecible", stock=500, fecha_caducidad=hoy + timedelta(days=15)),
            # Digital (Demostración de Polimorfismo)
            ProductoDigital(codigo="LIC-WIN11", nombre="Licencia Windows 11 Pro", tipo="Digital", stock=1, enlace_descarga="https://wms.local/keys/win11")
        ]

        for p in productos:
            db.session.add(p)
        
        db.session.commit()

        # --- 4. CREACIÓN DE HISTORIAL DE MOVIMIENTOS ---
        print("Generando historial de auditoría...")
        
        op = Usuario.query.filter_by(username="operador_01").first()
        prod_resina = ProductoPerecible.query.filter_by(codigo="MAT-P01").first()
        prod_cascos = ProductoFisico.query.filter_by(codigo="MAT-F01").first()

        movimientos = [
            Movimiento(tipo_movimiento="INGRESO", cantidad=400, observacion="Lote inicial recibido de proveedor", producto_id=prod_resina.id, usuario_id=op.id),
            Movimiento(tipo_movimiento="DESPACHO", cantidad=100, observacion="Requisición para línea de ensamblaje A", producto_id=prod_resina.id, usuario_id=op.id),
            Movimiento(tipo_movimiento="INGRESO", cantidad=300, observacion="Dotación semestral", producto_id=prod_cascos.id, usuario_id=op.id),
            Movimiento(tipo_movimiento="DESPACHO", cantidad=50, observacion="Entrega a nuevo personal", producto_id=prod_cascos.id, usuario_id=op.id)
        ]

        for m in movimientos:
            db.session.add(m)

        db.session.commit()
        print("¡Base de datos inicializada con éxito! Credencial y datos de demostracion.")

if __name__ == "__main__":
    inicializar_datos()