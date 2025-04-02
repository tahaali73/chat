from flask import Blueprint
from app.extensions import mongo 

auth_bp = Blueprint("auth", __name__, template_folder="templates")

@auth_bp.route('/')
def auth():
    user = mongo.db.user.find_one({"username": "Tahaali" })
    return str(user)