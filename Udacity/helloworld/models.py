from google.appengine.ext import db
from utils import make_pw_hash, valid_pw

class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    def as_dict(self):
        time_fmt = '%c'
        d = {'subject': self.subject,
             'content': self.content,
             'created': self.created.strftime(time_fmt),
             'modified': self.modified.strftime(time_fmt)}
        return d

    
class User(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.EmailProperty()
    
    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

    @classmethod
    def by_name(cls, username):
        u = User.all().filter('username =', username).get()
        return u

    @classmethod
    def register(cls, username, pw, email = None):
        pw_hash = make_pw_hash(username, pw)
        if email:
            return User(username = username,
                    password = pw_hash,
                    email = email)
        else:
            return User(username = username,
                        password = pw_hash)

    @classmethod
    def login(cls, username, pw):
        u = cls.by_name(username)
        if u and valid_pw(username, pw, u.password):
            return u

class Wiki(db.Model):
    name = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def by_name(cls, name):
        u = cls.all().filter('name =', name).get()
        return u
