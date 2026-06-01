from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Initialize extensions without app (they will be configured later)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'  # where to redirect if not logged in
login_manager.login_message = 'Please log in to access this page.'

def create_app(config_class=Config):
    """Application factory: creates and configures the Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Import and register blueprints (routes)
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    return app