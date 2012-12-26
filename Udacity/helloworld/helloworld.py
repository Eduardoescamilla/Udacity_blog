from google.appengine.api import memcache
from google.appengine.ext import db
from handler import Handler
from models import Post, User
from rot13 import ROT13
import wiki
import datetime
import logging
import re
import webapp2

class Signup(Handler):
    def render_signup(self, error_username="",
                        error_password="",
                        error_verify="",
                        error_email="",
                        username="",
                        email=""):
        self.render("signup.html", error_username=error_username,
                        error_password=error_password,
                        error_verify=error_verify,
                        error_email=error_email,
                        username=username,
                        email=email)
    def get(self):
        self.render_signup()
        
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        error_username = ""
        error_password = ""
        error_verify = ""
        error_email = ""
        error = False
        if not(username and self.valid_username(username)):
            error_username = "That's not a valid username"
            error = True
        if not(password and self.valid_password(password)):
            error_password = "That's not a valid password"
            error = True
        elif not(verify and self.valid_verify(password, verify)):
            error_verify = "Passwords don't match"
            error = True
        if email and not self.valid_email(email):
            error_email = "That's not a valid email"
            error = True
        if error:
            self.render_signup(error_username, error_password, error_verify, error_email, username, email)
        elif self.exists_username(username):
            error_username = "Username already exists"
            self.render_signup(error_username, error_password, error_verify, error_email, username, email)
        else:            
            user = User.register(username, password, email)
            user.put()
            self.login(user)
            self.redirect("/blog/welcome")
        
    def exists_username(self, username):
        return User.by_name(username)
    
    def valid_username(self, username):
        return re.compile(r"^[a-zA-Z0-9_-]{3,20}$").match(username)
    
    def valid_password(self, password):
        return re.compile(r"^.{3,20}$").match(password)
    
    def valid_verify(self, password, verify):
        return password == verify
    
    def valid_email(self, email):
        return re.compile(r"^[\S]+@[\S]+\.[\S]+$").match(email)

class Login(Handler):
    def get(self):
        self.render("login.html")
    
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        user = User.login(username, password)
        if user:
            self.login(user)
            self.redirect("/blog/welcome")
        else:
            error_login = "Invalid Login"
            self.render("login.html", username=username, error_login=error_login)

class Logout(Handler):
    def get(self):
        self.logout()
        self.redirect("/blog/signup")

class Welcome(Handler):
    def get(self):        
        username = self.user.username
        self.render("welcome.html", username=username)
        
def top_posts(update=None):
    key = "top"
    key_stamp = "top_stamp"
    client = memcache.Client()
    posts = client.get(key)
    stamp = client.get(key_stamp)
    if update or not posts:
        logging.error("DB")
        posts = db.GqlQuery("select * from Post order by created desc limit 10")
        posts = list(posts)
        stamp = datetime.datetime.today()
        client.set(key, posts)
        client.set(key_stamp, stamp)
    return posts, stamp

class Blog (Handler):
    def get(self):
        posts, stamp = top_posts()
        stamp = datetime.datetime.today() - stamp
        self.render("main.html", posts=posts, stamp = stamp)
     
def get_post(post_id):
    key = "permalink%s" %post_id
    key_stamp = "permalink_stamp%s" %post_id
    client = memcache.Client()
    post = client.get(key)
    stamp = client.get(key_stamp)
    if not post:
        logging.error("DB")
        post = Post.get_by_id(int(post_id))
        stamp = datetime.datetime.today()
        client.set(key, post)
        client.set(key_stamp, stamp)
    return post, stamp
                        
class BlogPost (Handler):
    def get(self, post_id):
        post, stamp = get_post(post_id)
        if post is None:
            self.error(404)
            return
        stamp = datetime.datetime.today() - stamp
        self.render("main.html", posts=[post], stamp=stamp)
        
class NewPost(Handler):
    
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/blog/login")
    
    def post(self):
        if not self.user:
            self.redirect("/blog/login")
            return
        
        subject = self.request.get("subject")
        content = self.request.get("content")
        
        if subject and content:
            post = Post(subject=subject, content=content)
            post.put()
            top_posts(update=True)
            self.redirect("/blog/%i" % (post.key().id()))
        else:
            error = "we need both subject and content"
            self.render("newpost.html", subject=subject, content=content, error=error)

class Blog2Json(Handler):
    def get(self):
        posts = top_posts()[0]
        self.render_json([post.as_dict() for post in posts])

class BlogPost2Json(Handler):
    def get(self, post_id):
        post = get_post(post_id)[0]
        self.render_json(post.as_dict())
        
class FlushCache(webapp2.RequestHandler):
    def get(self):
        memcache.Client().flush_all()
        self.redirect("/blog")

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
app = webapp2.WSGIApplication([ ('/rot13', ROT13),
                                ('/blog', Blog),
                                ('/blog/flush', FlushCache),
                                ('/blog/\.json', Blog2Json),
                                ('/blog/(\d+)', BlogPost),
                                ('/blog/(\d+)\.json', BlogPost2Json),
                                ('/blog/newpost', NewPost),
                                ('/blog/signup', Signup),
                                ('/blog/login', Login),
                                ('/blog/logout', Logout),
                                ('/blog/welcome', Welcome),
                                ('/wiki/welcome', wiki.Welcome),
                                ('/wiki/signup', wiki.Signup),
                                ('/wiki/login', wiki.Login),
                                ('/wiki/logout', wiki.Logout), 
                                ('/wiki/_history' + PAGE_RE, wiki.History),                                
                                ('/wiki/_edit' + PAGE_RE, wiki.WikiEdit),
                                ('/wiki' + PAGE_RE, wiki.WikiPage),],
                              debug=True)
