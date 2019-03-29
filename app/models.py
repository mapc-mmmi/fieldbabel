from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    timestamp = db.Column(db.DateTime)
    request = db.relationship('Request', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.email)


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1200))
    timestamp = db.Column(db.DateTime)
    crop_type = db.Column(db.String(40))
    season = db.Column(db.String(4))
    processed = db.Column(db.Boolean)
    processed_time = db.Column(db.DateTime)
    request_queued = db.Column(db.Boolean)
    link = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Request %r>' % (self.body)
