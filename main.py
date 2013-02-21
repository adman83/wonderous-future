import webapp2
import jinja2
import os
import re
import urllib2
import urlparse
import base64
import hashlib
import hmac
import datetime
import time
import bcrypt_folder.bcrypt as bcrypt
from google.appengine.ext import db

#jinja template render definition
template_dir = os.path.join(os.path.dirname(__file__), 'templates')

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True)

secret = 'Adam Has a Secret'

def render_str(template, **params):
        #renders a template with its parameters
        t = jinja_environment.get_template(template)
        return t.render(params)

def make_secure_val(val):
        return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
        val = secure_val.split('|')[0]
        if secure_val == make_secure_val(val):
                return val

#make a datastore model of kind "User"           
class User(db.Model):
        #and assign the following properties
        firstname = db.StringProperty(required=True)
        lastname = db.StringProperty(required=True)
        username = db.StringProperty()
        email = db.StringProperty()
        memberid = db.StringProperty(required=True)
        pictureurl = db.StringProperty()
        datejoined = db.DateTimeProperty(auto_now_add=True)
        dob = db.DateProperty()
        gender = db.StringProperty()
        accepted = db.StringProperty()
        role = db.StringProperty()
        preferred_framework = db.ReferenceProperty()
        
        def get_goals(self, user, type):
            parent_key= user.key()
            
            g = Goals.all()
            g.ancestor(parent_key)
            g.filter("type =", type)
            
            goal = g.get()
            
            return render_str('includes/goal.html', goal=goal, type=type, user=user)
        
        def get_active_objectives(self, user, typefilter, activefilter):
            parent_key = user.key()
            
            q = Objectives.all()
            q.ancestor(parent_key)
            q.filter("type =", typefilter)
            q.filter("display IN", activefilter)
            q.order("due_date")
            
            objectives = q.run()
            
            return render_str('includes/render_objectives.html', objectives=objectives, user=user)
        
        def get_evidence_by_obj(self, user, obj_key):
            q=Evidence.all()
            q.ancestor(user.key())
            q.filter("objective_key =", obj_key)
#            q.filter("framework_key =", frwk_key)
            
            evidence = q.run()
            return render_str('includes/render_evidence.html', evidence=evidence, user=user)
        
        def get_evidence_by_frwk(self, user, frwk_key):
            q=Evidence.all()
            q.ancestor(user.key())
#            q.filter("objective_key =", obj_key)
            q.filter("framework_key =", frwk_key)
            
            evidence = q.run()
            return render_str('includes/render_evidence.html', evidence=evidence, user=user)

        @classmethod
        def by_id(cls, uid):
                return cls.get_by_id(uid)

        @classmethod
        def by_username(cls, username):
                u = cls.all().filter('username =', username).get()
                return u
        
        @classmethod
        def by_memberid(cls, memberid):
                u = cls.all().filter('memberid =', memberid).get()
                return u

        @classmethod
        def login_check(cls, username, memberid):
                u = cls.by_username(username)

                if u and memberid:
                        return u
                    
class Frameworks(db.Model):
    discipline = db.StringProperty()
    organisation = db.StringProperty()
    title = db.StringProperty()
    
class Competencies(db.Model):
    section = db.StringProperty()
    type = db.StringProperty()
    description = db.TextProperty()
    guidance = db.TextProperty()
                    
#make a datastore model of kind "Plans"
class Plans(db.Model):
    #and assign the following properties
    memberid = db.StringProperty(required=True)
    grandparent_id = db.IntegerProperty()
    parent_id = db.IntegerProperty()
    plan_id = db.IntegerProperty(required=True)
    plan_type = db.StringProperty(required=True)
    title = db.StringProperty()
    description = db.TextProperty()
    status = db.StringProperty()
    due_date = db.DateTimeProperty()
    traffic_light = db.StringProperty()
    date_created = db.DateTimeProperty(auto_now_add=True)
    date_edited = db.DateTimeProperty(auto_now_add=True)
    archived = db.StringProperty()

