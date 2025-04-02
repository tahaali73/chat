from flask import Flask
from app.blueprints.auth import auth_bp  
from config import Config
from app.extensions import jwt, bcrypt, mongo

def create_app():
    app = Flask(__name__)
    
    # configurations
    app.config.from_object(Config)
    
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    
    # EXtensions
    jwt.init_app(app)
    bcrypt.init_app(app)
    mongo.init_app(app)
    
    return app