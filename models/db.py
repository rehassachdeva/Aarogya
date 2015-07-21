from gluon.contrib.appconfig import AppConfig
myconf = AppConfig(reload=True)
import datetime
if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')

from gluon.tools import Crud
crud = Crud(db)
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import *

auth = Auth(db)
service = Service()
plugins = PluginManager()
mail=Mail()

is_phone=IS_MATCH('\d{10}',error_message="Example: 9876111234")

auth.settings.extra_fields['auth_user']= [
  Field('sex', requires=IS_IN_SET(('F','M')),notnull=True),
  Field('phone',requires=is_phone),
  Field('address',requires=IS_NOT_EMPTY()),
  Field('birth_date','date', requires=IS_DATE_IN_RANGE(format=T('%Y-%m-%d'),
                   minimum=datetime.date(1900,1,1),
                   maximum=request.now.date())),
  Field('Category','string',requires=IS_IN_SET(('Patient', 'Doctor','Staff')),widget=SQLFORM.widgets.radio.widget),
  Field('patient','boolean',default=True, writable=False, readable=False),
  Field('doctor','boolean',default=False, writable=False, readable=False),
  ]
auth.define_tables(username=False, signature=True)


db.define_table('patient',
                Field('UPID',db.auth_user,default=auth.user_id, label="Patient", writable=False),
                Field('bloodgroup', 'string',length=3,
                    requires=IS_IN_SET(('O+','O-','A+','A-','B+','B-','AB+','AB-')),widget=SQLFORM.widgets.radio.widget, label="Blood Group"),
                Field('allergies', 'text',label="Allergies"),
                Field('surgeries','text',label="Past Surgeries"),
                Field('diseases','string',label="Chronic Diseases"),
                format='%(UPID)s'
                )

db.define_table('doctor',
                Field('UDID', db.auth_user,default=auth.user_id, label="Doctor", writable=False) ,
                Field('Qualifications', 'string', requires=IS_NOT_EMPTY(), label="Qualifications"),
                Field('visiting_days', 'string',
                      requires=IS_IN_SET(('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'))),
                Field('visiting_hours','string',requires=IS_IN_SET(['10:00-11:00','11:00-12:00','12:00-13:00','13:00-14:00','14:00-15:00','15:00-16:00'],multiple=True),widget=SQLFORM.widgets.checkboxes.widget),
                Field('image','upload'),                
                format='%(UDID)s'
                )




db.define_table('staff',
                Field('USID',db.auth_user,default=auth.user_id, label="USID", writable=False, readable=False),
                Field('Designation','string',requires=IS_NOT_EMPTY(),),
                Field('Qualifications',requires=IS_NOT_EMPTY(),),
                Field('Experience'),
                Field('Salary','string',writable=False),
                format='%(USID)s'
                )

db.define_table('MedicalReports',
                Field('UPID',db.auth_user, label="Patient"),
                Field('UDID',db.auth_user,default=auth.user_id,writable=False, label="Doctor") ,
                Field('dated','date',default=request.now, label="Created on",writable=False),
                Field('ChiefComplaint','string',requires=IS_NOT_EMPTY(),label="Chief Complaint"),
                Field('CaseHistory','string',requires=IS_NOT_EMPTY(), label="Case History"),
                Field('ClinicalFinding','string',requires=IS_NOT_EMPTY(), label="Clinical Finding"),
                Field('InvestigationsAdvised','string', label="Investigations Advised (if any)"),
                
                Field('Treatment','string', label="Treatment",requires=IS_NOT_EMPTY()),
                Field('Prescription','string'),
                Field('FollowUpDetails','string',label="Follow Up details")
                )

