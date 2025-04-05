from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class MessageForm(FlaskForm):
    socket_id = StringField("Socket Id", id="s_id",
        validators=[DataRequired(), Length(min=1)], 
        render_kw={"placeholder": "Socket id"})
    
    message = StringField("message", id="msg",
        validators=[DataRequired(), Length(min=1)],
        render_kw={"placeholder": "message.."})
    
    submit = SubmitField("send", id="send_msg")
    