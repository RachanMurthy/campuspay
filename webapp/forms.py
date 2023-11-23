from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField, ValidationError, IntegerField
from wtforms.validators import DataRequired, Email, NumberRange
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
    submit = SubmitField('LOGIN')

    def validate_user_type_email(self, email):
            # Get the values of user_type and email fields
            user_type = self.user_type.data
            email = email.data

            # Perform your validation logic here
            user = User.query.filter_by(user_type=user_type, email=email).first()

            if not user:
                raise ValidationError('Invalid User Type and Email combination')
            
class AddCreditForm(FlaskForm):
    add_credit_amount = IntegerField(
        'Add Token Amount :',
        validators=[
            DataRequired(),
            NumberRange(min=1, max=5000, message='The amount must be between 0 to 5000')
        ],
        render_kw={"placeholder": "Enter amount to add"}
    )
    submit_add = SubmitField('Add Credit')

class ReadTagForm(FlaskForm):
    read_tag = StringField(
        'Read Tag :',
        validators=[DataRequired()],
        render_kw={"placeholder": "Scan tag here"}
    )
    submit_read = SubmitField('Read Tag')

class SpendCreditsForm(FlaskForm):
    spend_amount = IntegerField(
        'Spend Amount : ',
        validators=[
            DataRequired(),
            NumberRange(min=1, message='The amount must be greater than zero.')
        ],
        render_kw={"placeholder": "Enter amount to spend"}
    )
    submit_spend = SubmitField('Spend Credits')

class WalletEnableForm(FlaskForm):
    walletenable = SubmitField('Block Account')

class CardPinForm(FlaskForm):
    pin = IntegerField(
        'ENTER PIN',
        validators=[
            DataRequired(),
            NumberRange(min=1000, max=9999, message='FOUR DIGIT PIN')
        ],
        render_kw={"placeholder": "PIN : "}
    )
    submit = SubmitField('Submit')
