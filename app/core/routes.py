import io
from flask import render_template, redirect, url_for, Response
from flask_login import login_required, current_user
from app.core import core_bp
from app.inventario.models import Producto
from app.ventas.models import Venta
from app.clientes.models import Cliente
from openpyxl import Workbook
from xhtml2pdf import pisa  

@core_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("core.dashboard"))
    return redirect(url_for("auth.login"))


@core_bp.route("/dashboard")
@login_required
def dashboard():
    kpi_ventas = Venta.query.count()
    kpi_clientes = Cliente.query.count()
    kpi_bajo_stock = Producto.query.filter(Producto.stock <= 4).count()
    
    ultimos_productos = Producto.query.order_by(Producto.id.desc()).limit(3).all()

    if current_user.rol == "Administrador":
        ultimas_ventas = Venta.query.order_by(Venta.id.desc()).limit(4).all()
        total_ingresos = sum(v.total for v in Venta.query.all())
    else:
        ultimas_ventas = Venta.query.filter_by(usuario_id=current_user.id).order_by(Venta.id.desc()).limit(4).all()
        total_ingresos = sum(v.total for v in Venta.query.filter_by(usuario_id=current_user.id).all())

    return render_template(
        "core/dashboard.html",
        total_ventas=kpi_ventas if current_user.rol == "Administrador" else len(ultimas_ventas),
        total_clientes=kpi_clientes,
        productos_bajo_stock=kpi_bajo_stock,
        ultimas_ventas=ultimas_ventas,
        ultimos_productos=ultimos_productos,
        total_ingresos=total_ingresos
    )

@core_bp.route("/reportes")
@login_required
def reportes():
    return render_template("core/reportes.html")


@core_bp.route("/reportes/ventas/excel")
@login_required
def reportes_ventas_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Libro de Ventas"
    
    ws.append(["Código Factura", "Fecha y Hora", "Cliente", "NIT/CI", "Monto Total (Bs.)", "Atendido Por ID"])
    
    ventas = Venta.query.all()
    for v in ventas:
        nombre_cliente = v.cliente_rel.nombre if v.cliente_rel else "Cliente General"
        nit_cliente = v.cliente_rel.nit_ci if v.cliente_rel else "0"
        
        ws.append([
            v.id, 
            v.fecha.strftime('%d/%m/%Y %H:%M'), 
            nombre_cliente, 
            nit_cliente, 
            v.total, 
            v.usuario_id
        ])
        
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=Libro_Ventas_ElectroNova.xlsx"}
    )

@core_bp.route("/reportes/ventas/print")
@login_required
def imprimir_ventas_pdf():
    ventas = Venta.query.all()
    html_contenido = render_template("core/print_ventas.html", ventas=ventas)
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html_contenido), dest=pdf_buffer)
    
    if pisa_status.err:
        return "Error interno del servidor al procesar el documento PDF", 500   
    pdf_buffer.seek(0)

    return Response(
        pdf_buffer,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=Libro_Ventas_ElectroNova.pdf"}
    )