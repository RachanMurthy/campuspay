from webapp import db 
from eth_connect import create_wallet

def create_wallet_for_user(w3, current_user, count, custom=None):
    password, pub_address, filename  = create_wallet(w3, custom=custom, count=count) # setting password as rfid card number
    current_user.wallet = pub_address # wallet address
    current_user.keystore = filename # location of file storing the wallet private key (password required to gain access to wallet)
    db.session.commit()

    return password