from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class MessageForm(FlaskForm):
    usernameReciver = StringField("Username", id="reciever_username",
        validators=[DataRequired(), Length(min=1)], 
        render_kw={"placeholder": "Reciever Username"})
    
    message = StringField("message", id="msg",
        validators=[DataRequired(), Length(min=1)],
        render_kw={"placeholder": "message.."})
    
    submit = SubmitField("send", id="send_msg")
    