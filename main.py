from webapp import app, w3
import eth_connect
from webapp.models import User


if __name__ == "__main__":
    app.run(debug=True)

    # with app.app_context():
    #     # Query all users from the database
    #     all_users = User.query.all()

    #     # Print the users or perform any other operations
    #     for user in all_users:
    #         print(f"ID: {user.id}, Name: {user.name}, Email: {user.email} pub_address : {user.wallet}")
    #         print(type(eth_connect.wallet_balance(w3, user.wallet)))