#make a datastore model of kind "Future"
class Future(db.Model):
    #and assign the following properties
    description = db.TextProperty()
    date_created = db.DateTimeProperty(auto_now_add=True)
    date_edited = db.DateTimeProperty(auto_now_add=True)
    

#make a datastore model of kind "Goals"
class Goals(db.Model):
    #and assign the following properties
    type = db.StringProperty()
    description = db.TextProperty()
    date_created = db.DateTimeProperty(auto_now_add=True)
    date_edited = db.DateTimeProperty(auto_now_add=True)
        
    
#make a datastore model of kind "Objectives"
class Objectives(db.Model):
    #and assign the following properties
    title = db.StringProperty()
    type = db.StringProperty()
    description = db.TextProperty()
    due_date = db.DateProperty()
    status = db.StringProperty()
    traffic_light = db.StringProperty()
    date_created = db.DateTimeProperty(auto_now_add=True)
    date_edited = db.DateTimeProperty(auto_now_add=True)
    display = db.StringProperty() 
    
    def get_comments(self, user, parent_key):
        q = Comments.all()
        q.ancestor(parent_key)
        q.order("-date_created")
        
        comments = q.run()
        return render_str('includes/render_comments.html', comments=comments, user=user)
    
#make a datastore model of kind "Comments"
class Comments(db.Model):
    #and assign the following properties
    author=db.ReferenceProperty()
    comment = db.TextProperty()
    date_created = db.DateTimeProperty(auto_now_add=True)

#make a datastore model of kind "Suggestions"
class Suggestions(db.Model):
    #and assign the following properties
    author=db.ReferenceProperty()
    suggestion = db.TextProperty()
    date_created = db.DateTimeProperty(auto_now_add=True)
    up_votes = db.IntegerProperty()
    down_votes = db.IntegerProperty()
    sum_votes = db.IntegerProperty()
    
    def get_comments(self, user, parent_key):
        q = Comments.all()
        q.ancestor(parent_key)
        q.order("-date_created")
        
        comments = q.run()
        return render_str('includes/render_comments.html', comments=comments, user=user)

#make a datastore model of kind "Objectives"
class Evidence(db.Model):
    #and assign the following properties
    experience_date = db.DateProperty()
    title = db.StringProperty()
    details = db.TextProperty()
    objective_key = db.ReferenceProperty(reference_class=Objectives)
    framework_key = db.ReferenceProperty(reference_class=Frameworks, collection_name="section")
    date_created = db.DateTimeProperty(auto_now_add=True)
    date_edited = db.DateTimeProperty(auto_now_add=True)
    

#make the basic handler class
class MyHandler(webapp2.RequestHandler):
        #
        def write(self, *a, **kw):
                self.response.out.write(*a, **kw)

        def render(self, template, **kw):
                self.response.out.write(render_str(template, **kw))
                
        def set_secure_cookie(self, name, val):
                cookie_val = make_secure_val(val)
                self.response.headers.add_header(
                        'Set-Cookie',
                        '%s=%s; Path=/' % (name, cookie_val))#we can put a cookie expires value in here too (maybe optional on 'remember me')

        def read_secure_cookie(self, name):
                cookie_val = self.request.cookies.get(name)
                return cookie_val and check_secure_val(cookie_val)

        def login_set_cookie(self, user):
                self.set_secure_cookie('user_id', str(user.key().id()))

        def logout(self):
                self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

        def initialize(self, *a, **kw):
                webapp2.RequestHandler.initialize(self, *a, **kw)
                uid = self.read_secure_cookie('user_id')
                self.user = uid and User.by_id(int(uid))
                

# define the plan page handler class
class Welcome(MyHandler):

        def get(self):
                self.response.headers['content'] = 'text/plain'
                
                #check if there is a signed in user after the page INITIALIZEZ
                if not self.user:
                        #render the page with the template values
                        template_values = {
                                           
                        }
        
                        self.render('welcome.html', **template_values)
                else:
                    #there is a signed in user so go straight to the plan page
                        self.redirect('/plan')
                        
                
                

