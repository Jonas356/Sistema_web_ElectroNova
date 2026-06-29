from flask import Blueprint

ventas_bp = Blueprint("ventas", __name__, url_prefix="/ventas", template_folder="templates")

from app.ventas import routes