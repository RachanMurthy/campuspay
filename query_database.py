from webapp import app
from webapp.models import User

# Create the Flask application context
with app.app_context():
    # Query all users from the database
    all_users = User.query.all()

    # Print the users or perform any other operations
    for user in all_users:
        print(f"ID: {user.id}, Name: {user.name}, Email: {user.email} pub_address : {user.wallet}")

    # You can also perform specific queries, for example, to find a user by email
    user_by_email = User.query.filter_by(email='UGCET22016@REVA.EDU.IN').first()
    if user_by_email:
        print(f"User found by email: {user_by_email.name}")