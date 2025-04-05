from flask import Blueprint, request, jsonify
from app.blueprints.auth.auth_model import Auth_Model
from flask_jwt_extended import jwt_required, verify_jwt_in_request

auth_bp = Blueprint("auth", __name__, template_folder="templates")

model = Auth_Model()

@auth_bp.route('/user/registration',methods=['GET','POST'])
def register_user(): 
    return model.register_user()

@auth_bp.route('/user/login',methods=['GET','POST'])
def login_user():
    return model.login_user()

@auth_bp.route('/refresh', methods=['POST', 'GET'])
@jwt_required(refresh=True)
def token_refresh():
    #if request.method == 'POST':
        refresh_token = request.cookies.get("refresh_token_cookie")
        print(refresh_token)
        return model.token_refresh(refresh_token)

