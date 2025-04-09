from flask import Blueprint, request
from app.blueprints.auth.auth_model import Auth_Model
from flask_jwt_extended import jwt_required

auth_bp = Blueprint("auth", __name__, template_folder="templates")

model = Auth_Model()

@auth_bp.route('/user/registration',methods=['GET','POST'],endpoint='registration')
def register_user(): 
    return model.register_user()

@auth_bp.route('/user/login',methods=['GET','POST'],endpoint='login')
def login_user():
    return model.login_user()

@auth_bp.route('/refresh', methods=['GET'],endpoint='refresh')
@jwt_required(refresh=True)
def token_refresh():
    #if request.method == 'POST':
        refresh_token = request.cookies.get("refresh_token_cookie")
        return model.token_refresh(refresh_token)

@auth_bp.route('/user/logout', methods=['GET'])
@jwt_required()
def logout():
    return model.logout_user()
