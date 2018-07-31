import webapp2
import jinja2
import os
import time

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext import blobstore

env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
)

class Project(ndb.Model):
    owner = ndb.KeyProperty()
    rows = ndb.IntegerProperty()
    columns = ndb.IntegerProperty()
    created_time = ndb.DateTimeProperty(auto_now_add=True)
    title = ndb.StringProperty()

class Panel(ndb.Model):
    height = ndb.IntegerProperty()
    width = ndb.IntegerProperty()
    panel_id = ndb.IntegerProperty()
    creator = ndb.KeyProperty()
    content = ndb.BlobProperty()
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

        project_key = ndb.Key(urlsafe = self.request.get('key'))
        panels_query = Panel.query().order(Panel.panel_id)
        panels = panels_query.filter(Panel.project_key == project_key).fetch()

        project = project_key.get()

        current_user = users.get_current_user()
        logout_url = users.create_logout_url("/viewproject")
        login_url = users.create_login_url("/viewproject")

        if current_user:
            current_email = current_user.email()
            current_person = user_query.filter(User.email == current_email).get()
        else:
            current_person = None

        # project_url_key = self.request.get('project_key')
        # project_key = ndb.Key(urlsafe=project_url_key)

        templateVars = { #this is a dictionary
            "current_user" : current_user,
            "login_url" : login_url,
            "logout_url" : logout_url,
            "current_person" : current_person,
            "panels" : panels,
            "project" : project,
        }

        template = env.get_template("templates/viewProject.html")

        self.response.write(template.render(templateVars))

    def post(self):
        user_query = User.query()
        user_list = user_query.fetch()

        rows = int(self.request.get('rows'))
        columns = int(self.request.get('columns'))
        current_user = users.get_current_user()
        title = self.request.get('title')

        if current_user:
            current_email = current_user.email()
            current_person = user_query.filter(User.email == current_email).get()
            newProject = Project(owner=current_person.key, rows=rows,
            columns=columns, title=title,)
            newProject.put()
            newProject_key = newProject.key
            for i in range(1, rows*columns + 1):
                newPanel = Panel(project_key=newProject_key, width=200, height=200,
                panel_id = i, content="THIS IS A PANEL")
                newPanel.put()
        else:
            current_person = None

        time.sleep(2)
        self.redirect("/viewproject?key=" + newProject_key.urlsafe())

class UpdatePanel(webapp2.RequestHandler):
    def get(self):
        user_query = User.query()
        user_list = user_query.fetch()

        panel_key = ndb.Key(urlsafe = self.request.get('key'))
        panel = panel_key.get()

        project = panel.project_key.get()

        current_user = users.get_current_user()
        logout_url = users.create_logout_url("/updatepanel")
        login_url = users.create_login_url("/updatepanel")

        if current_user:
            current_email = current_user.email()
            current_person = user_query.filter(User.email == current_email).get()
        else:
            current_person = None

        upload_url = blobstore.create_upload_url("/uploadphoto")
        # project_url_key = self.request.get('project_key')
        # project_key = ndb.Key(urlsafe=project_url_key)

        templateVars = { #this is a dictionary
            "current_user" : current_user,
            "login_url" : login_url,
            "logout_url" : logout_url,
            "current_person" : current_person,
            "panel" : panel,
            "project" : project,
            "upload_url" : upload_url,
        }

        template = env.get_template("templates/updatepanel.html")

        self.response.write(template.render(templateVars).format(upload_url))

    def post(self):
        user_query = User.query()
        user_list = user_query.fetch()

        current_user = users.get_current_user()

        if current_user:
            current_email = current_user.email()
            current_person = user_query.filter(User.email == current_email).get()

        else:
            current_person = None

class PhotoUploadHandler(webapp2.RequestHandler):
    def post(self):
        user_query = User.query()
        user_list = user_query.fetch()
        upload = self.request.get("file")
        current_user = users.get_current_user()

        urlsafe_key = self.request.get('key')
        panel_key = ndb.Key(urlsafe=urlsafe_key)

        panel = panel_key.get()
        panel.content = upload

        if current_user:
            current_email = current_user.email()
            current_person = user_query.filter(User.email == current_email).get()
            panel.creator = current_person.key

        else:
            current_person = None

        panel.put()

        self.redirect('/updatepanel?key=' + panel.key.urlsafe())

class PhotoHandler(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get("key")
        key = ndb.Key(urlsafe=urlsafe_key)
        panel = key.get()
        self.response.headers["Content-Type"] = "image/jpg"
        self.response.write(panel.content)

class Profile(webapp2.RequestHandler):
    def get(self):

        user_query = User.query()
        user_list = user_query.fetch()

        current_user = users.get_current_user()
        logout_url = users.create_logout_url("/profile")
        login_url = users.create_login_url("/profile")
        projects = None

        if current_user:
            current_email = current_user.email()
            current_person = user_query.filter(User.email == current_email).get()
            if current_person:
                projects = Project.query().filter(Project.owner == current_person.key)
                projects = projects.order(Project.created_time)
        else:
            current_person = None

        templateVars = { #this is a dictionary
            "current_user" : current_user,
            "user_list" : user_list,
            "login_url" : login_url,
            "logout_url" : logout_url,
            "current_person" : current_person,
            "projects" : projects,
        }

        template = env.get_template("templates/profile.html")

        self.response.write(template.render(templateVars))

    def post(self):
        firstname = self.request.get('firstname')
        lastname = self.request.get('lastname')
        biography = self.request.get('biography')
        email=users.get_current_user().email()
        newUser = User(firstname=firstname, lastname=lastname,
        biography=biography, email=email)
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


class Preview(webapp2.RequestHandler):
    def get(self):

        user_query = User.query()
        user_list = user_query.fetch()

        project_key = ndb.Key(urlsafe = self.request.get('key'))
        panels_query = Panel.query().order(Panel.panel_id)
        panels = panels_query.filter(Panel.project_key == project_key).fetch()

        project = project_key.get()

        current_user = users.get_current_user()
        logout_url = users.create_logout_url("/preview")
        login_url = users.create_login_url("/preview")

        if current_user:
            current_email = current_user.email()
            current_person = user_query.filter(User.email == current_email).get()
        else:
            current_person = None

        # project_url_key = self.request.get('project_key')
        # project_key = ndb.Key(urlsafe=project_url_key)

        templateVars = { #this is a dictionary
            "current_user" : current_user,
            "login_url" : login_url,
            "logout_url" : logout_url,
            "current_person" : current_person,
            "panels" : panels,
            "project" : project,
        }

        template = env.get_template("templates/preview.html")

        self.response.write(template.render(templateVars))



app = webapp2.WSGIApplication([
    ("/", MainPage),
    ("/viewproject", viewProject),
    ("/profile", Profile),
    ("/newproject", NewProject),
    ("/updatepanel", UpdatePanel),
    ("/uploadphoto", PhotoUploadHandler),
    ("/photo", PhotoHandler),
    ("/preview", Preview)
], debug=True)
