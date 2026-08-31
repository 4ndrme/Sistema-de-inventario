from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
# TABLA 1: Control de Accesos y Roles
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='Operador') # Roles: Operador, Supervisor, Auditor
    activo = db.Column(db.Boolean, default=True)

    # Métodos integrados para cifrar y verificar contraseñas
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
# TABLA 2: Inventario Híbrido (POO Avanzada)
class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, default=0)
    activo = db.Column(db.Boolean, default=True)

    __mapper_args__ = {
        'polymorphic_on': tipo,
        'polymorphic_identity': 'Generico'
    }

    # 1. ENCAPSULAMIENTO ESTRICTO: Interceptor de asignación
    @validates('stock')
    def validar_stock(self, key, value):
        if value < 0:
            raise ValueError(f"Violación de regla de negocio: El stock de '{self.nombre}' no puede ser negativo.")
        return value

    # 2. POLIMORFISMO BASE: Regla de negocio estándar
    def requiere_atencion(self):
        """Devuelve True si el producto necesita reabastecimiento o revisión"""
        return self.stock < 50

    def generar_mensaje_alerta(self):
        """Mensaje por defecto (Polimorfismo Base)"""
        return f"ALERTA DE STOCK: El material '{self.nombre}' ha alcanzado un nivel de inventario crítico (Stock disponible: {self.stock} unidades)."

# --- CLASES HIJAS---

class ProductoFisico(Producto):
    __mapper_args__ = {'polymorphic_identity': 'Físico'}
    ruta_documento = db.Column(db.String(255), nullable=True)

    # . POLIMORFISMO: Sobreescritura de reglas por tipo
    def requiere_atencion(self):
        return self.stock < 100

class ProductoPerecible(Producto):
    __mapper_args__ = {'polymorphic_identity': 'Perecible'}
    fecha_caducidad = db.Column(db.Date, nullable=True)

    # 4. POLIMORFISMO: Sobreescritura de reglas por tipo
    def requiere_atencion(self):
        alerta_stock = super().requiere_atencion()
        
        if not self.fecha_caducidad:
            return alerta_stock
            

        dias_restantes = (self.fecha_caducidad - datetime.utcnow().date()).days
        alerta_caducidad = dias_restantes < 30
        
        # Requiere atención si falla el stock O si está a punto de caducar
        return alerta_stock or alerta_caducidad
    def generar_mensaje_alerta(self):
        """Mensaje especializado (Polimorfismo Compuesto)"""
        if not self.fecha_caducidad:
            return super().generar_mensaje_alerta()
            
        dias_restantes = (self.fecha_caducidad - datetime.utcnow().date()).days
        
        # Evalúa si sufre de ambos problemas (Stock bajo y a punto de caducar)
        if dias_restantes < 30 and super().requiere_atencion():
            return f"ALERTA DOBLE: El material '{self.nombre}' caduca en {dias_restantes} días Y tiene stock crítico ({self.stock} unidades)."
        
        # Evalúa si es solo por caducidad
        elif dias_restantes < 30:
            return f"ALERTA DE CADUCIDAD: El material '{self.nombre}' está próximo a caducar en {dias_restantes} días. (Stock actual: {self.stock} unidades)."
            
        # Si la fecha está bien, asume que la alerta fue por stock
        return super().generar_mensaje_alerta()

    

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