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
    filled = ndb.BooleanProperty()

class User(ndb.Model):
    firstname = ndb.StringProperty()
    lastname = ndb.StringProperty()
    email = ndb.StringProperty()
    biography = ndb.StringProperty()
    profilepic = ndb.BlobProperty()

class MainPage(webapp2.RequestHandler):
    def get(self):
        project_query = Project.query()
        project_query = project_query.order(-Project.created_time)
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
        current_user = users.get_current_user()
        user_query = User.query()

        firstname = self.request.get('firstname')
        lastname = self.request.get('lastname')
        biography = self.request.get('biography')
        current_person = None
        logout_url = users.create_logout_url("/")

        if current_user:
            current_email = current_user.email()
            current_person = user_query.filter(User.email == current_email).get()

        if current_person:
            urlsafe_project_key = self.request.get("project_key")
            if urlsafe_project_key:
                project_key = ndb.Key(urlsafe=urlsafe_project_key)
                panels = Panel.query().filter(Panel.project_key == project_key)
                for panel in panels:
                    panel.key.delete()
                project_key.delete()

            urlsafe_profile_key = self.request.get("profile_key")
            if urlsafe_profile_key:
                profile_key = ndb.Key(urlsafe=urlsafe_profile_key)

                projects = Project.query().filter(Project.owner == profile_key)
                for project in projects:
                    panels = Panel.query().filter(Panel.project_key == project.key)
                    for panel in panels:
                        panel.key.delete()
                    project.key.delete()

                profile_key.delete()
                time.sleep(2)
                self.redirect(logout_url)

        else:
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
        all_panels = panels_query.filter(Panel.project_key == project_key).fetch()

        print "all panels", all_panels
        project = project_key.get()
        rows = project.rows
        columns = project.columns
        print("rows", rows)
        print("columns", columns)

        panel_rows = []

        for i in range(columns):
            row = []
            for j in range(rows):
                index_in_all_panels = columns * j + i
                print("index_in_all_panels", index_in_all_panels)
                panel_to_append = all_panels[index_in_all_panels]
                row.append(panel_to_append)
            panel_rows.append(row)

        # For however many rows,
        # Create a new row and add column however many panels

        current_user = users.get_current_user()
        logout_url = users.create_logout_url("/")
        login_url = users.create_login_url("/")

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
            "panel_rows" : panel_rows,
            "project" : project,
        }

        template = env.get_template("templates/viewProject.html")

        self.response.write(template.render(templateVars))

    def post(self):
        user_query = User.query()
        user_list = user_query.fetch()

        title = self.request.get('title')
        if self.request.get('rows'):
            rows = int(self.request.get('rows'))
            columns = int(self.request.get('columns'))
            current_user = users.get_current_user()


            if current_user:
                current_email = current_user.email()
                current_person = user_query.filter(User.email == current_email).get()
                newProject = Project(owner=current_person.key, rows=rows,
                columns=columns, title=title,)
                newProject_key = newProject.key
                newProject.put()
                newProject_key = newProject.key
                for i in range(1, columns + 1):

                    for j in range(1, rows + 1):
                        newPanel = Panel(project_key=newProject_key, width=200, height=200,
                                         panel_id=((i)+columns*(j-1)), content="%d %d" %(j, i))
                        newPanel.put()
            else:
                current_person = None
            time.sleep(2)
            self.redirect("/viewproject?key=" + newProject_key.urlsafe())
        else:
            project = ndb.Key(urlsafe=self.request.get('project_key')).get()
            project.title = title
            project.put()
            time.sleep(2)
            self.redirect("/viewproject?key=" + project.key.urlsafe())



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
        panel.filled = True

        if current_user:
            current_email = current_user.email()
            current_person = user_query.filter(User.email == current_email).get()
            panel.creator = current_person.key

        else:
            current_person = None

        panel.put()

        self.redirect('/updatepanel?key=' + panel.key.urlsafe())

class ProfilePictureUploadHandler(webapp2.RequestHandler):
    def post(self):
        user_query = User.query()
        user_list = user_query.fetch()
        upload = self.request.get("file")
        current_user = users.get_current_user()

        urlsafe_key = self.request.get('profile_key')
        profile_key = ndb.Key(urlsafe=urlsafe_key)

        profile = profile_key.get()
        profile.profilepic = upload

        profile.put()

        self.redirect('/editprofile')

