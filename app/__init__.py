from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail
from config.config import config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
mail = Mail()

def create_app(config_name='development'):
    app = Flask(__name__)
    cfg_obj = config[config_name] if isinstance(config_name, str) else config_name
    app.config.from_object(cfg_obj)
    
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    mail.init_app(app)
    CORS(app)

    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.hotel_routes import hotel_bp
    from app.routes.room_routes import room_bp
    from app.routes.booking_routes import booking_bp
    from app.routes.payment_routes import payment_bp
    from app.routes.review_routes import review_bp
    from app.routes.search_routes import search_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.notification_routes import notification_bp
    from app.routes.discount_routes import discount_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(hotel_bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(discount_bp)
    
    from app.middleware.error_handler import register_error_handlers
    register_error_handlers(app)
    
    return app