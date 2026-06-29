from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != "Administrador":
            flash("Acceso denegado: Se requieren permisos de Administrador.", "danger")
            return redirect(url_for("core.dashboard"))
        return f(*args, **kwargs)
    return decorated_function