class Register(MyHandler):

        def get(self):
                #this page should only be accessed by a POST request, so redirect any GET request to the front page.              
                self.redirect('/')
                
        def post(self):
                self.response.headers['content'] = 'text/plain'
                #POST generated after the user profile has been pulled by the welcome page
                #get the submitted user memberid
                memberid = self.request.get("memberId")
                
                #look at the user table to see if a user with this member ID exists
                memberexists = User.by_memberid(memberid)
                #if a user with this memberID already exists, 
                if memberexists:
                    
                    self.login_set_cookie(memberexists)
                    self.redirect('/')
                    
                else:     
                    #if a user with this ID dosent already exist, then we want to ask them if they want to register with pdapp.
                    #get the form values
                    firstname = self.request.get("firstName")
                    lastname = self.request.get("lastName")
                    memberid = self.request.get("memberId")
                    pictureurl = self.request.get("pictureUrl")
                    email = self.request.get("emailAddress")
                    
                    #make a username
                    username = firstname+" "+lastname
                    
                    #if the user has pressed the agree button we can put the information into the user table.
                    if self.request.get("agree"):

                        #store the values in the database
                        u = User(firstname=firstname, lastname=lastname, username=username, memberid=memberid, pictureurl=pictureurl, email=email, accepted='yes',role='user')
                        u.put()

                        self.login_set_cookie(u)
                        self.redirect('/')
                        
                    #otherwise, the user agreement button hasnt been submitted, then we will render the page for them to agree
                    else:
                        #render the register page with template values to fill in the 
                        template_values = {
                                'firstname':firstname,
                                'lastname':lastname,
                                'username':username,#to stop the api from looking up details
                                'memberid':memberid,
                                'pictureurl':pictureurl,
                                'email':email
                        }
        
                        self.render('register.html', **template_values)
                
class Profile(MyHandler):
    def get(self):
        self.response.headers['content'] = 'text/plain'
        
        #check if there is a signed in user after the page INITIALIZEZ
        if not self.user:
                
                self.redirect('/')
        else:
            user = self.user
            
            q=Frameworks.all()
            frameworks = q.run()
            #render the page with the template values
            template_values = {
                    'user':user,
                    'frameworks':frameworks        
            }

            self.render('profile.html', **template_values)
    
    def post(self):
        if self.request.get("update_preferred_framework"):
            
            framework_key = self.request.get("framework_key")

            #get the user entity
            u = db.get(self.user.key())
            
            if framework_key:
                u.preferred_framework = db.Key(framework_key)
                
                u.put()
                
                self.redirect('/profile')
            else:
                u.preferred_framework=None
                u.put()
                self.redirect('/profile')
            
            

# define the plan page handler class
class PlanPage(MyHandler):

        def get(self):
                self.response.headers['content'] = 'text/plain'
                
                #check if there is a signed in user after the page INITIALIZEZ
                if not self.user:
                        
                        self.redirect('/')
                else:
                    user = self.user
                    
                    #get the users future description from the Plans table
                    q = Future.all()
                    q.ancestor(self.user.key())#the ancestor key is just the parents key value
                    #at this point future is still a query object - i need to use future.get() to actually get results
                    future = q.get()
                    
                    #get the error messages from a botched objective input if there are any
                    have_error = self.request.get("have_error")
                    error_type = self.request.get("type")

                    page = "plan"
                    #render the page with the template values
                    template_values = {
                            'user':user,
                            'future':future,
                            'have_error':have_error,
                            'error_type':error_type,
                            'page':page         
                    }
    
                    self.render('plan.html', **template_values)

class UpdateFuture(MyHandler):
    def post(self, id):
        #if there is no existing future description
        if int(id) == 0:
            #get the form values
            description = self.request.get("future")
            
            #get the users key value
            u_key = self.user.key()
            f = Future(parent = u_key,
                      description = description)
            
            f.put()
            
        else:
        
            #get the existing future entity by the current key id number
            f_key = db.Key.from_path("User", int(self.user.key().id()),"Future", int(id))
            f=db.get(f_key)
            
            
            #get the new description
            new_description = self.request.get("future")
            
            #assign new values to the properties
            f.description = new_description
            f.date_edited = datetime.datetime.now()
            
            #put the new data into the table
            f.put()
            
        #redirect the user to the front page
        self.redirect('/')

