from init import db, ma 
from marshmallow import fields, validates_schema
from marshmallow.validate import Length, OneOf, And, Regexp, ValidationError

VALID_STATUSES = ['To Do', 'Done', 'In Progress', 'Testing', 'Deployed']

class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100))
    description = db.Column(db.Text())
    status = db.Column(db.String(30))
    date_created = db.Column(db.Date())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', back_populates='cards')
    comments = db.relationship('Comment', back_populates='card', cascade='all, delete')


class CardSchema(ma.Schema):
    #tell marshmallow to use UserSchema to serialise the 'user' field
    user = fields.Nested('UserSchema', exclude=['password', 'cards', 'comments'])
    comments = fields.List(fields.Nested('CommentSchema', exclude=['card', 'id']))
    title = fields.String(required=True, validate=And(
        Length(min=3, error='title must be at least 3 characters long'),
        Regexp('^[a-zA-Z0-9 ]+$', error='Only letters, numbers and spaces are allowed')
    ))
    description = fields.String(load_default='')
    status = fields.String(load_default=VALID_STATUSES[0])

    @validates_schema()
    def validate_status(self, data, **kwargs):
        status = [x for x in VALID_STATUSES if x.upper() == data['status'].upper()]
        if len(status) == 0:
            raise ValidationError(f'Status must be one of: {VALID_STATUSES}')
        
        data['status'] = status[0]

    class Meta: 
        fields = ('id', 'title', 'description', 'status', 'date_created', 'user', 'comments')
        ordered = True