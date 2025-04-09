from flask import render_template
from flask_jwt_extended import get_jwt_identity
from .forms import MessageForm
from .events import socke_handles

socket = socke_handles()

class Msg_model():
    
    def msg(self):
        form = MessageForm()
        user_id = get_jwt_identity()
        socke_handles.connect(user_id=user_id)
        socke_handles.disconnect(user_id=user_id)
        socke_handles.message(user_id)
        return render_template("index.html",form=form)
    
        