class UpdateGoal(MyHandler):
    
    def post(self,type,id):
        if int(id) == 0:
            #get the form values
            description = self.request.get(type+"_description")
            
            #get the users key value
            u_key = self.user.key()
            #create the goal entity
            g = Goals(parent = u_key,
                      type = type,
                      description = description)
            
            g.put()
            
        else:
        
            #get the existing goal entity by the current key id number
            g_key = db.Key.from_path("User", int(self.user.key().id()),"Goals", int(id))
            g=db.get(g_key)

            
            #get the new description
            new_description = self.request.get(type+"_description")
            
            #assign new values to the properties
            g.description = new_description
            g.date_edited = datetime.datetime.now()
            
            #put the new data into the table
            g.put()
            
        #redirect the user to the front page
        self.redirect('/')

DATE_RE = re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
def valid_date(date):
    return date and DATE_RE.match(date)

class UpdateObjective(MyHandler):
    def post(self,type,id):
        self.response.headers['content'] = 'text/plain'
        
        if int(id) == 0:
            #initialise the error values
            error_title = ""
            error_date = ""
            error_description = ""
            have_error=""
            
            user = self.user
            
            #get the form values
            title = self.request.get("obj_title")
            description = self.request.get("obj_description")
            due_date = self.request.get("obj_due_date")
            status = self.request.get("obj_status")
            traffic_light = self.request.get("obj_traffic_light")
            
            #check the required form values have been completed
            #note that I couldnt do the normal trick of rendering a template with error_values because it wouldnt change the url when I did. not sure why?
            #anyway, to get around that, I am now redirecting to the plan page with some GET variables, which I check for in the plan page to
            #generate some javascript to show the message.
            if not title:
                #set error_fields message
                have_error = True
                
            #check date is in the correct format
            if not valid_date(due_date):
                #set error_date message
                have_error = True
            
            if not description:
                have_error = True
            
            if have_error:
                self.redirect('/plan?have_error=True&type='+type)
            
            else:#no errors so...
                
                #put the date in a suitable DateProperty format for the datastore
                if due_date:
                                yearint = time.strptime(due_date,'%Y-%m-%d').tm_year
                                monthint = time.strptime(due_date,'%Y-%m-%d').tm_mon
                                dayint = time.strptime(due_date,'%Y-%m-%d').tm_mday
                                formatted_due_date = datetime.date(yearint,monthint,dayint)
                            
                            
            
                #encode the goal key string back into a key object
                #parent_key = db.Key(g_key)
                
                #get the goal key value
                #g_key = self.user.key()
                o = Objectives(parent = self.user.key(),
                               type = type,
                               title = title,
                               description = description,
                               due_date = formatted_due_date,
                               status= status,
                               traffic_light = traffic_light,
                               display = "active")
                
                o.put()
                
                #redirect the user to the front.
                self.redirect('/')
                
        else:#not an id of zero
            #get the existing objective entity by the current key id number
            o_key = db.Key.from_path("User", int(self.user.key().id()),"Objectives", int(id))
            o=db.get(o_key)
            
            #if we are only doing a quick change of display option from the review page, then check the "type" variable
            if type == "display_option":
                display = self.request.get("obj_display")
                
                o.display = display
                o.put()
                
                self.redirect('/review?view=objectives')
            else:
            

                #get the new values from the form
                #title = self.request.get("obj_title") not letting the user change the title of an objective once it has been set.
                new_description = self.request.get("obj_description")
                due_date = self.request.get("obj_due_date")
                status = self.request.get("obj_status")
                traffic_light = self.request.get("obj_traffic_light")
                type = self.request.get("obj_type")
                display = self.request.get("obj_display")
                
                #TODO: write some error handling for the properties above - maybs investigate JS error handling techniques?
                
                #put the date in a suitable DateProperty format for the datastore
                if due_date:
                                yearint = time.strptime(due_date,'%Y-%m-%d').tm_year
                                monthint = time.strptime(due_date,'%Y-%m-%d').tm_mon
                                dayint = time.strptime(due_date,'%Y-%m-%d').tm_mday
                                formatted_due_date = datetime.date(yearint,monthint,dayint)
                                #update the current objective value
                                o.due_date = formatted_due_date
                                
                #assign new values to the properties
                o.date_edited = datetime.datetime.now()
                o.description = new_description 
                o.status = status
                o.traffic_light = traffic_light
                o.type = type
                o.display = display
                
                #put the new data into the table
                o.put()
                
                #check if there is a new comment
                comment = self.request.get("obj_comment")
                if comment:
                    
                    #create a new comment entity
                    c = Comments(parent = o_key,
                                 comment = comment,
                                 author = self.user.key())
                    
                    #and add it to the datastore
                    c.put()
                
            
                #redirect the user to the front.
                self.redirect('/')
