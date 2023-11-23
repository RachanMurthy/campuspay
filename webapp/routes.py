# Standard Library Imports
import stripe

# Related Third Party Imports
from flask import flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user, login_required

# Local Application/Library Specific Imports
from .forms import AddCreditForm, LoginForm, ReadTagForm, SpendCreditsForm, WalletEnableForm
from .models import User
from .utils import create_wallet_for_user
from webapp import app, db, w3, bcrypt
from eth_connect import get_private_key, send_eth, send_eth_from_genesis, wallet_balance, get_transactions_by_address, GENESIS_PUB_ADDRESS

# ADD MORE HANDLING FOR SCHOOL

stripe.api_key = "sk_test_51O6TCjSIc1bFL8pWjYx5i1ZfWQXZEodXz8u1xAD8NCwu1NXPZd7rpTyrtuWTOFr9QXPHrVrKye8ASzNVlK6tXkRG00OEhZqhos"
YOUR_DOMAIN = "http://localhost:5000"


@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        selected_user_type = current_user.user_type

        if selected_user_type == 'STUDENT':
            return redirect(url_for('studentlogin'))
        elif selected_user_type == 'SHOPKEEPER':
            return redirect(url_for('shopkeeperlogin'))

    form = LoginForm()

    if form.validate_on_submit():
        selected_user_type = form.user_type.data # Get the selected user type from the form
        selected_user_email = form.email.data
        user = User.query.filter_by(user_type=selected_user_type, email=selected_user_email).first()

        # After login, redirects to home home which Based on the selected user type, redirect to the appropriate route
        if user and user.password == form.password.data:
            login_user(user, remember=True)

            if selected_user_type == 'STUDENT':
                return redirect(url_for('studentlogin'))
            elif selected_user_type == 'SHOPKEEPER':
                return redirect(url_for('shopkeeperlogin'))
            
        else:
            flash("User not found. Please check username and password", "danger")

    return render_template("login.html", title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/studentlogin", methods=['GET', 'POST'])
def studentlogin():
    if current_user.is_authenticated and current_user.user_type == 'STUDENT':

        form_wallet_enable = WalletEnableForm()
        form_add = AddCreditForm()

        if current_user.wallet is None or current_user.wallet == "":
            password = create_wallet_for_user(w3, current_user, count=4)
            pin_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            current_user.keystore_password = pin_hash
            db.session.commit()
            flash(f"YOUR PASSWORD {password}", "success")

        if current_user.wallet_enable:
            form_wallet_enable.walletenable.label.text = '  Block Account  '
        else:
            form_wallet_enable.walletenable.label.text = 'Unblock Account'
        
        session['wallet'] = current_user.wallet
        balance = str(wallet_balance(w3,session['wallet']))
            
        if form_add.validate_on_submit():
            return redirect(url_for('checkout', add_credit_amount=form_add.add_credit_amount.data))
        
        if form_wallet_enable.validate_on_submit():
            current_user.wallet_enable = not (current_user.wallet_enable)
            db.session.commit()
            return redirect(url_for('studentlogin'))

           
        return render_template("studentlogin.html", title='Student', form_add=form_add,form_wallet_enable=form_wallet_enable, balance=str(balance), user=current_user,wallet_status=current_user.wallet_enable)
    
    else:
        flash('Please log in to access your account.', 'warning')
        return redirect(url_for('login'))


@app.route("/shopkeeperlogin", methods=['GET', 'POST'])
def shopkeeperlogin():
    if current_user.is_authenticated and current_user.user_type == 'SHOPKEEPER':
        
        spend_tag_form = SpendCreditsForm()
        read_tag_form = ReadTagForm()

        if current_user.wallet is None or current_user.wallet == "":
            password = create_wallet_for_user(w3, current_user, count=10)
            pin_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            current_user.keystore_password = pin_hash
            db.session.commit()
            flash(f"YOUR PASSWORD {password}", "success")

        session['wallet'] = current_user.wallet
        balance = 0

        if read_tag_form.validate_on_submit():
            rfid_tag = read_tag_form.read_tag.data
            user_with_rfid = User.query.filter_by(rfid=rfid_tag).first()
            
            if user_with_rfid and user_with_rfid.wallet:

                if user_with_rfid.wallet_enable == True:
                    session['user_with_rfid_wallet'] = user_with_rfid.wallet
                    session['user_with_rfid_filename'] = user_with_rfid.keystore
                    session['user_with_rfid_password'] = user_with_rfid.rfid
                    flash(f"RFID Tag belongs to: {user_with_rfid.name}", "info")

                else:
                    session['user_with_rfid_wallet'] = None
                    session['user_with_rfid_filename'] = None
                    flash("RFID Tag BLOCKED", "danger")
                
            else:
                session['user_with_rfid_wallet'] = None
                session['user_with_rfid_filename'] = None
                flash("RFID Tag not found or user has no wallet address", "danger")

            if session['user_with_rfid_wallet']:
                balance = wallet_balance(w3, session['user_with_rfid_wallet'])
            else:
                balance = 0

            return render_template("shopkeeperlogin.html", title='Shopkeeper', read_tag_form=read_tag_form, spend_tag_form=spend_tag_form, balance=str(balance))
          
        if spend_tag_form.validate_on_submit():
            try:
                spend_amt = spend_tag_form.spend_amount.data
                user_with_rfid_wallet = session.get('user_with_rfid_wallet')

                user_with_rfid = User.query.filter_by(wallet=user_with_rfid_wallet).first()
                filename = user_with_rfid.keystore

                customer_pri = get_private_key(w3, filename, session.get('user_with_rfid_password'))

                transaction_result= send_eth(w3, user_with_rfid_wallet, customer_pri, session['wallet'],spend_amt)

                session['user_with_rfid_wallet'] = None
                session['user_with_rfid_filename'] = None

                if transaction_result:
                    flash("Payment successful and ETH sent!", "success")
                else:
                    flash("ETH transfer failed.", "danger")

            except Exception as e:
                flash(f"ETH transfer failed. {e}", "danger")

        return render_template("shopkeeperlogin.html", title='Shopkeeper', read_tag_form=read_tag_form, spend_tag_form=spend_tag_form, balance=balance)
    
    else:
        flash('Please log in to access your account.', 'warning')
        redirect(url_for('login'))


@app.route("/checkout/<int:add_credit_amount>", methods=['POST', 'GET'])
def checkout(add_credit_amount):
    if current_user.is_authenticated and current_user.user_type == 'STUDENT':
        
        if not add_credit_amount:
            flash("No credit amount set for checkout.", "danger")
            return redirect(url_for('studentlogin'))
        
        elif (add_credit_amount + wallet_balance(w3,session['wallet'])) > 5000:
            flash("Exceeds wallet limit", "danger")
            return redirect(url_for('studentlogin'))

        try:
            success_url = YOUR_DOMAIN + "/success?session_id={CHECKOUT_SESSION_ID}"
            cancel_url = YOUR_DOMAIN + "/cancel"
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': 'price_1O6acTSIc1bFL8pWX1dMEAI2',
                        'quantity': add_credit_amount
                    }
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url
            )
        except Exception as e:
            flash("An error occurred while creating the Stripe checkout session: " + str(e), "danger")
            return redirect(url_for('studentlogin'))

        # Redirect the user to the Stripe Checkout page
        return redirect(checkout_session.url, code=303)
    
    else:
        flash('Please log in to access your account.', 'warning')
        return redirect(url_for('login'))


