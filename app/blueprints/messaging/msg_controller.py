from flask import Blueprint, jsonify
from .events import *
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.blueprints.messaging.msg_model import Msg_model

msg_bp = Blueprint("messaging",__name__,template_folder="templates",static_folder="static")

model = Msg_model()

@msg_bp.route('/chat',endpoint="chat")
@jwt_required()
def msg():
    user_id = get_jwt_identity()
    return model.msg(user_id=user_id)

@msg_bp.route('/get-chat', methods=['POST'],endpoint="get-chat")
@jwt_required()
def getChat():
    data = request.get_json()
    username = data.get('username')
    user_id = data.get('user_id')
    return model.getChat(user_id=user_id,usernmae=username)


@msg_bp.route("/chat_deselected", methods=["POST"],endpoint="chat_deselected")
def chat_deselect():
    return model.handle_chat_deselected()

@msg_bp.route("/get-lastseen/<username>",endpoint="get-lastseen")
def get_lastseen(username):
    return model.get_lastseen(username)