class Comment(MyHandler):
    def post(self, parent_key_str):
        
        parent_key = db.Key(parent_key_str)
        
        comment = self.request.get("comment")

        #create a new comment entity
        c = Comments(parent = parent_key,
                     comment = comment,
                     author = self.user.key())
        
        #and add it to the datastore
        c.put()
    

        #redirect the user to the front.
        self.redirect('/suggestions')

class DeleteComment(MyHandler):
    
    
    def post(self, ckey):
        
            #get the existing comment entity by the current key id number
#            c_key = db.Key.from_path("User", int(self.user.key().id()), parent, int(parent_id), "Comments", int(comment_id))
            #NOTE: you dont need to build the path from all these variables. you can just pass the key as it already includes the path!
            c=db.get(db.Key(ckey))
            
            self.write('<br> ckey is:')
            self.write(ckey)
            self.write('<br> c is:')
            self.write(c.key().id())
            c.delete()
            
            self.redirect('/')
                
# define the do page handler class
class DoPage(MyHandler):

        def get(self):
                self.response.headers['content'] = 'text/plain'
                
                #check if there is a signed in user after the page INITIALIZEZ
                if not self.user:
                        
                        self.redirect('/')
                else:
                    user = self.user
                    
                    page = "do"
   
                    #render the page with the template values
                    template_values = { 
                            'user':user,
                            'page':page     
                    }
    
                    self.render('do.html', **template_values)
                
# define the plan page handler class
class RecordPage(MyHandler):

        def get(self):
                self.response.headers['content'] = 'text/plain'
                
                #check if there is a signed in user after the page INITIALIZEZ
                if not self.user:
                        
                        self.redirect('/')
                else:
                    user = self.user

                    q = Objectives.all()
                    q.ancestor(user.key())
                    q.filter("display IN", ["active","review"])
                    q.order("-date_created")
                    
                    objectives = q.run()
                    
                    if user.preferred_framework:
                        c = Competencies.all()
                        c.ancestor(user.preferred_framework.key())
                        c.filter("type =", "competence")
                        competencies = c.run()
                    else:
                        competencies = ""
                    
                    page = "record"
                    #render the page with the template values
                    template_values = { 
                            'user':user,
                            'objectives':objectives,
                            'competencies':competencies,
                            'page':page        
                    }
    
                    self.render('record.html', **template_values)
        
        def post(self):
            #initialise the values
            user = self.user
            error_title = ""
            error_date = ""
            error_details = ""
            have_error = ""
            
            #get the form values
            title = self.request.get("title")
            experience_date = self.request.get("exp_date")
            objective_key_str = self.request.get("obj_key")
            framework_key_str = self.request.get("framework_key")
            details = self.request.get("details")

            #check if the user has selected an objective to associate the evidence with
            if not objective_key_str:
                #if not then set the objective key to None so that it doesnt upset the db model prperty
                objective_key=None
            else:
                #otherwise turn the key back into a string
                objective_key = db.Key(objective_key_str)
            
            #do the same for the framework key.
            if not framework_key_str:
                framework_key=None
            else:
                framework_key = db.Key(framework_key_str)
            
            
            #check the required form values have been completed
            if not title:
                #set error_fields message
                error_title = "please add a title"
                have_error = True
                
            #check date is in the correct format
            if not valid_date(experience_date):
                #set error_date message
                error_date = "please enter date in format YYYY-MM-DD"
                have_error = True
            
            if not details:
                error_details = "please enter your evidence details"
                have_error = True
            
            if have_error:
                
                q = Objectives.all()
                q.ancestor(user.key())
                q.filter("display =", "active")
                q.order("-date_created")
                
                objectives = q.run()
                
                c = Competencies.all()
                c.ancestor(user.preferred_framework.key())
                c.filter("type =", "competence")
                competencies = c.run()
                
                page = "record"
                #redirect to the record page with the error messages and the correct information
                template_values = { 
                            'user':user,
                            'objectives':objectives,
                            'competencies':competencies,
                            'title':title,
                            'experience_date':experience_date,
                            'details':details,
                            'error_title':error_title,
                            'error_date':error_date,
                            'error_details':error_details,
                            'page':page        
                    }
                
                self.render('record.html', **template_values)
            
            else:
                yearint = time.strptime(experience_date,'%Y-%m-%d').tm_year
                monthint = time.strptime(experience_date,'%Y-%m-%d').tm_mon
                dayint = time.strptime(experience_date,'%Y-%m-%d').tm_mday
                formatted_date = datetime.date(yearint,monthint,dayint)
                
                #make the Evidence entity
                e = Evidence(parent=user.key(),
                              title=title,
                               experience_date=formatted_date,
                                objective_key=objective_key,
                                 framework_key=framework_key,
                                  details=details)                       
                
                #put it in the datastore
                e.put()
                
                #make a thank you message
                thanks="Thanks for submitting evidence."
                page = "record"
                #redirect to the record page with a thank you message
                template_values = { 
                            'user':user,
                            'thanks':thanks,
                            'page':page,
                            'formatted_date':formatted_date        
                    }
                
                self.render('record.html', **template_values)
                    
