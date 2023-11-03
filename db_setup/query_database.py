from webapp import app
from webapp.models import User

# Create the Flask application context
with app.app_context():
    # Query all users from the database
    all_users = User.query.all()

    # Print the users or perform any other operations
    for user in all_users:
        print(f"ID: {user.id}, Name: {user.name}, Email: {user.email} pub_address : {user.wallet}")
