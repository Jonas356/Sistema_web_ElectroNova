import io
from flask import render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from app.extensions import db
from app.inventario import inventario_bp
from app.inventario.models import Producto, Categoria, HistorialStock, Proveedor
from app.auth.helpers import admin_required 
from xhtml2pdf import pisa

@inventario_bp.route("/")
@login_required
def index():
    productos = Producto.query.all()
    return render_template("inventario/index.html", productos=productos)


@inventario_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required 
def create():
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = float(request.form["precio"])
        stock = int(request.form["stock"])
        categoria_id = int(request.form["categoria_id"])
        
        proveedor_id = request.form.get("proveedor_id")
        if proveedor_id == "" or proveedor_id == "None" or not proveedor_id:
            proveedor_id = None
        else:
            proveedor_id = int(proveedor_id)

        nuevo_p = Producto(
            nombre=nombre, 
            descripcion=descripcion, 
            precio=precio, 
            stock=stock, 
            categoria_id=categoria_id,
            proveedor_id=proveedor_id
        )
        db.session.add(nuevo_p)
        db.session.commit()

        historial = HistorialStock(producto_id=nuevo_p.id, cantidad_cambio=stock, tipo_movimiento="INGRESO")
        db.session.add(historial)
        db.session.commit()

        flash("Producto de ElectroNova añadido con éxito", "success")
        return redirect(url_for("inventario.index"))

    categorias = Categoria.query.all()
    proveedores = Proveedor.query.all()
    return render_template("inventario/create.html", categorias=categorias, proveedores=proveedores)


@inventario_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required 
def edit(id):
    producto = Producto.query.get_or_404(id)
    if request.method == "POST":
        nuevo_stock = int(request.form["stock"])
        diferencia = nuevo_stock - producto.stock

        producto.nombre = request.form["nombre"]
        producto.descripcion = request.form.get("descripcion", "")
        producto.precio = float(request.form["precio"])
        producto.stock = nuevo_stock
        categoria_form = request.form.get("categoria_id")
        if categoria_form:
            producto.categoria_id = int(categoria_form)

        proveedor_id = request.form.get("proveedor_id")
        if proveedor_id == "" or proveedor_id == "None" or not proveedor_id:
            producto.proveedor_id = None
        else:
            producto.proveedor_id = int(proveedor_id)

        if diferencia != 0:
            tipo = "AJUSTE_INGRESO" if diferencia > 0 else "AJUSTE_EGRESO"
            historial = HistorialStock(producto_id=producto.id, cantidad_cambio=abs(diferencia), tipo_movimiento=tipo)
            db.session.add(historial)

        db.session.commit()
        flash(f"Producto '{producto.nombre}' modificado correctamente", "success")
        return redirect(url_for("inventario.index"))

    categorias = Categoria.query.all()
    proveedores = Proveedor.query.all()
    return render_template("inventario/edit.html", producto=producto, categorias=categorias, proveedores=proveedores)

@inventario_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete(id):
    producto = Producto.query.get_or_404(id)
    try:
        db.session.delete(producto)
        db.session.commit()
        flash(f"Producto '{producto.nombre}' removido del sistema con todo su historial.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error crítico en la transacción de borrado: {str(e)}", "danger")
        
    return redirect(url_for("inventario.index"))

@inventario_bp.route("/categoria/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_categoria():
    if request.method == "POST":
        nombre = request.form["nombre"]

        if Categoria.query.filter_by(nombre=nombre).first():
            flash("La categoría ingresada ya existe", "warning")
            return redirect(url_for("inventario.create_categoria"))

        nueva_cat = Categoria(nombre=nombre)
        db.session.add(nueva_cat)
        db.session.commit()

        flash("Categoría de cocina añadida con éxito", "success")
        return redirect(url_for("inventario.index"))

    return render_template("inventario/create_categoria.html")

@inventario_bp.route("/proveedores", methods=["GET"])
@login_required
@admin_required
def proveedores():
    proveedores_lista = Proveedor.query.all()
    return render_template("inventario/proveedores.html", proveedores=proveedores_lista)

@inventario_bp.route("/proveedores/create", methods=["POST"])
@login_required
@admin_required
def create_proveedor():
    try:
        nombre = request.form["nombre"]
        contacto = request.form.get("contacto")
        telefono = request.form["telefono"]
        direccion = request.form.get("direccion")

        nuevo_prov = Proveedor(nombre=nombre, contacto=contacto, telefono=telefono, direccion=direccion)
        db.session.add(nuevo_prov)
        db.session.commit()
        
        flash("Proveedor registrado con éxito", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al registrar: {str(e)}", "danger")
        
    return redirect(url_for("inventario.proveedores"))

@inventario_bp.route("/reporte/excel")
@login_required
@admin_required
def exportar_excel():
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario ElectroNova"
    
    ws.append(["ID", "Nombre de Artículo", "Descripción", "Precio (Bs.)", "Stock Actual", "Categoría", "Proveedor"])
    
    productos = Producto.query.all()
    for p in productos:
        cat = p.categoria_rel.nombre if p.categoria_rel else "Sin Categoría"
        prov = p.proveedor_rel.nombre if p.proveedor_rel else "Compra Directa"
        ws.append([p.id, p.nombre, p.descripcion if p.descripcion else "—", p.precio, p.stock, cat, prov])
        
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=Reporte_Inventario_ElectroNova.xlsx"}
    )

@inventario_bp.route("/reporte/print")
@login_required
@admin_required
def imprimir_pdf():
    productos = Producto.query.all()
    
    html_contenido = render_template("inventario/print_inventario.html", productos=productos)
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html_contenido), dest=pdf_buffer)
    
    if pisa_status.err:
        return "Error al compilar el PDF de inventario", 500       
    pdf_buffer.seek(0)
    
    return Response(
        pdf_buffer,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=Reporte_Inventario_ElectroNova.pdf"}
    )

