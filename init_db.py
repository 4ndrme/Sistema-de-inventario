from app import app
from models import db, Usuario, ProductoFisico, ProductoPerecible, Movimiento
from datetime import datetime, timedelta

def inicializar_datos():
    with app.app_context():
        print("Limpiando y recreando la base de datos...")
        # db.drop_all() # Descomenta esta línea solo si quieres borrar todo lo anterior
        db.create_all()

        # CREACIÓN DE USUARIOS, basado en roles ---
        print("Creando usuarios...")
        usuarios = [
            Usuario(username="admin_super", rol="Supervisor"),
            Usuario(username="auditor_ext", rol="Auditor"),
            Usuario(username="operador_01", rol="Operador")
        ]
        
        # A todos les pondremos la contraseña "1234" para facilitar la defensa
        for u in usuarios:
            u.set_password("1234")
            db.session.add(u)
        
        db.session.commit() # Guardamos para obtener sus IDs

        # --- 2. CREACIÓN DE PRODUCTOS (Físicos y Perecibles) ---
        print("Creando catálogo de materiales...")
        hoy = datetime.utcnow().date()
        
        productos = [
            # Físico Saludable (Stock > 100)
            ProductoFisico(codigo="MAT-F01", nombre="Cascos de Seguridad Nivel 3", tipo="Físico", stock=250),
            
            # Físico Crítico (Stock < 100) -> Disparará alerta si se despacha
            ProductoFisico(codigo="MAT-F02", nombre="Filtros de Aceite Industrial", tipo="Físico", stock=80),
            
            # Perecible Saludable
            ProductoPerecible(codigo="MAT-P01", nombre="Lote Resina Epoxi 50L", tipo="Perecible", stock=300, fecha_caducidad=hoy + timedelta(days=180)),
            
            # Perecible Crítico por Fecha (< 30 días) -> El Polimorfismo en acción
            ProductoPerecible(codigo="MAT-P02", nombre="Adhesivo de Contacto Rápido", tipo="Perecible", stock=500, fecha_caducidad=hoy + timedelta(days=15)),
            
            # Perecible Crítico por Stock (< 50)
            ProductoPerecible(codigo="MAT-P03", nombre="Reactivo Químico Base", tipo="Perecible", stock=20, fecha_caducidad=hoy + timedelta(days=90))
        ]

        for p in productos:
            db.session.add(p)
        
        db.session.commit()

        # --- 3. CREACIÓN DE HISTORIAL DE MOVIMIENTOS (Para los reportes del Auditor) ---
        print("Generando historial de auditoría...")
        
        # Rescatamos los objetos de la BD para asociarlos
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
        print("¡Base de datos inicializada con éxito! Escenario listo para la defensa.")

if __name__ == "__main__":
    inicializar_datos()