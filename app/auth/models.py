from flask_login import UserMixin
from app.extensions import db

class Rol(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

    usuarios = db.relationship("Usuario", backref="rol_rel", lazy=True)

class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    rol_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    
    @property
    def rol(self):
        return self.rol_rel.nombre if self.rol_rel else "Vendedor"