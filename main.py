import webapp2
import random
import os
import jinja2

from google.appengine.api import users
from google.appengine.ext import ndb

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello, World!') #response for the MainPage handler

class EmotionHandler(webapp2.RequestHandler):
    def get(self): #responds to a GET request
        emotions = ["witty", "edgy", "hangry", "excited", "on-point"]
        self.response.write("I feel so " + random.choice(emotions) + "!")


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/feelings', EmotionHandler)
], debug=True)
