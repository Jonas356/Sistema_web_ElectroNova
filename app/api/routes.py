from flask import jsonify, request
from app.extensions import db
from app.api import api_bp
from app.inventario.models import Producto

@api_bp.route("/productos/<int:id>", methods=["GET"])
def get_producto_api(id):
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({"error": "No existe el electrodoméstico"}), 404
    return jsonify(producto.to_dict()), 200

@api_bp.route("/productos/<int:id>", methods=["PUT"])
def update_producto_api(id):
    data = request.get_json()
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({"error": "No existe el electrodoméstico"}), 404
    
    producto.nombre = data.get('nombre', producto.nombre)
    producto.precio = float(data.get('precio', producto.precio))
    producto.stock = int(data.get('stock', producto.stock))
    
    db.session.commit()
    return jsonify(producto.to_dict()), 200

@api_bp.route("/productos/<int:id>", methods=["DELETE"])
def delete_producto_api(id):
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({"error": "No existe el electrodoméstico"}), 404
        
    db.session.delete(producto)
    db.session.commit()
    return jsonify({"success": "Producto eliminado del inventario correctamente"}), 200