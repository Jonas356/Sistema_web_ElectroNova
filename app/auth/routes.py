from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, bcrypt
from app.auth import auth_bp
from app.auth.models import Usuario, Rol
from app.auth.helpers import admin_required  

@auth_bp.route("/usuarios")
@login_required
@admin_required
def usuarios_index():
    usuarios = Usuario.query.all()
    return render_template("auth/usuarios_index.html", usuarios=usuarios)

@auth_bp.route("/register", methods=["GET", "POST"])
@login_required
@admin_required
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        rol_nombre = request.form.get("rol", "Vendedor")

        user_exists = Usuario.query.filter_by(username=username).first() 
        if user_exists:
            flash("El nombre de usuario ya existe.", "danger") 
            return redirect(url_for("auth.register"))

        rol = Rol.query.filter_by(nombre=rol_nombre).first()
        if not rol:
            rol = Rol(nombre=rol_nombre)
            db.session.add(rol)
            db.session.commit()

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8") 
        nuevo_usuario = Usuario(username=username, password=hashed_password, rol_id=rol.id)
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Personal registrado correctamente en ElectroNova", "success") 
        return redirect(url_for("auth.usuarios_index")) 
    return render_template("auth/register.html")

@auth_bp.route("/usuarios/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    
    if usuario.id == current_user.id:
        flash("Para modificar tus propias credenciales activas, ve al panel de perfil.", "warning")
        return redirect(url_for("auth.usuarios_index"))

    if request.method == "POST":
        username_nuevo = request.form["username"]
        rol_nombre = request.form.get("rol")

        if username_nuevo != usuario.username:
            if Usuario.query.filter_by(username=username_nuevo).first():
                flash("El nombre de usuario ya se encuentra ocupado.", "danger")
                return redirect(url_for("auth.edit_usuario", id=id))
            usuario.username = username_nuevo

        rol = Rol.query.filter_by(nombre=rol_nombre).first()
        if not rol:
            rol = Rol(nombre=rol_nombre)
            db.session.add(rol)
            db.session.commit()
        usuario.rol_id = rol.id

        nueva_pass = request.form.get("password")
        if nueva_pass and nueva_pass.strip() != "":
            usuario.password = bcrypt.generate_password_hash(nueva_pass).decode("utf-8")

        db.session.commit()
        flash(f"Usuario '{usuario.username}' actualizado correctamente", "success")
        return redirect(url_for("auth.usuarios_index"))

    return render_template("auth/edit_usuario.html", usuario=usuario)

@auth_bp.route("/usuarios/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    if usuario.id == current_user.id:
        flash("Operación denegada: No puedes eliminar tu propia cuenta de Administrador.", "danger")
        return redirect(url_for("auth.usuarios_index"))

    try:
        db.session.delete(usuario)
        db.session.commit()
        flash(f"El usuario '{usuario.username}' fue dado de baja del sistema.", "success")
    except Exception as e:
        db.session.rollback()
        flash("No se puede eliminar el usuario porque tiene transacciones de venta asociadas.", "danger")

    return redirect(url_for("auth.usuarios_index"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = Usuario.query.filter_by(username=username).first() 
        if user and bcrypt.check_password_hash(user.password, password): 
            login_user(user) 
            flash("Bienvenido al ecosistema ElectroNova", "success") 
            return redirect(url_for("core.dashboard"))
        
        flash("Credenciales de acceso incorrectas", "danger") 
    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user() 
    return redirect(url_for('auth.login'))