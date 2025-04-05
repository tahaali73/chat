from flask import render_template
from .forms import MessageForm

class Msg_model():
    
    def msg(self):
        form = MessageForm()
        return render_template("index.html",form=form)