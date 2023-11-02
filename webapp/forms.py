from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email
from .models import User

class LoginForm(FlaskForm):
    user_type = SelectField(
        'User Type',
        choices=[('', 'Select user type'), ('STUDENT', 'Student'), ('SHOPKEEPER', 'Shopkeeper')],
        validators=[DataRequired()],
        render_kw={"placeholder": "Select user type"}
    )
    email = StringField('Email',validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def validate_user_type_email(self, email):
            # Get the values of user_type and email fields
            user_type = self.user_type.data
            email = email.data

            # Perform your validation logic here
            user = User.query.filter_by(user_type=user_type, email=email).first()

            if not user:
                raise ValidationError('Invalid User Type and Email combination')
            
    