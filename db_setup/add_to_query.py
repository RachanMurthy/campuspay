from webapp import db, app
from webapp.models import User

user1 = User(
    srn='R22EK016',
    name='RACHAN MURTHY',
    email='UGCET22016@REVA.EDU.IN',
    password='RAC',
    rfid='0002158252',
    user_type='STUDENT',
)

user2 = User(
    srn='R22EK001',
    name='A CHAITANYA RAJ REDDY',
    email='UGCET22001@REVA.EDU.IN',
    password='ACH',
    rfid='0002347248',
    user_type='STUDENT',
)

user3 = User(
    name='SHOPKEEPER1',
    email='SHOPKEEPER1@REVA.EDU.IN',
    password='SHO',
    user_type='SHOPKEEPER',
)

user4 = User(
    name='GUARD1',
    email='GUARD1@REVA.EDU.IN',
    password='GUA',
    user_type='GUARD',
)


with app.app_context():
    # Create the database tables based on your models
    db.create_all()
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(user4)
    db.session.commit()
