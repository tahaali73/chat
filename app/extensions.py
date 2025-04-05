from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_socketio import SocketIO

jwt = JWTManager()
bcrypt = Bcrypt()
mongo = PyMongo()
socketio = SocketIO()