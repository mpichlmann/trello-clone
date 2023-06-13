
from flask_jwt_extended import jwt_required
from flask import Blueprint, request, abort
from init import db
from blueprints.auth_bp import admin_required
from models.card import Card, CardSchema
from datetime import date

cards_bp = Blueprint('cards', __name__, url_prefix='/cards')

#get all cards
@cards_bp.route('/')
@jwt_required()
def all_cards():
    admin_required()
    
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
def create_card():
    card_info = CardSchema().load(request.json)
    card = Card(
        title = card_info['title'],
        description = card_info['description'],
        status = card_info['status'],
        date_created = date.today()
    )
    db.session.add(card)
    db.session.commit()
    return CardSchema().dump(card), 201 

#update a card 
@cards_bp.route('/<int:card_id>', methods=['PUT', 'PATCH'])
def update_card(card_id):
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    card_info = CardSchema().load(request.json)
    if card:
        card.title = card_info.get('title', card.title),
        card.description = card_info.get('description', card.description),
        card.status = card_info.get('status', card.status),
        db.session.commit()
        return CardSchema().dump(card)
    else: 
        return {'error': 'card not found'}, 404
    
#delete a card 
@cards_bp.route('/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card:
        db.session.delete(card)
        db.session.commit()
        return {}, 200
    else: 
        return {'error': 'card not found'}, 404
    


