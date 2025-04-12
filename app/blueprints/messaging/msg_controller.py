from flask import Blueprint, jsonify
from .events import *
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.blueprints.messaging.msg_model import Msg_model

msg_bp = Blueprint("messaging",__name__,template_folder="templates")

model = Msg_model()

@msg_bp.route('/chat',endpoint="chat")
@jwt_required()
def msg():
    user_id = get_jwt_identity()
    return model.msg(user_id)

@msg_bp.route('/check_token_expiry',endpoint="check_token_expiry")
@jwt_required()
def check():
    return jsonify({'msg': "token is working"})
