from datetime import datetime
from app.extensions import db

class Categoria(db.Model):
    __tablename__ = "categorias"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    productos = db.relationship("Producto", backref="categoria_rel", lazy=True)

class Producto(db.Model):
    __tablename__ = "productos" 
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable=True)

    detalles = db.relationship("DetalleVenta", backref="producto_rel", lazy=True, cascade="all, delete-orphan")
    historiales = db.relationship("HistorialStock", backref="producto_rel", lazy=True, cascade="all, delete-orphan")

    def to_dict(self): 
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio': self.precio,
            'stock': self.stock,
            'categoria': self.categoria_rel.nombre if self.categoria_rel else None
        }

class HistorialStock(db.Model):
    __tablename__ = "historial_stock"
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    cantidad_cambio = db.Column(db.Integer, nullable=False) 
    tipo_movimiento = db.Column(db.String(50), nullable=False) 
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class Proveedor(db.Model):
    __tablename__ = "proveedores"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    contacto = db.Column(db.String(100), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)

    productos = db.relationship("Producto", backref="proveedor_rel", lazy=True)