"""
This file defines the database models
"""
import datetime

from . common import db, Field, auth
from pydal.validators import *

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#

# Get the user's email
def get_user_email():
    return auth.current_user.get('email')

# Contacts table
db.define_table(
    'contacts',
    Field('first_name'),
    Field('last_name'),
    # Used to query for certain user's contacts only
    Field('user_email', default=get_user_email)
)

# Phone Numbers table
db.define_table(
    'phone_numbers',
    Field('phone_number'),
    Field('kind'),
    Field('contact_id', 'reference contacts')
)


# Fields that will be hidden in forms
db.contacts.id.readable = False
db.contacts.user_email.readable = False


db.commit()
