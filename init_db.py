from app import app
from models import db, Usuario, Producto, Movimiento

with app.app_context():
    print("Eliminando tablas antiguas...")
    # ATENCIÓN: drop_all borra todas las tablas y sus datos. 
    # Solo lo usamos en desarrollo para reiniciar la estructura.
    db.drop_all() 
    
    print("Creando nuevas tablas industriales...")
    db.create_all()
    
    # Crear un usuario Supervisor de prueba
    if not Usuario.query.filter_by(username="supervisor").first():
        supervisor = Usuario(username="supervisor", rol="Supervisor")
        # Aquí se usa el método que encripta la clave
        supervisor.set_password("admin123") 
        db.session.add(supervisor)
        
        # Crear un producto físico de prueba para el WMS
        prod_prueba = Producto(
            codigo="MAT-001",
            nombre="Cajas de Embalaje Tipo A",
            tipo="Físico",
            stock=500
        )
        db.session.add(prod_prueba)
        
        db.session.commit()
        print("Tablas creadas. Usuario 'supervisor' y material de prueba insertados con éxito.")