db.define_table('appointment',
                Field('UPID',db.auth_user, default=auth.user_id, label="Patient", writable=False,),
                Field('UDID',db.auth_user, label="Doctor",),
                Field('dated','date', label="Date",requires=IS_DATE_IN_RANGE(format=T('%Y-%m-%d'),
                   maximum=None,
                   minimum=request.now.date())),
                Field('patient_request_time',requires=IS_IN_SET(('Morning(10:00-12:00)','Afternoon(12:00-14:00)','Evening(14:00-16:00)')),label="Requested Time"),
                Field('Status',requires=IS_IN_SET(('Accepted', 'Rejected'))),
                Field('Slot_doctor_confirm',requires=IS_IN_SET(('10:00-11:00','11:00-12:00','12:00-13:00','13:00-14:00','14:00-15:00','15:00-16:00')),label="Slot Alotted"),
                Field('symptoms','text',label=T('Symptoms'))
                )

db.define_table('Stock',
                Field('USID',db.auth_user, default=auth.user_id, label="Staff", writable=False),
                Field('Name',requires=IS_NOT_EMPTY()),
                Field('Dose', requires=IS_NOT_EMPTY()),
                Field('Salts',requires=IS_NOT_EMPTY()),
                Field('MedicineUse','text',requires=IS_NOT_EMPTY(), label="Usage"),
                Field('Quantity','integer',requires=IS_NOT_EMPTY()),
                Field('ExpiryDate','date', label="Expiry Date")
                
                )

db.define_table('EquipmentsChemicals',
                Field('UDID',db.auth_user, default=auth.user_id, label="Doctor", writable=False),
                Field('Name','string',length=128,requires=IS_NOT_EMPTY()),
                Field('EquipmentUsage','text',requires=IS_NOT_EMPTY(), label="Usage"),
                Field('Quantity','integer',requires=IS_NOT_EMPTY()),
                Field('Supplier')
                )

db.define_table('Feedback',
                Field('UPID',db.auth_user, default=auth.user_id, label="Patient", writable=False),
                Field('environment',requires=IS_IN_SET(('Good','Average','Poor')),label="The Hospital environment is: "),
                Field('ward_facilities',requires=IS_IN_SET(('Good','Average','Poor')),label="The Ward Facilities are: "),
                Field('doctors_services',requires=IS_IN_SET(('Good','Average','Poor')),label="The service of attending Doctors is: ")
                )


## create all tables needed by auth if not custom tables
#############################################################3
#By default, web2py uses email for login. If instead you want to log in using username set auth.define_tables(username=True)

#Setting signature=True adds user and date stamping to auth tables, to track modifications.

#Auth has an optional secure=True argument, which will force authenticated pages to go over HTTPS. 



#########################################################################



## configure email
mail = auth.settings.mailer
mail.settings.server = EMAIL_SERVER
mail.settings.sender = EMAIL_SENDER
mail.settings.login = EMAIL_LOGIN

## configure auth policy
auth.settings.registration_requires_verification = True #edit this

auth.settings.reset_password_requires_verification = True

## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
#doctor_gp=auth.add_group('Doctor','Doctor at Aarogya')
#patient_gp=auth.add_group('Patient','Patient at Aarogya')
#admin_gp=auth.add_group('Admin','Admin at Aarogya')
#auth.settings.create_user_groups = False

def send_email_realtime(to, subject, message, sender):
    if not isinstance(to,list): to = [to]
    if auth.user: to = [email for email in to if not to==auth.user.email]    
    mail.settings.sender = sender
    return mail.send(to=to, subject=subject, message=message or '(no message)')


def send_email_deferred(to, subject, message, sender):
    if not isinstance(to,list): to = [to]
    #db.email.insert(to_addrs=to,subject=subject,body=message,sender=sender,
    #                status='pending')
    #scheduler.queue_task(send_pending_emails)
    scheduler.queue_task(send_email_realtime,
                         pvars=dict(to=to,subject=subject,
                                    message=message,sender=sender))




def send_email(to, subject, message, sender):
    if EMAIL_POLICY == 'realtime':
        return send_email_realtime(to, subject, message, sender)
    else:
        return send_email_deferred(to, subject, message, sender)
