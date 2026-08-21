from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# TABLA 1: Control de Accesos y Roles
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), nullable=False) # Roles: Operador, Supervisor, Auditor
    activo = db.Column(db.Boolean, default=True)

    # Métodos integrados para cifrar y verificar contraseñas
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# TABLA 2: Inventario Híbrido
class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(50), nullable=False) # Físico, Perecible, Digital
    stock = db.Column(db.Integer, default=0)
    
    # Atributos específicos
    fecha_caducidad = db.Column(db.Date, nullable=True) # Vital para FEFO
    ruta_documento = db.Column(db.String(255), nullable=True) # Para Hojas de Seguridad (PDF)
    activo = db.Column(db.Boolean, default=True)

# TABLA 3: Motor Transaccional (Trazabilidad)
class Movimiento(db.Model):
    __tablename__ = 'movimientos'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_movimiento = db.Column(db.String(20), nullable=False) # INGRESO o DESPACHO
    cantidad = db.Column(db.Integer, nullable=False)
    fecha_movimiento = db.Column(db.DateTime, default=datetime.utcnow)
    observacion = db.Column(db.String(255), nullable=True)
    
    # Claves foráneas (Integridad Referencial en SQL Server)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    # Relaciones para facilitar consultas en Flask
    producto = db.relationship('Producto', backref=db.backref('movimientos', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('movimientos', lazy=True))