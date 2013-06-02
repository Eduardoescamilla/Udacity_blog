from rot13 import ROT13
import blog
import webapp2
import wiki

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
app = webapp2.WSGIApplication([ ('/rot13', ROT13),
                                ('/blog', blog.Blog),
                                ('/blog/flush', blog.FlushCache),
                                ('/blog/\.json', blog.Blog2Json),
                                ('/blog/(\d+)', blog.BlogPost),
                                ('/blog/(\d+)\.json', blog.BlogPost2Json),
                                ('/blog/newpost', blog.NewPost),
                                ('/blog/signup', blog.Signup),
                                ('/blog/login', blog.Login),
                                ('/blog/logout', blog.Logout),
                                ('/blog/welcome', blog.Welcome),
                                ('/wiki/welcome', wiki.Welcome),
                                ('/wiki/signup', wiki.Signup),
                                ('/wiki/login', wiki.Login),
                                ('/wiki/logout', wiki.Logout),
                                ('/wiki/_history' + PAGE_RE, wiki.History),                                
                                ('/wiki/_edit' + PAGE_RE, wiki.WikiEdit),
                                ('/wiki' + PAGE_RE, wiki.WikiPage),],
                              debug=True)
