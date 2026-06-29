from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.ventas import ventas_bp
from app.ventas.models import Venta, DetalleVenta
from app.inventario.models import Producto, HistorialStock
from app.clientes.models import Cliente

@ventas_bp.route("/")
@login_required
def index():
    ventas = Venta.query.all()
    return render_template("ventas/index.html", ventas=ventas)

@ventas_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        cliente_id = int(request.form["cliente_id"])
        producto_id = int(request.form["producto_id"])
        cantidad = int(request.form["cantidad"])

        producto = Producto.query.get_or_404(producto_id)
        if producto.stock < cantidad:
            flash(f"Stock insuficiente para {producto.nombre}", "danger")
            return redirect(url_for("ventas.create"))

        producto.stock -= cantidad
        total_operacion = producto.precio * cantidad

        nueva_venta = Venta(cliente_id=cliente_id, usuario_id=current_user.id, total=total_operacion)
        db.session.add(nueva_venta)
        db.session.commit()

        detalle = DetalleVenta(venta_id=nueva_venta.id, producto_id=producto.id, cantidad=cantidad, precio_unitario=producto.precio)
        historial = HistorialStock(producto_id=producto.id, cantidad_cambio=-cantidad, tipo_movimiento="VENTA")
        
        db.session.add(detalle)
        db.session.add(historial)
        db.session.commit()

        flash("Venta efectuada y stock actualizado", "success")
        return redirect(url_for("ventas.index"))

    clientes = Cliente.query.all()
    productos = Producto.query.filter(Producto.stock > 0).all()
    return render_template("ventas/create.html", clientes=clientes, productos=productos)

@ventas_bp.route("/detail/<int:id>")
@login_required
def detail(id):
    venta = Venta.query.get_or_404(id)
    return render_template("ventas/detail.html", venta=venta)