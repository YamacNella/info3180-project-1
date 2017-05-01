from app import db, app
from werkzeug.security import generate_password_hash, check_password_hash

class Profiles(db.Model):
    userid = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30))
    name = db.Column(db.String(130))
    image = db.Column(db.String(30))
    age = db.Column(db.Integer)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    profile_added_on = db.Column(db.DateTime)
    wishlist = db.relationship('Wishlist', backref='user', lazy='dynamic')
    
    def __init__(self, userid, username, name, age, image, email, password, profile_added_on):
        self.userid = userid
        self.username = username
        self.name = name
        self.age = age
        self.image = image
        self.email = email
        self.password = password
        self.profile_added_on = profile_added_on
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
            try:
                return unicode(self.userid)
            except NameError:
                return str(self.userid)
    
    def __repr__(self):
        return'<Profile %r>' % self.username
        
        
class Wishlist(db.Model):
    itemid  = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(5000))
    url = db.Column(db.String(500))
    thumbnailurl = db.Column(db.String(500))
    userid = db.Column(db.Integer, db.ForeignKey('profiles.userid'))
    
    def __init__(self, itemid, title, description, url, thumbnailurl):
        self.itemid = itemid
        self.title = title
        self.description = description
        self.url = url
        self.thumbnail = thumbnailurl
    
    def get_id(self):
        try:
            return unicode(self.item_id)  # python 2 support
        except NameError:
            return str(self.item_id)  # python 3 support
    
    def __repr__(self):
        return '<Item %r>' % self.title    
        

users_wishes = db.Table('users_wishes',
        db.Column('userid', db.Integer, db.ForeignKey('profiles.userid')), 
        db.Column('wishid', db.Integer, db.ForeignKey('wishlist.itemid')))
