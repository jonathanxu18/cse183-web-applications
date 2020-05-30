"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

import uuid

from py4web import action, request, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner

from yatl.helpers import A
from . common import db, session, T, cache, auth, signed_url


url_signer = URLSigner(session)

# The auth.user below forces login.
@action('index', method='GET')
@action.uses('index.html', auth.user, session, db, url_signer)
def index():
    user_email = auth.current_user.get('email')

    # Queries all the contacts in a list
    rows = db(db.contacts.user_email == user_email).select()

    # Iterating over the contacts
    for row in rows:
        
        phone_list = []

        # Querying all the phone numbers associated with current contact
        # based on foreign key
        phone_numbers = db(db.phone_numbers.contact_id == row.id).select()

        # Iterating over the phone numbers
        for phone in phone_numbers:

            # Putting phone numbers into formatted string
            phone_list.append("{0} ({1})".format(phone.phone_number, phone.kind))

        phone_string = ", ".join(phone_list)

        # Creating new field in contact 
        row['phone_numbers'] = phone_string

    return dict(rows=rows, url_signer=url_signer)

@action('add_contact', method=['GET', 'POST'])
@action.uses('add_contact.html', session, db)
def add_contact():

    # Form displayed to user
    form = Form(db.contacts, csrf_session=session, formstyle=FormStyleBulma, validation=validate_contact)

    # Form inputs were accepted redirect to home page
    if form.accepted:
        redirect(URL('index'))

    return dict(form=form)

@action('edit_contact/<contact_id>', method=['GET','POST'])
@action.uses('add_contact.html', auth.user, session, db)
def edit_contact(contact_id=None):

    contact = db.contacts[contact_id]
    user = auth.current_user.get('email')

    # Contact DNE or belongs to different user
    if contact is None or contact.user_email != user:
        redirect(URL('index'))
    
    # Display the form corresponding to contact
    form = Form(db.contacts, record=contact, deletable=False, csrf_session=session, formstyle=FormStyleBulma, validation=validate_contact)

    if form.accepted:
        redirect(URL('index'))

    return dict(form=form)

@action('delete_contact', method=['GET', 'POST'])
@action.uses('index.html', session, db, url_signer.verify())
def delete_contact():

    parameters = request.params  
    row_id = parameters['contact_id']

    del db.contacts[row_id]

    redirect(URL('index'))

    return dict()

@action('edit_phones/<contact_id>', method=['GET'])
@action.uses('edit_phones.html', auth.user, db)
def edit_phones(contact_id=None):

    contact = db.contacts[contact_id]
    user_email = auth.current_user.get('email')

    # Contact DNE or belongs to different user
    if contact is None or contact.user_email != user_email:
        redirect(URL('index'))

    # Retrieve contact from database based on id
    contact = db.contacts[contact_id]

    rows = db(db.phone_numbers.contact_id == contact_id).select()
    
    first_name = contact.first_name
    last_name = contact.last_name

    return dict(rows=rows, first_name=first_name, last_name=last_name, contact_id=contact_id, url_signer=url_signer)

@action('add_phone/<contact_id>', method=['GET', 'POST'])
@action.uses('add_phone.html', auth.user, session, db)
def add_phone(contact_id=None):

    # Retrieving First/Last name for header
    contact = db.contacts[contact_id]
    first_name = contact.first_name
    last_name = contact.last_name

    user_email = auth.current_user.get('email')

    # Contact DNE or belongs to different user
    if contact is None or contact.user_email != user_email:
        redirect(URL('index'))

    # Creating form to add phone number
    form = Form([Field('phone_number'), (Field('kind'))], csrf_session=session, formstyle=FormStyleBulma, validation=validate_phone)

    # Inserting phone number into phone_numbers table
    # Redirecting to edit_phones page
    if form.accepted:

        phone_number = form.vars['phone_number']
        kind = form.vars['kind']
        db.phone_numbers.insert(phone_number=phone_number, kind=kind, contact_id=contact_id)

        redirect(URL('edit_phones', contact_id))

    return dict(form=form, first_name=first_name, last_name=last_name)

@action('edit_phone/<contact_id>/<phone_id>', method=['GET','POST'])
@action.uses('add_phone.html', auth.user, session, db, url_signer)
def edit_phone(contact_id=None, phone_id=None):

    # Validation
    contact = db.contacts[contact_id]
    user_email = auth.current_user.get('email')

    # Contact DNE or belongs to different user
    if contact is None or contact.user_email != user_email:
        redirect(URL('index'))

    # Retrieving First/Last name for header
    first_name = contact.first_name
    last_name = contact.last_name

    # Getting the current phone number
    phone = db.phone_numbers[phone_id]

    phone_number = phone.phone_number
    kind = phone.kind

    # Create form to display 
    # Retrieve current phone_number, kind values
    form = Form([Field('phone_number'), Field('kind')], record=dict(phone_number=phone_number, kind=kind), 
                deletable=False, csrf_session=session, formstyle=FormStyleBulma, validation=validate_phone)
    
    if form.accepted:

        # Retriving updated values from form
        phone_number = form.vars['phone_number']
        kind = form.vars['kind']

        # Updating values in phone_number table
        phone.update_record(phone_number=phone_number,kind=kind)

        redirect(URL('edit_phones', contact_id))

    return dict(form=form, first_name=first_name, last_name=last_name)

@action('delete_phone/<contact_id>/<phone_id>', method=['GET', 'POST'])
@action.uses(session, db, url_signer.verify())
def delete_phone(contact_id=None, phone_id=None):

    del db.phone_numbers[phone_id]
    redirect(URL('edit_phones', contact_id))
    
    return dict()

# Helper function for empty fields in Contact form
def validate_contact(form):

    first_name = form.vars['first_name']
    last_name = form.vars['last_name']

    if first_name is None:
        form.errors['first_name'] = T("Enter your first name")
    
    if last_name is None:
        form.errors['last_name'] = T("Enter your last name")


# Helper function for empty fields in Phone numbers form
def validate_phone(form):

    phone_number = form.vars['phone_number']
    kind = form.vars['kind']

    if len(phone_number) == 0:
        form.errors['phone_number'] = T("Enter your phone number")
    
    if len(kind) == 0:
        form.errors['kind'] = T("Enter kind of phone number")


    


