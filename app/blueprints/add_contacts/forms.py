from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class ContactForm(FlaskForm):
    
    name = StringField("Name",
        validators=[DataRequired(), Length(min=3, max=20)],
        render_kw={"placeholder": "Name"},)
    
    username = StringField("Username",
        validators=[DataRequired(), Length(min=3, max=20)],
        render_kw={"placeholder": "Username"},)
    
    submit = SubmitField("Add Contact")