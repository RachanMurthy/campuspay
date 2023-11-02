from flask import render_template, url_for, redirect, request, flash, abort
from .forms import LoginForm
from .models import User
from webapp import app, db
from flask_login import login_user, current_user, logout_user


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

@app.route("/studentlogin")
def studentlogin():
    if current_user.is_authenticated and current_user.user_type == 'STUDENT':
        return render_template("studentlogin.html", title='Student')
    else:
        # Handle unauthorized access for shopkeepers or other roles
        abort(404)

@app.route("/shopkeeperlogin")
def shopkeeperlogin():
    if current_user.is_authenticated and current_user.user_type == 'SHOPKEEPER':        
        return render_template("shopkeeperlogin.html", title='Shopkeeper')
    else:
        # Handle unauthorized access for students or other roles
        abort(404)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/checkout")
def checkout():
    pass