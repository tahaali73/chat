from flask import Flask
from app.blueprints.auth import auth_bp  
from app.blueprints.messaging import msg_bp
from app.blueprints.add_contacts import add_contact_bp
from config import Config
from app.extensions import jwt, bcrypt, mongo, socketio, crf


def create_app():
    app = Flask(__name__)
    
    # configurations
    app.config.from_object(Config)
    
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(msg_bp)
    app.register_blueprint(add_contact_bp)
    
    # EXtensions
    #crf.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mongo.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode="eventlet")
    return app