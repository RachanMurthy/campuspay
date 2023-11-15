from flask import render_template, url_for, redirect, request, flash, abort, session
from .forms import LoginForm, AddCreditForm, ReadTagForm, SpendCreditsForm
from .models import User
from webapp import app, db, w3
from flask_login import login_user, current_user, logout_user
from eth_connect import create_wallet, wallet_balance, send_eth_from_genesis, send_eth, get_private_key
import stripe

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
            login_user(user, remember=form.remember.data)
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

        if current_user.wallet is None or current_user.wallet == "":
            password, pub_address, filename  = create_wallet(w3, custom=current_user.rfid) # setting password as rfid card number
            current_user.wallet = pub_address # wallet address
            current_user.keystore = filename # location of file storing the wallet private key (password required to gain access to wallet)
            db.session.commit()
            flash(f"YOUR PASSWORD {password}", "success")
        
        balance = str(wallet_balance(w3,current_user.wallet))

        form_add = AddCreditForm()
        if form_add.validate_on_submit():
            session['add_credit_amount'] = form_add.add_credit_amount.data
            return redirect(url_for('checkout'))
                         
        return render_template("studentlogin.html", title='Student', form_add=form_add, balance=str(balance))
    
    else:
        flash('Please log in to access your account.', 'warning')
        redirect(url_for('login'))


@app.route("/shopkeeperlogin", methods=['GET', 'POST'])
def shopkeeperlogin():
    if current_user.is_authenticated and current_user.user_type == 'SHOPKEEPER':
        if current_user.wallet is None or current_user.wallet == "":
            password, pub_address, filename  = create_wallet(w3, count=12)
            current_user.wallet = pub_address
            current_user.keystore = filename
            db.session.commit()
            flash(f"YOUR PASSWORD {password}", "success")

        
        balance = 0
        spend_tag_form = SpendCreditsForm()
        read_tag_form = ReadTagForm()

        if read_tag_form.validate_on_submit():
            rfid_tag = read_tag_form.read_tag.data
            user_with_rfid = User.query.filter_by(rfid=rfid_tag).first()
            
            if user_with_rfid and user_with_rfid.wallet:
                session['user_with_rfid_wallet'] = user_with_rfid.wallet
                session['user_with_rfid_filename'] = user_with_rfid.keystore
                session['user_with_rfid_password'] = user_with_rfid.rfid
                flash(f"RFID Tag belongs to: {user_with_rfid.name}", "info")
            else:
                flash("RFID Tag not found or user has no wallet address", "danger")
                session['user_with_rfid_wallet'] = None  # Reset the session variable
                session['user_with_rfid_filename'] = None

            if session['user_with_rfid_wallet']:
                balance = wallet_balance(w3, session['user_with_rfid_wallet'])
            else:
                balance = 0

            return render_template("shopkeeperlogin.html", title='Shopkeeper', read_tag_form=read_tag_form, spend_tag_form=spend_tag_form, balance=str(balance))
        
        user_with_rfid_wallet = session.get('user_with_rfid_wallet')

        if spend_tag_form.validate_on_submit():
            spend_amt = spend_tag_form.spend_amount.data
            flash(f"Spend Amount: {spend_amt}", "info")
            customer_pri = get_private_key(w3, session.get('user_with_rfid_filename'), session.get('user_with_rfid_password'))
            try:
                transaction_result=  send_eth(w3, user_with_rfid_wallet, customer_pri, current_user.wallet,spend_amt)
                if transaction_result:
                    flash("Payment successful and ETH sent!", "success")
                        # You might want to log this transaction or update the database here
                else:
                    flash("ETH transfer failed.", "danger")
                            # Handle ETH transfer failure appropriately
            except Exception as e:
                flash("ETH transfer failed.", "danger")

        return render_template("shopkeeperlogin.html", title='Shopkeeper', read_tag_form=read_tag_form, spend_tag_form=spend_tag_form, balance=balance)
    else:
        # Handle unauthorized access for students or other roles
        abort(404)


@app.route("/checkout", methods=['POST', 'GET'])
def checkout():
    if 'add_credit_amount' not in session:
        flash("No credit amount set for checkout.", "danger")
        return redirect(url_for('studentlogin'))

    try:
        success_url = YOUR_DOMAIN + "/success?session_id={CHECKOUT_SESSION_ID}"
        cancel_url = YOUR_DOMAIN + "/cancel"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': 'price_1O6acTSIc1bFL8pWX1dMEAI2',
                    'quantity': session['add_credit_amount']
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


@app.route("/success", methods=['GET', 'POST'])
def payment_success():
    session_id = request.args.get('session_id')
    if session_id:
        try:
            # Retrieve the checkout session to confirm payment
            checkout_session = stripe.checkout.Session.retrieve(session_id)

            # Check if the checkout_session payment status is 'paid' or other success indicators
            if checkout_session.payment_status == 'paid':
                # Calculate the amount to send based on some logic or a predefined value
                # IMPORTANT: Be sure this value is correct and validated to avoid sending incorrect amounts
                # You could use checkout_session metadata or other fields to determine the amount if needed
                amount_to_send = session.pop('add_credit_amount', None)  # Use pop to remove the value after retrieving it

                if amount_to_send:
                    # Assuming send_eth_from_genesis function returns a status or result
                    transaction_result = send_eth_from_genesis(w3, current_user.wallet, amount_to_send)
                    if transaction_result:
                        flash("Payment successful and ETH sent!", "success")
                        # You might want to log this transaction or update the database here
                    else:
                        flash("ETH transfer failed.", "danger")
                        # Handle ETH transfer failure appropriately
                else:
                    flash("No credit amount available for ETH transfer.", "danger")
            else:
                flash("Payment not successful.", "danger")
            
        except stripe.error.StripeError as e:
            # Handle Stripe errors appropriately
            flash("A Stripe error occurred: " + str(e), "danger")
        except Exception as e:
            # Handle general errors appropriately
            flash("An error occurred: " + str(e), "danger")
        finally:
            # This ensures that the user is redirected regardless of the outcome
            # Redirect to a confirmation page or somewhere else as needed
            return redirect(url_for('studentlogin'))
    else:
        flash("Payment session ID was not provided.", "danger")
        return redirect(url_for('studentlogin')) 