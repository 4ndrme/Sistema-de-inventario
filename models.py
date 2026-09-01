from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# TABLA 1: Configuración Global (Ubicada arriba para lectura limpia)
class ConfiguracionSistema(db.Model):
    __tablename__ = 'configuracion'

    id = db.Column(db.Integer, primary_key=True)
    correo_alertas = db.Column(db.String(120), nullable=False, default="michaelandresqc@gmail.com")
    dias_alerta_caducidad = db.Column(db.Integer, nullable=False, default=30)
    umbral_stock_critico = db.Column(db.Integer, nullable=False, default=50)

# TABLA 2: Control de Accesos y Roles
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='Operador')
    activo = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
# TABLA 3: Inventario Híbrido (POO Avanzada)
# CLASE PADRE
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

    #  ENCAPSULAMIENTO
    @validates('stock')
    def validar_stock(self, key, value):
        if value < 0:
            raise ValueError(f"Violación de regla de negocio: El stock de '{self.nombre}' no puede ser negativo.")
        return value

    #  POLIMORFISMO
    def requiere_atencion(self):
        config = ConfiguracionSistema.query.first()
        limite = config.umbral_stock_critico if config else 50
        return self.stock < limite

    def generar_mensaje_alerta(self):
        return f"ALERTA DE STOCK: El material '{self.nombre}' ha alcanzado un nivel de inventario crítico (Stock disponible: {self.stock} unidades)."

# --- CLASES HIJAS
class ProductoFisico(Producto):
    __mapper_args__ = {'polymorphic_identity': 'Físico'}
    ruta_documento = db.Column(db.String(255), nullable=True)

class ProductoPerecible(Producto):
    __mapper_args__ = {'polymorphic_identity': 'Perecible'}
    fecha_caducidad = db.Column(db.Date, nullable=True)

    # POLIMORFISMO: Sobreescritura de reglas combinando stock y caducidad dinámica
    def requiere_atencion(self):
        alerta_stock = super().requiere_atencion()
        
        if not self.fecha_caducidad:
            return alerta_stock
            
        config = ConfiguracionSistema.query.first()
        limite_dias = config.dias_alerta_caducidad if config else 30

        dias_restantes = (self.fecha_caducidad - datetime.utcnow().date()).days
        alerta_caducidad = dias_restantes < limite_dias
        
        return alerta_stock or alerta_caducidad

    def generar_mensaje_alerta(self):
        if not self.fecha_caducidad:
            return super().generar_mensaje_alerta()
            
        config = ConfiguracionSistema.query.first()
        limite_dias = config.dias_alerta_caducidad if config else 30
        dias_restantes = (self.fecha_caducidad - datetime.utcnow().date()).days
        
        if dias_restantes < limite_dias and super().requiere_atencion():
            return f"ALERTA DOBLE: El material '{self.nombre}' caduca en {dias_restantes} días Y tiene stock crítico ({self.stock} unidades)."
        
        elif dias_restantes < limite_dias:
            return f"ALERTA DE CADUCIDAD: El material '{self.nombre}' está próximo a caducar en {dias_restantes} días. (Stock actual: {self.stock} unidades)."
            
        return super().generar_mensaje_alerta()

class ProductoDigital(Producto):
    __mapper_args__ = {
        'polymorphic_identity': 'Digital'
    }
    enlace_descarga = db.Column(db.String(255), nullable=True)

    # POLIMORFISMO: Productos infinitos
    def requiere_atencion(self):
        return False

# TABLA 4: Motor Transaccional (Trazabilidad)
class Movimiento(db.Model):
    __tablename__ = 'movimientos'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_movimiento = db.Column(db.String(20), nullable=False) 
    cantidad = db.Column(db.Integer, nullable=False)
    fecha_movimiento = db.Column(db.DateTime, default=datetime.utcnow)
    observacion = db.Column(db.String(255), nullable=True)
    
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    producto = db.relationship('Producto', backref=db.backref('movimientos', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('movimientos', lazy=True))