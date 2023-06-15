
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, request, abort
from init import db
from blueprints.auth_bp import admin_required, admin_or_owner_required
from models.card import Card, CardSchema
from datetime import date

cards_bp = Blueprint('cards', __name__, url_prefix='/cards')

#get all cards
@cards_bp.route('/')
@jwt_required()
def all_cards():
    # select * from cards
    stmt = db.select(Card).order_by(Card.title)
    cards = db.session.scalars(stmt).all()
    return CardSchema(many=True).dump(cards)

#get one card 
@cards_bp.route('/<int:card_id>')
def one_card(card_id):
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card:
        return CardSchema().dump(card)
    else: 
        return {'error': 'card not found'}, 404
    
#create a new card 
@cards_bp.route('/', methods=['POST'])
@jwt_required()
def create_card():
    #load the incoming POST data via the schema
    card_info = CardSchema().load(request.json)
    #create a new card instance from the card_info
    card = Card(
        title = card_info['title'],
        description = card_info['description'],
        status = card_info['status'],
        date_created = date.today(),
        user_id = get_jwt_identity()
    )
    db.session.add(card)
    db.session.commit()
    return CardSchema().dump(card), 201 

#update a card 
@cards_bp.route('/<int:card_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_card(card_id):
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    card_info = CardSchema().load(request.json)
    if card:
        admin_or_owner_required(card.user.id)
        card.title = card_info.get('title', card.title),
        card.description = card_info.get('description', card.description),
        card.status = card_info.get('status', card.status),
        db.session.commit()
        return CardSchema().dump(card)
    else: 
        return {'error': 'card not found'}, 404
    
#delete a card 
@cards_bp.route('/<int:card_id>', methods=['DELETE'])
@jwt_required()
def delete_card(card_id):
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card:
        admin_or_owner_required(card.user.id)
        db.session.delete(card)
        db.session.commit()
        return {}, 200
    else: 
        return {'error': 'card not found'}, 404
    


