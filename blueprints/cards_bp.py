
from flask_jwt_extended import jwt_required
from flask import Blueprint
from init import db
from blueprints.auth_bp import admin_required
from models.card import Card, CardSchema

cards_bp = Blueprint('cards', __name__)

@cards_bp.route('/cards')
@jwt_required()
def all_cards():
    admin_required()
    
    # select * from cards
    stmt = db.select(Card).order_by(Card.title)
    cards = db.session.scalars(stmt).all()
    return CardSchema(many=True).dump(cards)