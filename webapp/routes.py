from flask import render_template, url_for, redirect, request, flash, abort, session
from .forms import LoginForm, AddCreditForm, CheckCreditsForm
from .models import User
from webapp import app, db, w3
from flask_login import login_user, current_user, logout_user
from eth_connect import create_wallet
import stripe

stripe.api_key = "sk_test_51O6TCjSIc1bFL8pWjYx5i1ZfWQXZEodXz8u1xAD8NCwu1NXPZd7rpTyrtuWTOFr9QXPHrVrKye8ASzNVlK6tXkRG00OEhZqhos"

YOUR_DOMAIN = "http://localhost:5000"

class PAYMENTS_:
    payment = 24

user = PAYMENTS_()


@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.user_type == 'STUDENT':
            return redirect(url_for('studentlogin'))
        elif current_user.user_type == 'SHOPKEEPER':
            return redirect(url_for('shopkeeperlogin'))

    form = LoginForm()
    if form.validate_on_submit():
        # Get the selected user type from the form
        selected_user_type = form.user_type.data
        user = User.query.filter_by(user_type=form.user_type.data, email=form.email.data).first()

        # Based on the selected user type, redirect to the appropriate route
        if user:
            if user.password == form.password.data:
                login_user(user, remember=form.remember.data)
                if selected_user_type == 'STUDENT':
                    return redirect(url_for('studentlogin'))
                elif selected_user_type == 'SHOPKEEPER':
                    return redirect(url_for('shopkeeperlogin'))
            else:
                flash("Login Unsuccessful. Please check password", "danger")
        else:
            flash("User not found. Please check username and password", "danger")

    return render_template("login.html", title='Login', form=form)

@app.route("/studentlogin", methods=['GET', 'POST'])  # Accept GET and POST requests
def studentlogin():
    if current_user.is_authenticated and current_user.user_type == 'STUDENT':
        if current_user.wallet is None or current_user.wallet == "":
            password, pub_address, filename  = create_wallet(w3)
            current_user.wallet = pub_address
            current_user.filename = filename
            db.session.commit()
            flash(f"YOUR PASSWORD {password}", "success")

        form_add = AddCreditForm()
        if form_add.validate_on_submit():
            session['add_credit_amount'] = form_add.add_credit_amount.data
            return redirect(url_for('checkout'))
        
        form_check = CheckCreditsForm()
        if form_check.validate_on_submit():
            pass

        return render_template("studentlogin.html", title='Student', form_add=form_add, form_check=form_check)
    else:
        # Handle unauthorized access for shopkeepers or other roles
        abort(404)

@app.route("/shopkeeperlogin")
def shopkeeperlogin():
    if current_user.is_authenticated and current_user.user_type == 'SHOPKEEPER':
        if current_user.wallet is None or current_user.wallet == "":
            password, pub_address, filename  = create_wallet(w3, 12)
            current_user.wallet = pub_address
            current_user.filename = filename
            db.session.commit()
            flash(f"YOUR PASSWORD {password}", "success")

        
        return render_template("shopkeeperlogin.html", title='Shopkeeper')
    else:
        # Handle unauthorized access for students or other roles
        abort(404)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/checkout", methods=['POST', 'GET'])
def checkout():
    if 'add_credit_amount' not in session:
        # Handle the error - maybe redirect back to a different page or show an error message
        flash("No credit amount set for checkout.", "error")
        return redirect(url_for('studentlogin'))

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': 'price_1O6acTSIc1bFL8pWX1dMEAI2',
                    'quantity': session['add_credit_amount']
                }
            ],
            mode="payment",
            success_url=YOUR_DOMAIN + "/success",
            cancel_url=YOUR_DOMAIN + "/cancel"
        )
    except Exception as e:
        return str(e)
    
    return redirect(checkout_session.url, code=303)


