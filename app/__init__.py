from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail
from config.config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
mail = Mail()

def create_app(config_name='development'):
    app = Flask(__name__)
    cfg_obj = config[config_name] if isinstance(config_name, str) else config_name
    app.config.from_object(cfg_obj)
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    CORS(app)
    
    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    
    from app.middleware.error_handler import register_error_handlers
    register_error_handlers(app)
    
    return app

