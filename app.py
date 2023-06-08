from flask import Flask, request, abort
from datetime import date
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from os import environ
from dotenv import load_dotenv
from models.user import User, UserSchema
from models.card import Card, CardSchema
from init import db, ma, bcrypt, jwt

load_dotenv()

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = environ.get('JWT_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URI')

db.init_app(app)
ma.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)


def admin_required(): 
    user_email = get_jwt_identity()
    stmt = db.select(User).filter_by(email=user_email)
    user = db.session.scalar(stmt)
    if not (user and user.is_admin):
        abort(401)

@app.errorhandler(401)
def unauthorized(err):
    return {'error': 'you must be an admin'}, 401


@app.cli.command('create')
def create_db():
    db.drop_all()
    db.create_all()
    print('Tables created successfully')


@app.cli.command('seed')
def seed_db():
    users = [
        User(
            email='admin@spam.com',
            password=bcrypt.generate_password_hash('spinynorman').decode('utf-8'),
            is_admin=True
        ),
        User(
            name='John Cleese',
            email='cleese@spam.com',
            password=bcrypt.generate_password_hash('scratch').decode('utf-8')
        ),
    ]

    # Create an instance of the Card model in memory 
    cards = [
        Card(
            title = 'Start the project',
            description = 'Stage 1 - Create an ERD',
            status = "Done",
            date_created = date.today()
        ),
        Card(
            title = 'ORM Queries',
            description = 'Stage 2 - Implement several queries',
            status = "In Progress",
            date_created = date.today()
        ),
        Card(
            title = 'Marshmallow',
            description = 'Stage 3 - Implement jsonify of models',
            status = "In Progress",
            date_created = date.today()
        ),
    ]


    #Truncate the card table
    db.session.query(Card).delete()
    db.session.query(User).delete()
    #add the card to the session (transaction)
    db.session.add_all(cards)
    db.session.add_all(users)
    # cmmit the transaction to the database
    db.session.commit()
    print('Models Seeded')


@app.route('/register', methods=['POST'])
def register():
    try:
        # Parse, sanitize and validate the incoming JSON data
        # via the schema
        user_info = UserSchema().load(request.json)
        # Create a new User model instance with the schema data
        user = User(
            email=user_info['email'],
            password=bcrypt.generate_password_hash(user_info['password']).decode('utf-8'),
            name=user_info['name']
        )

        # Add and commit the new user
        db.session.add(user)
        db.session.commit()

        # Return the new user, excluding the password
        return UserSchema(exclude=['password']).dump(user), 201
    except IntegrityError:
        return {'error': 'Email address already in use'}, 409


@app.route('/login', methods=['POST'])
def login():
    try:
        stmt = db.select(User).filter_by(email=request.json['email'])
        user = db.session.scalar(stmt)
        if user and bcrypt.check_password_hash(user.password, request.json['password']):
            token = create_access_token(identity=user.email, expires_delta=timedelta(days=1))
            return {'token': token, 'user': UserSchema(exclude=['password']).dump(user)}
        else:
            return {'error': 'Invalid email address or password'}, 401
    except KeyError:
        return {'error': 'Email and password are required'}, 400
    

@app.route('/cards')
@jwt_required()
def all_cards():
    admin_required()

    # user_email = get_jwt_identity()
    # stmt = db.select(User).filter_by(email=user_email)
    # user = db.session.scalar(stmt)
    # if not user.is_admin:
    #     return {'error': 'you must be an admin'}, 401

    # select * from cards;
    stmt = db.select(Card).order_by(Card.title)
    cards = db.session.scalars(stmt).all()
    return CardSchema(many=True).dump(cards)
    

@app.route('/')
def index():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)
