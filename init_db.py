from app import app
from models import db, Categoria, Producto

with app.app_context():
    print("Creando tablas en SQL Server...")
    # db.drop_all() # Descomenta esto si en el futuro necesitas borrar y recrear todo
    db.create_all()
    print("Tablas creadas con éxito.")

    # Crear una categoría y un producto de prueba si no existen
    if not Categoria.query.first():
        cat_electronica = Categoria(nombre="Electrónica")
        db.session.add(cat_electronica)
        db.session.commit() # Guardamos para que se genere el ID de la categoría

        prod_prueba = Producto(
            codigo="ELEC-001",
            nombre="Monitor 24 pulgadas",
            precio=150.00,
            stock=15,
            categoria_id=cat_electronica.id
        )
        db.session.add(prod_prueba)
        db.session.commit()
        print("Datos de prueba insertados.")