class UpdateEvidence(MyHandler):
    def post(self,id):
        #get the existing objective entity by the current key id number
        e_key = db.Key.from_path("User", int(self.user.key().id()),"Evidence", int(id))
        e=db.get(e_key)

        #get the new values from the form
        new_details = self.request.get("evidence_details")
        
        e.details = new_details
        e.date_edited = datetime.datetime.now()
        
        e.put()
        
        self.redirect('/review')

# define the plan page handler class
class ReviewPage(MyHandler):

        def get(self):
                self.response.headers['content'] = 'text/plain'
                
                #check if there is a signed in user after the page INITIALIZEZ
                if not self.user:
                        
                        self.redirect('/')
                else:
                    user = self.user
                        
                    q=Objectives.all()
                    q.ancestor(user.key())
                    q.filter("display IN", ["active","review"])
                    objectives = q.run()
                    
                    a=Objectives.all()
                    a.ancestor(user.key())
                    a.filter("display =", "archive")
                    archive = a.run()
                    
                    c=Competencies.all()
		#I need to add a filter here so that only the users preferred competency framework competencies are retrieved
                    c.order("section")
                    competencies=c.run()
                    
                    e=Evidence.all()
                    e.ancestor(user.key())
                    e.order("experience_date")
                    evidence=e.run()
                    
                    view=self.request.get('view')
                    page = "review"
                    #render the page with the template values
                    template_values = { 
                            'user':user,
                            'objectives':objectives,
                            'archive':archive,
                            'competencies':competencies,
                            'evidence':evidence,
                            'page':page,
                            'view':view
                                 
                    }
    
                    self.render('review.html', **template_values)
                
class SuggestionsPage(MyHandler):
    def get(self):
        self.response.headers['content'] = 'text/plain'
                
        #check if there is a signed in user after the page INITIALIZEZ
        if not self.user:
            self.redirect('/')
        else:
            user = self.user
            page = "suggestions"
            
            q = Suggestions.all()
            q.order("-sum_votes")
            suggestions = q.run()
            
            #render the page with the template values
            template_values = { 
                    'user':user,
                    'page':page,
                    'suggestions':suggestions                                 
            }

            self.render('suggestions.html', **template_values)
    
    def post(self):

        #get the suggestion details
        suggestion = self.request.get("suggestion")
        
        #create a new suggestion entity
        c = Suggestions(parent = self.user.key(),
                        suggestion = suggestion,
                       author = self.user.key(),
                       up_votes = 0,
                       down_votes = 0,
                       sum_votes = 0)
        
        #and add it to the datastore
        c.put()
        
        #redirect to the suggestions page
        self.redirect('/suggestions')
            

