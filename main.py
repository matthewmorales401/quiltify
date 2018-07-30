import webapp2
import jinja2
import os
import time

from google.appengine.ext import ndb
from google.appengine.api import users

env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
)

class Project(ndb.Model):
    owner = ndb.KeyProperty()
    completed = ndb.BooleanProperty()
    rows = ndb.IntegerProperty()
    columns = ndb.IntegerProperty()
    created_time = ndb.DateTimeProperty()

class Panel(ndb.Model):
    filled = False
    height = ndb.IntegerProperty()
    width = ndb.IntegerProperty()
    panel_id = ndb.IntegerProperty()
    creator = ndb.KeyProperty()
    content = "i'm a panel"
    project_key = ndb.KeyProperty() #project_key = project_name.key

class User(ndb.Model):
    firstname = ndb.StringProperty()
    lastname = ndb.StringProperty()
    email = ndb.StringProperty()
    biography = ndb.StringProperty()

class MainPage(webapp2.RequestHandler):
    def get(self):
        project_query = Project.query()
        project_query = project_query.order(Project.created_time)
        projects = project_query.fetch()

        user_query = User.query()
        user_list = user_query.fetch()

        current_user = users.get_current_user()
        logout_url = users.create_logout_url("/")
        login_url = users.create_login_url("/")

        if current_user:
            current_email = current_user.email()
            current_person = user_query.filter(User.email == current_email).get()
        else:
            current_person = None

        templateVars = { #this is a dictionary
            "current_user" : current_user,
            "projects" : projects,
            "user_list" : user_list,
            "login_url" : login_url,
            "logout_url" : logout_url,
            "current_person" : current_person,
        }
        template = env.get_template("templates/home.html")

        self.response.write(template.render(templateVars))

    def post(self):
        firstname = self.request.get('firstname')
        lastname = self.request.get('lastname')
        biography = self.request.get('biography')
        email=users.get_current_user().email()
        newUser = User(firstname=firstname, lastname=lastname, biography=biography, email=email)
        newUser.put()
        time.sleep(2)
        self.redirect("/")


class viewProject(webapp2.RequestHandler):
    def get(self):

        user_query = User.query()
        user_list = user_query.fetch()

        current_user = users.get_current_user()
        logout_url = users.create_logout_url("/viewproject")
        login_url = users.create_login_url("/viewproject")

        if current_user:
            current_email = current_user.email()
            current_person = user_query.filter(User.email == current_email).get()
        else:
            current_person = None

        templateVars = { #this is a dictionary
            "current_user" : current_user,
            "login_url" : login_url,
            "logout_url" : logout_url,
            "current_person" : current_person,
        }

        template = env.get_template("templates/viewProject.html")

        self.response.write(template.render(templateVars))

    def post(self):
        firstname = self.request.get('firstname')
        lastname = self.request.get('lastname')
        biography = self.request.get('biography')
        email=users.get_current_user().email()
        newUser = User(firstname=firstname, lastname=lastname, biography=biography, email=email)
        newUser.put()
        time.sleep(2)
        self.redirect("/viewproject")

class Profile(webapp2.RequestHandler):
    def get(self):

        user_query = User.query()
        user_list = user_query.fetch()

        current_user = users.get_current_user()
        logout_url = users.create_logout_url("/profile")
        login_url = users.create_login_url("/profile")

        if current_user:
            current_email = current_user.email()
            current_person = user_query.filter(User.email == current_email).get()
        else:
            current_person = None

        templateVars = { #this is a dictionary
            "current_user" : current_user,
            "user_list" : user_list,
            "login_url" : login_url,
            "logout_url" : logout_url,
            "current_person" : current_person,
        }

        template = env.get_template("templates/profile.html")

        self.response.write(template.render(templateVars))

    def post(self):
        firstname = self.request.get('firstname')
        lastname = self.request.get('lastname')
        biography = self.request.get('biography')
        email=users.get_current_user().email()
        newUser = User(firstname=firstname, lastname=lastname, biography=biography, email=email)
        newUser.put()
        time.sleep(2)

        self.redirect("/profile")

class NewProject(webapp2.RequestHandler):
    def get(self):
        user_query = User.query()
        user_list = user_query.fetch()

        current_user = users.get_current_user()
        logout_url = users.create_logout_url("/profile")
        login_url = users.create_login_url("/profile")

        if current_user:
            current_email = current_user.email()
            current_person = user_query.filter(User.email == current_email).get()
        else:
            current_person = None

        templateVars = { #this is a dictionary
            "current_user" : current_user,
            "user_list" : user_list,
            "login_url" : login_url,
            "logout_url" : logout_url,
            "current_person" : current_person,
        }

        template = env.get_template("templates/newproject.html")

        self.response.write(template.render(templateVars))

app = webapp2.WSGIApplication([
    ("/", MainPage),
    ("/viewproject", viewProject),
    ("/profile", Profile),
    ("/newproject", NewProject),
], debug=True)
