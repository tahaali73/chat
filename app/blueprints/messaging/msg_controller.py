from flask import Blueprint
from .events import *

from app.blueprints.messaging.msg_model import Msg_model

msg_bp = Blueprint("messaging",__name__,template_folder="templates")

model = Msg_model()

@msg_bp.route('/chat')
def msg():
    return model.msg()