class Vote(MyHandler):
    def post (self, authorid, id):
        #get the existing objective entity by the current key id number
        s_key = db.Key.from_path("User", int(authorid),"Suggestions", int(id))
        s=db.get(s_key)
        
        if self.request.get("vote_up"):
            s.up_votes += 1
            s.sum_votes += 1
            s.put()

        elif self.request.get("vote_down"):
            s.down_votes += 1
            s.sum_votes -= 1
            s.put()
        
        self.redirect('/suggestions')


        

class Logout(MyHandler):
        def get(self):
                #logout method to get rid of the cookie
                self.logout()
                #self.redirect("/")
                
                #render the page with the template values
                template_values = { 
                             
                }

                self.render('logout.html', **template_values)
                
class BackDoor(MyHandler):
    def get(self):
        memberid = self.request.get("memberId")
                
        #look at the user table to see if a user with this member ID exists
        memberexists = User.by_memberid(memberid)
        #if a user with this memberID already exists, 
        if memberexists:
            
            self.login_set_cookie(memberexists)
            self.redirect('/')
            
        else:     
            #render the page with the template values
            template_values = { 
                           
            }
    
            self.render('backdoor.html', **template_values)
        
class AddFramework(MyHandler):
    def get(self):
        
        user = self.user
        
        if user.role != "administrator":
            #redirectthe user as they have no permission
            self.redirect('/')
        else:
            #query the frameworks table for any frameworks
            q=Frameworks.all()
            frameworks = q.run()
            
            c=Competencies.all()
            c.order("section")
            competencies = c.run()
            
            #render the page with the template values
            template_values = {
                               'user':user,
                               'frameworks':frameworks,
                               'competencies':competencies,
                               }
    
            self.render('frameworks.html', **template_values)

    def post(self):
        #check if the user pressed the add framework button
        if self.request.get("add_framework"):
            
            #get the framework values
            discipline = self.request.get("framework_discipline")
            organisation = self.request.get("framework_organisation")
            title = self.request.get("framework_title")
            
            #make the framework entity
            f = Frameworks(discipline=discipline, organisation=organisation, title=title)
            #and put it into the table
            f.put()
            
            #redirect back to the page
            self.redirect('/add_framework')
            
        else:#otherwise it was the add competence button
            if self.request.get("parent"):
                #get the competence values
                parent_str = self.request.get("parent")
                section = self.request.get("section")
                type = self.request.get("type")
                description = self.request.get("description")
                guidance = self.request.get("guidance")
                
                parent=db.Key(parent_str)
                
                #make the framework entity
                c = Competencies(parent=parent, section=section, type=type, description=description, guidance=guidance)
                #and put it into the table
                c.put()
                
                #redirect back to the page
                self.redirect('/add_framework')
            else:
                self.write("add a framework first")
            

# define the pagehandlers
app = webapp2.WSGIApplication([('/', Welcome),
                               ('/backdoor',BackDoor),
                               ('/add_framework',AddFramework),
                               ('/profile',Profile),
                               ('/register',Register),
                               ('/plan', PlanPage),
                               ('/do', DoPage),
                               ('/record', RecordPage),
                               ('/review', ReviewPage),
                               ('/suggestions',SuggestionsPage),
                               ('/vote/([0-9]+)/([0-9]+)',Vote),
                               ('/logout', Logout),
                               ('/update_future/([0-9]+)',UpdateFuture),
                               ('/update_goal/([a-zA-Z]+)/([0-9]+)',UpdateGoal),
                               ('/update_objective/([a-zA-Z0-9_-]+)/([0-9]+)',UpdateObjective),
                               ('/comment/([a-zA-Z0-9_-]+)', Comment),
                               ('/delete_comment/([a-zA-Z0-9_-]+)',DeleteComment),
                               ('/update_evidence/([0-9]+)',UpdateEvidence)],
                              debug=True)
