from init import db, ma 

class Card(db.Model):
    __tablename__ = 'cards'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text())
    status = db.Column(db.String(30))
    date_created = db.Column(db.Date())


class CardSchema(ma.Schema):
    class Meta: 
        fields = ('id', 'title', 'description', 'status', 'date_created')