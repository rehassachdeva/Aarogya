# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    if auth.user:
        eventLogin = db.auth_event.user_id == auth.user.id
        if db(eventLogin).count() == 1:
            if auth.user.Category=='Patient':
                redirect(URL('profile_patient'))
            elif auth.user.Category=='Doctor':
                redirect(URL('profile_doctor'))
            elif auth.user.Category=='Staff':
                redirect(URL('profile_staff'))
    if auth.user:
        if auth.user.Category=='Doctor':
            redirect(URL('Doctor_index'))
        elif auth.user.Category=='Patient':
            redirect(URL('Patient_index'))
        elif auth.user.Category=='Staff':
            redirect(URL('Staff_index'))
    return dict(heading=T('Welcome to Aarogya!'))

@auth.requires_login()
def profile_patient():
    form=SQLFORM(db.patient)
    if form.process().accepted:
        redirect(URL('profile_view_patient'))
    return dict(form=form, heading="Create Profile")

@auth.requires_login()
def profile_view_patient():
    query=db.patient.UPID==auth.user_id
    db.patient.bloodgroup.writable=False
    db.patient.id.writable=False
    db.patient.id.readable=False
    grid=SQLFORM.grid(query=query,create=False, deletable=False, searchable=False)
    return dict(grid=grid, heading="My Profile")

@auth.requires_login()
def profile_doctor():
    form=SQLFORM(db.doctor)
    if form.process().accepted:
        redirect(URL('profile_view_doctor'))
    return dict(form=form, heading="Create Profile")

@auth.requires_login()
def profile_view_doctor():
    query=db.doctor.UDID==auth.user_id    
    db.doctor.id.writable=False
    db.doctor.id.readable=False
    grid=SQLFORM.grid(query=query,create=False, deletable=False, searchable=False)
    return dict(grid=grid, heading="My Profile")

@auth.requires_login()
def profile_staff():
    form=SQLFORM(db.staff)
    if form.process().accepted:
        redirect(URL('profile_view_staff'))
    return dict(form=form, heading="Create Profile")

@auth.requires_login()
def profile_view_staff():
    query=db.staff.USID==auth.user_id
    db.staff.Designation.writable=False
    db.staff.id.writable=False
    db.staff.id.readable=False
    grid=SQLFORM.grid(query=query,create=False, deletable=False, searchable=False)
    return dict(grid=grid, heading="My Profile")

@auth.requires_login()
def Staff_index():
    return dict()

def user():    
    if auth.user:
        db.auth_user.Category.writable=False
        db.auth_user.sex.writable=False
        db.auth_user.birth_date.writable=False
    return dict(form=auth(),heading="My Profile")

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

@auth.requires_login()
def Patient_index():
    return dict()


@auth.requires_login()
def Doctor_index():
    return dict()

@auth.requires_login()
def report_patient():
    db.MedicalReports.UPID.readable=False
    db.MedicalReports.id.readable=False   
    query=db.MedicalReports.UPID==auth.user_id   
    grid=SQLFORM.grid(query=query,editable=False, create=False,deletable=False)
    return dict(grid=grid,heading='My Medical Reports')

@auth.requires_login()
def appointment_patient():
    db.appointment.UPID.writable=False
    db.appointment.Status.writable=False
    db.appointment.Slot_doctor_confirm.writable=False
    query=db.appointment.UPID==auth.user_id
    grid=SQLFORM.grid(query=query)
    return dict(grid=grid,heading='My Appointments')

@auth.requires_login()
def medicine_patient():
    db.Stock.Quantity.readable=False
    query=db.Stock.Quantity>0
    grid=SQLFORM.grid(query=query,editable=False, create=False,deletable=False,searchable=True)
    return dict(grid=grid,heading='Medicines Available')

@auth.requires_login()
def feedback_patient():
    form=SQLFORM(db.Feedback)
    if form.process().accepted:
        response.flash = 'Thank you for your valuable feedback!'
    return dict(form=form,heading='My Feedback')

@auth.requires_login()
def report_doctor():
    query=db.MedicalReports.UDID==auth.user_id
    db.MedicalReports.UPID.readable=True
    db.MedicalReports.UPID.writable=True
    grid=SQLFORM.grid(query=query,editable=True, create=True,deletable=False,searchable=True)
    return dict(grid=grid,heading='Medical Reports')

@auth.requires_login()
def medicine_doctor():
    grid1=SQLFORM.grid(db.Stock,editable=False, create=False,deletable=False)
    return dict(grid=grid1,heading='Medicines Available')

@auth.requires_login()
def request_doctor():
    form1=SQLFORM(db.EquipmentsChemicals)
    if form1.process().accepted:
       response.flash = 'Thank you for your request! We will do the needful as soon as possible.'
    return dict(form=form1,heading='Request for New Medicines or Chemicals or Equipments')

@auth.requires_login()
def appointment_doctor():
    db.appointment.UPID.writable=False
    db.appointment.UDID.writable=False
    rows=db(db.appointment.UDID==auth.user_id).select()
    rows=rows[0]
    rows=rows.visiting_hours
    db.appointment.symptoms.writable=False
    db.appointment.dated.writable=False
    db.appointment.patient_request_time.writable=False
    query=db.appointment.UDID==auth.user_id
    grid=SQLFORM.grid(query=query, create=False, deletable=False, onupdate=appointment_edit)
    return dict(grid=grid,heading='My Appointments')

@auth.requires_login()
def mycal():
 rows=db(db.appointment.UDID==auth.user_id).select()
 return dict(rows=rows,heading='My Calendar')

@auth.requires_login()
def appointment_edit(form):
    rows = db(db.appointment.id==form.vars.id).select()
    rows = rows[0]
    upid = rows.UPID
    udid = rows.UDID
    patient = db(db.auth_user.id==upid).select()
    patient = patient[0]
    pname = patient.first_name+" "+patient.last_name
    email_to = patient.email
    doctor = db(db.auth_user.id==udid).select()
    doctor = doctor[0]
    dname = doctor.first_name+" "+doctor.last_name

    if rows.Status=='Accepted':
        subject="Appointment Confirmed"
        message="Dear %s,\n\t Your appointment with Dr. %s on %s has been confirmed and you have been allotted the slot %s. In case you are not comfortable with the allotted slot, please book a new appointment. \n\n Wishing you best of health, \n IIIT-H Aarogya" % (pname,dname,rows.dated,rows.Slot_doctor_confirm)

    elif rows.Status=='Rejected':
        subject="Appointment Rejected"
        message="Dear %s,\n\t We regret to inform you that your appointment with Dr. %s on %s has been rejected as the doctor is not available on the requested day. Please book a new appointment. \n\n Wishing you best of health, \n IIIT-H Aarogya" % (pname,dname,rows.dated)

    send_email(to=email_to,sender=EMAIL_SENDER,subject=subject,message=message)

@auth.requires_login()
def feedback_staff():
    grid1=SQLFORM.grid(db.Feedback,editable=False, create=False,deletable=False)
    return dict(grid=grid1,heading='Feedbacks Recieved')

@auth.requires_login()
def medicine_requests_staff():
    grid1=SQLFORM.grid(db.EquipmentsChemicals,editable=False, create=False,deletable=False)
    return dict(grid=grid1,heading='Requests for Stocks')

@auth.requires_login()
def stock_staff():
    grid1=SQLFORM.grid(db.Stock,searchable=True,editable=True, create=True,deletable=True)
    return dict(grid=grid1,heading='Medicines Available')
