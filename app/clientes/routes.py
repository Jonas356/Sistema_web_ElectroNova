from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.clientes import clientes_bp
from app.clientes.models import Cliente
from app.auth.helpers import admin_required

@clientes_bp.route("/")
@login_required
def index():
    clientes = Cliente.query.all()
    return render_template("clientes/index.html", clientes=clientes)

@clientes_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        nombre = request.form["nombre"]
        nit_ci = request.form["nit_ci"]
        telefono = request.form.get("telefono")

        if Cliente.query.filter_by(nit_ci=nit_ci).first():
            flash("La cédula o NIT ingresado ya existe", "warning")
            return redirect(url_for("clientes.create"))

        nuevo_c = Cliente(nombre=nombre, nit_ci=nit_ci, telefono=telefono)
        db.session.add(nuevo_c)
        db.session.commit()
        flash("Cliente registrado exitosamente.", "success")
        return redirect(url_for("clientes.index"))
    return render_template("clientes/create.html")

@clientes_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == "POST":
        nit_nuevo = request.form["nit_ci"]

        if nit_nuevo != cliente.nit_ci:
            if Cliente.query.filter_by(nit_ci=nit_nuevo).first():
                flash("El nuevo NIT o Cédula ya pertenece a otro cliente.", "danger")
                return redirect(url_for("clientes.edit", id=id))

        cliente.nombre = request.form["nombre"]
        cliente.nit_ci = nit_nuevo
        cliente.telefono = request.form.get("telefono")

        db.session.commit()
        flash(f"Datos de '{cliente.nombre}' actualizados correctamente.", "success")
        return redirect(url_for("clientes.index"))
        
    return render_template("clientes/edit_cliente.html", cliente=cliente)

@clientes_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
@admin_required 
def delete_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    try:
        db.session.delete(cliente)
        db.session.commit()
        flash(f"Cliente '{cliente.nombre}' eliminado de los directorios.", "success")
    except Exception:
        db.session.rollback()
        flash("No se puede eliminar el cliente porque posee un historial de facturas registradas.", "danger")
        
    return redirect(url_for("clientes.index"))