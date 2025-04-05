from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    username = StringField("Username",
        validators=[DataRequired(), Length(min=3, max=20)],
        render_kw={"placeholder": "Username"},)
    
    email = StringField("Email",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Email"},)
    
    password = PasswordField("Password",
        validators=[DataRequired(), Length(min=8)],
        render_kw={"placeholder": "Password"},)
    
    confirm_password = PasswordField("Confirm Password",
        validators=[DataRequired(), EqualTo("password")],
        render_kw={"placeholder": "Confirm Password"},)
    
    submit = SubmitField("Register")
    
class LoginForm(FlaskForm):
    username = StringField("Username",
        validators=[DataRequired()],
        render_kw={"placeholder": "Username"},)
    
    password = PasswordField("Password",
        validators=[DataRequired()],
        render_kw={"placeholder": "Password"},)
    
    submit = SubmitField("Sign In")