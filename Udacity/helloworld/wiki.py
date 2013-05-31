from handler import Handler
from models import Wiki, User
import re

def get_wiki(wiki_name):
    return Wiki.all().filter("name", wiki_name).order("-created").get()

def get_wiki_history(wiki_name):
    return list(Wiki.all().filter("name", wiki_name))

class WikiPage(Handler):
    def get(self, page):
        wiki = get_wiki(page)
        params = {"page":page}
        if wiki:
            params["content"] = wiki.content
            self.render("wikipage.html", **params)
        elif self.user:
            self.redirect("/wiki/_edit%s" %page)
        else:
            self.redirect("/wiki/login")
            
            
class WikiEdit(Handler):
    def get(self, page):
        if self.user:
            wiki = get_wiki(page)
            params = {"page":page}
            if wiki:
                params["content"] = wiki.content
            self.render("wiki-edit.html", **params)
        else:
            self.redirect("/wiki/login")
    
    def post(self, page):
        if not self.user:
            self.redirect("/wiki/login")
        else:
            content = self.request.get("content")
            if not content:
                self.render("wiki-edit.html", error="We need content")
            else:
                wiki = Wiki(name = page, content = content)
                wiki.put()
                self.redirect("/wiki%s" %page)

class Login(Handler):
    def get(self):
        self.render("wiki_login.html")
    
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        user = User.login(username, password)
        if user:
            self.login(user)
            self.redirect("/wiki/welcome")
        else:
            error_login = "Invalid Login"
            self.render("wiki_login.html", username=username, error_login=error_login)


class Logout(Handler):
    def get(self):
        self.logout()
        self.redirect("/wiki/login")


class Signup(Handler):
   
    def get(self):
        self.render("wiki_signup.html")
        
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        params = {"username":username, "email":email}
        error = False
        if not(username and self.valid_username(username)):
            params["error_username"] = "That's not a valid username"
            error = True
        if not(password and self.valid_password(password)):
            params["error_password"] = "That's not a valid password"
            error = True
        elif not(verify and self.valid_verify(password, verify)):
            params["error_verify"] = "Passwords don't match"
            error = True
        if email and not self.valid_email(email):
            params["error_email"] = "That's not a valid email"
            error = True
        if error:
            self.render("wiki_signup.html", **params)
        elif self.exists_username(username):
            params["error_username"] = "Username already exists"
            self.render("wiki_signup.html", **params)
        else:            
            user = User.register(username, password, email)
            user.put()
            self.login(user)
            self.redirect("/wiki/welcome")
        
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


class Welcome(Handler):
    def get(self):    
        if self.user:    
            self.render("wiki_welcome.html", username=self.user.username)
        else:
            self.redirect("/wiki/login")

class History(Handler):
    def get(self, page):
        history = get_wiki_history(page)
        self.render("wiki-history.html", page=page, history=history)