class PhotoHandler(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get("key")
        key = ndb.Key(urlsafe=urlsafe_key)
        panel = key.get()
        self.response.headers["Content-Type"] = "image/jpg"
        self.response.write(panel.content)

class ProfilePictureHandler(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get("profile_key")
        profile_key = ndb.Key(urlsafe=urlsafe_key)
        profile = profile_key.get()
        self.response.headers["Content-Type"] = "image/jpg"
        self.response.write(profile.profilepic)

class Profile(webapp2.RequestHandler):
    def get(self):

        user_query = User.query()
        user_list = user_query.fetch()

        current_user = users.get_current_user()
        logout_url = users.create_logout_url("/profile")
        login_url = users.create_login_url("/profile")
        projects = None
        projectDict = None
        current_person = None
        if current_user:
            current_email = current_user.email()
            current_person = user_query.filter(User.email == current_email).get()

        profile_key = self.request.get('profile_key')

        if profile_key:
            profile = ndb.Key(urlsafe=profile_key).get()
            if current_user and profile.key == current_person.key:
                self.redirect("/profile")
        else:
            profile = None
            if current_person:
                profile = current_person


        if profile:
            projects = Project.query().filter(Project.owner == profile.key)
            projects = projects.order(-Project.created_time)
            panels = Panel.query().filter(Panel.creator == profile.key)
            projectDict = {}
            for project in projects:
                projectDict[project.key] = True
            for panel in panels:
                if not panel.project_key in projectDict:
                    projectDict[panel.project_key] = True

        templateVars = { #this is a dictionary
            "current_user" : current_user,
            "user_list" : user_list,
            "login_url" : login_url,
            "logout_url" : logout_url,
            "profile" : profile,
            "current_person" : current_person,
            "projects" : projectDict,
        }

        template = env.get_template("templates/profile.html")

        self.response.write(template.render(templateVars))

    def post(self):

        current_user = users.get_current_user()
        user_query = User.query()

        firstname = self.request.get('firstname')
        lastname = self.request.get('lastname')
        biography = self.request.get('biography')
        current_person = None

        if current_user:
            current_email = current_user.email()
            current_person = user_query.filter(User.email == current_email).get()

        if current_person:
            profile = ndb.Key(urlsafe=self.request.get('profile_key')).get()
            profile.firstname = firstname
            profile.lastname = lastname
            profile.biography = biography
            profile.put()
        else:
            email=users.get_current_user().email()
            newUser = User(firstname=firstname, lastname=lastname, biography=biography, email=email)
            newUser.put()

        time.sleep(2)

        self.redirect("/profile")

class EditProfile(webapp2.RequestHandler):
    def get(self):

        user_query = User.query()
        user_list = user_query.fetch()

        current_user = users.get_current_user()
        current_email = current_user.email()

        current_person = user_query.filter(User.email == current_email).get()
        profile = current_person

        templateVars = { #this is a dictionary
            "profile" : profile,
            "current_person" : current_person,
            "current_user" : current_user,
        }
        template = env.get_template("templates/editprofile.html")

        self.response.write(template.render(templateVars))

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

class EditTitle(webapp2.RequestHandler):

    def post(self):

        user_query = User.query()
        user_list = user_query.fetch()

        project_urlsafe = self.request.get('project_key')
        project = ndb.Key(urlsafe=project_urlsafe).get()

        current_user = users.get_current_user()
        current_email = current_user.email()

        current_person = user_query.filter(User.email == current_email).get()
        profile = current_person

        templateVars = { #this is a dictionary
            "profile" : profile,
            "current_person" : current_person,
            "current_user" : current_user,
            "project" : project,
        }

        template = env.get_template("templates/edittitle.html")

        self.response.write(template.render(templateVars))

app = webapp2.WSGIApplication([
    ("/", MainPage),
    ("/viewproject", viewProject),
    ("/profile", Profile),
    ("/newproject", NewProject),
    ("/updatepanel", UpdatePanel),
    ("/uploadphoto", PhotoUploadHandler),
    ("/uploadprofilepic", ProfilePictureUploadHandler),
    ("/photo", PhotoHandler),
    ("/profilepic", ProfilePictureHandler),
    ("/preview", Preview),
    ("/editprofile", EditProfile),
    ("/edittitle", EditTitle)
], debug=True)
