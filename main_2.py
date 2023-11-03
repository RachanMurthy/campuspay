from webapp import app, w3
from eth_connect import GENESIS_PUB_ADDRESS, wallet_balance, get_private_key, GENESIS_FILE, GENESIS_PASSWORD, send_eth_from_genesis
from webapp.models import User



if __name__ == "__main__":
    # with app.app_context():
    #     # Query all users from the database
    #     all_users = User.query.all()

    #     # Print the users or perform any other operations
    #     for user in all_users:
    #         print(f"ID: {user.id}, Name: {user.name}, Email: {user.email} pub_address : {user.wallet}")
    #         print(type(eth_connect.wallet_balance(w3, user.wallet)))

    with app.app_context():
        # Query all users from the database
        first_user = User.query.get(1)
    print(wallet_balance(w3, GENESIS_PUB_ADDRESS))
    # print(get_private_key(w3, GENESIS_FILE, GENESIS_PASSWORD))
    print(first_user.wallet)
    # print(send_eth_from_genesis(w3, first_user.wallet, 10))
    print(wallet_balance(w3, first_user.wallet))