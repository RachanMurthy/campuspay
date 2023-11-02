from flask import render_template, url_for, redirect, request, flash, abort
from webapp import app



@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    return render_template("login.html", title='Login')

@app.route("/studentlogin")
def studentlogin():
    return render_template("studentlogin.html", title='Student')


@app.route("/shopkeeperlogin")
def shopkeeperlogin():
    return render_template("shopkeeperlogin.html", title='Shopkeeper')


@app.route("/logout")
def logout():
    return redirect(url_for('login'))

@app.route("/checkout")
def checkout():
    pass