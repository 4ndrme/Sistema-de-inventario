from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relación uno a muchos: Una categoría tiene muchos productos
    productos = db.relationship('Producto', backref='categoria', lazy=True)

    def __repr__(self):
        return f"<Categoria {self.nombre}>"

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False, unique=True)
    nombre = db.Column(db.String(150), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    activo = db.Column(db.Boolean, default=True)
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Clave foránea que conecta con la tabla categorias
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)

    def __repr__(self):
        return f"<Producto {self.codigo} - {self.nombre}>"