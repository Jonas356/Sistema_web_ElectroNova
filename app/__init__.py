from flask import Flask
from flask_migrate import Migrate
from app.extensions import db, bcrypt, login_manager

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.auth.models import Usuario
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    from app.core.routes import core_bp
    from app.auth.routes import auth_bp
    from app.inventario.routes import inventario_bp
    from app.clientes.routes import clientes_bp
    from app.ventas.routes import ventas_bp
    from app.api.routes import api_bp

    app.register_blueprint(core_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()

    return app