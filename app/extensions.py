from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)
from flask_pymongo import PyMongo

jwt = JWTManager()
bcrypt = Bcrypt()
mongo = PyMongo()