@app.route("/success", methods=['GET', 'POST'])
def payment_success():
    session_id = request.args.get('session_id')

    if not session_id:
        flash("Payment not successful.", "danger")
        return redirect(url_for('studentlogin'))

    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        if checkout_session.payment_status != 'paid':
            flash("Payment not successful.", "danger")
            return redirect(url_for('studentlogin'))

        amount_to_send = checkout_session.amount_total / 100

        if not amount_to_send:
            flash("Payment not successful.", "danger")
            return redirect(url_for('studentlogin'))

        transaction_result = send_eth_from_genesis(w3, session['wallet'], amount_to_send)

        if transaction_result:
            flash("Payment successful and ETH sent!", "success")
        else:
            flash("ETH transfer failed.", "danger")

    except Exception as e:
        flash(f"Payment not successful. {e}", "danger")

    return redirect(url_for('studentlogin'))


@app.route("/cancel", methods=['GET', 'POST'])
def payment_cancel():
    session_id = request.args.get('session_id')

    if not session_id:
        return redirect(url_for('studentlogin'))
    else:
        return render_template('cancel.html')


@app.route("/transactions", methods=['GET', 'POST'])
@login_required
def transactions():
    user_wallet = current_user.wallet
    tx = get_transactions_by_address(w3, user_wallet)
    for transaction in tx:
        transaction['value'] = w3.from_wei(transaction['value'], 'ether')

        _to = User.query.filter_by(wallet=transaction['to']).first()
        if _to:
            transaction['to'] = _to.name
        elif transaction['to'] == GENESIS_PUB_ADDRESS:
            transaction['to'] = "SCHOOL"
        else:
            transaction['to'] = "UNKNOWN"

        _from = User.query.filter_by(wallet=transaction['from']).first()
        if _from:
            transaction['from'] = _from.name
        elif transaction['from'] == GENESIS_PUB_ADDRESS:
            transaction['from'] = "SCHOOL"
        else:
            transaction['from'] = "UNKNOWN"

    return render_template("transactions.html", title='transactions', tx=tx)


