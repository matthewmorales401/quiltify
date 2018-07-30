import webapp2
import jinja2
import os

from google.appengine.ext import ndb
from google.appengine.api import users

env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
)

class Project(ndb.Model):
    collaborators = []
    completed = ndb.BooleanProperty()
    panels = []
    numPanels = ndb.IntegerProperty()
    panelsRemaining = ndb.IntegerProperty()
    created_time = ndb.DateTimeProperty()

class Panel(ndb.Model):
    filled = False
    height = 80
    width = 80
    creator = ndb.StringProperty()
    content = "i'm a panel"

class Profile(ndb.Model):
    projects = []
    name = ndb.StringProperty()
    email = ndb.StringProperty()


class MainPage(webapp2.RequestHandler):
    def get(self):
        project_query = Project.query()
        project_query = project_query.order(Project.created_time)
        projects = project_query.fetch()
        templateVars = { #this is a dictionary
            "projects" : projects
        }
        template = env.get_template("templates/home.html")

        self.response.write(template.render(templateVars))


class viewProject(webapp2.RequestHandler):
    def get(self):
        template = env.get_template("templates/viewProject.html")
        templateVars = { #this is a dictionary

        }
        self.response.write(template.render(templateVars))


class Profile(webapp2.RequestHandler):
    def get(self):
        #profile=self.request.get('profile')
        template = env.get_template("templates/profile.html")
        templateVars = { #this is a dictionary

        }
        self.response.write(template.render(templateVars))

app = webapp2.WSGIApplication([
    ("/", MainPage),
    ("/viewProject", viewProject),
    ("/profile", Profile)
], debug=True)
