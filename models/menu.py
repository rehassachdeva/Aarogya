# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('web',SPAN(2),'py'),XML('&trade;&nbsp;'),
                  _class="navbar-brand",_href="http://www.web2py.com/",
                  _id="web2py-logo")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
response.meta.description = 'a cool new app'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################
response.menu =[]

if auth.user and auth.user.Category=='Patient':
    response.menu.append(('Home', True, URL(request.application,'default','Patient_index')))
    response.menu.append(('Medical Reports', False, URL(request.application,'default','report_patient')))
    response.menu.append(('Appointments', False, URL(request.application,'default','appointment_patient')))
    response.menu.append(('Medicines Available', False, URL(request.application,'default','medicine_patient')))
    response.menu.append(('Feedback', False, URL(request.application,'default','feedback_patient')))
    response.menu.append(('Medical Profile', False, URL(request.application,'default','profile_view_patient')))

if auth.user and auth.user.Category=='Doctor':
    response.menu.append(('Home', True, URL(request.application,'default','Doctor_index')))
    response.menu.append(('Medical Reports', False, URL(request.application,'default','report_doctor')))
    response.menu.append(('My Appointments', False, URL(request.application,'default','appointment_doctor')))
    response.menu.append(('My Calendar', False, URL(request.application,'default','mycal')))
    response.menu.append(('Medicines Available', False, URL(request.application,'default','medicine_doctor')))
    response.menu.append(('Request for New', False, URL(request.application,'default','request_doctor')))
    response.menu.append(('My Profile', False, URL(request.application,'default','profile_view_doctor')))
    
if auth.user and auth.user.Category=='Staff':
    response.menu.append(('Home', True, URL(request.application,'default','Staff_index')))
    response.menu.append(('Stock', False, URL(request.application,'default','stock_staff')))
    response.menu.append(('Requests for Stock', False, URL(request.application,'default','medicine_requests_staff')))
    response.menu.append(('Feedbacks Received', False, URL(request.application,'default','feedback_staff')))
    response.menu.append(('My Profile', False, URL(request.application,'default','profile_view_staff')))
