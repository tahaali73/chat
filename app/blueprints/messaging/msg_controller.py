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
    print(user_id)
    return model.msg(user_id)


