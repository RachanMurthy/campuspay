from webapp import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Unique identifier for a user (e.g., student registration number)
    srn = db.Column(db.String(15), unique=True)

    # User's name
    name = db.Column(db.String(100), nullable=False)

    # User's email (unique)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # User's hashed password
    password = db.Column(db.String(255), nullable=False)

    # Unique RFID identifier
    rfid = db.Column(db.String(50), unique=True)

    # Type of user (e.g., 'student', 'shopkeeper')
    user_type = db.Column(db.String(10), nullable=False)

    # User's public Ethereum wallet address
    wallet = db.Column(db.String(42))

    # keystore for storing wallet password must be unique 
    keystore = db.Column(db.String(100), unique=True)

    # wallet_enable to block or unblock transactions
    wallet_enable = db.Column(db.Boolean, nullable=False, default=True)


    def __repr__(self):
        return f"ID : {self.id} NAME : {self.name} SRN : {self.srn} WALLET : {self.wallet} RFID : {self.rfid}"