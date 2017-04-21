import webapp2
import os
import jinja2
from google.appengine.ext import db
import re


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):

    def render_front(self, title ="", post = "", error = ""):
        posts = db.GqlQuery("SELECT * from Post ORDER BY created DESC LIMIT 5")
        self.render("frontpage.html", title = title, post = post, error = error, posts = posts)

    def get(self):
        self.render_front()


class NewPost(Handler):
    #new posts
    def render_new_post_form(self, title = "", post = "", error = ""):
        self.render("newposts.html", title = title, post = post, error = error)

    def get(self):
        self.render_new_post_form()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            p = Post(title = title, post = post)
            p.put()
            self.redirect("/blog/" + str(p.key().id()))
        else:
            error = "Please enter both a title and a blogpost."
            self.render_new_post_form(error = error)

class ViewPostHandler(Handler):
    #links to inividual posts

    def render_single_post(self,id, title = "", post = "", error = ""):
        single_post = Post.get_by_id(int(id), parent = None)
        self.render("singlepost.html", title = title, post = post, error = error, single_post = single_post)

    def get(self, id):
        if id:
            self.render_single_post(id)
        else:
            self.render_single_post(id, title = "No Title", post = "No post has the id:" + str(id))

app = webapp2.WSGIApplication([('/', MainPage),
                                ('/newpost', NewPost),
                                ('/blog', MainPage),
                                webapp2.Route(('/blog/<id:\d+>'), ViewPostHandler),
                                ], debug=True)
