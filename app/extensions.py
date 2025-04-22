from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_socketio import SocketIO
from flask_wtf import CSRFProtect

crf = CSRFProtect()
jwt = JWTManager()
bcrypt = Bcrypt()
mongo = PyMongo()
socketio = SocketIO()