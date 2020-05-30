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

from yatl.helpers import A

# Importing URL Signer from common.py
from . common import db, session, T, cache, auth, signed_url

# Creating variable to store URL Signer
#url_signer = signed_url

# Home page
# Displays all the products in a table

# We need to have a session that stores the signature on the server
# Session -> an object that uniquely identifies a browser
# We want to store the signature onto the session -> cookie -> key,value

# Declares the URL
@action('index', method='GET')
# Declares the HTML template that is being filled
@action.uses('index.html', db, session, signed_url)
def view_products():

    # Get content of vars dictionary
    parameters = request.params

    state = parameters.get('sort')

    # Products currently unsorted or in descending order
    if state == 'asc':
        rows = db().select(db.product.ALL, orderby=db.product.product_cost)
    
    # Products currently in ascending order
    elif state == 'desc':
        rows = db().select(db.product.ALL, orderby=~db.product.product_cost)
    
    # Products currently unsorted
    else:
        # We get all the table rows, via a query.
        rows = db(db.product).select()
        
    # Dictionary to fill the holes in HTML template
    return dict(rows=rows, signed_url=signed_url, state=state)

# Add product page
# Produces a form at directed URL when the 'Add Product' button is clicked
@action('add_product', method=['GET', 'POST'])
@action.uses('product_form.html', session, db)
def add_product():

    # The form displayed to the user
    form = Form(db.product, csrf_session=session, formstyle=FormStyleBulma)

    # Form information was successfully taken in
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form)

@action('edit_product/<product_id>', method=['GET', 'POST'])
@action.uses('product_form.html', session, db)
def edit_product(product_id=None):
    """Note that in the above declaration, the product_id argument must match
    the <product_id> argument of the @action."""
    # We read the product.
    p = db.product[product_id]
    if p is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    
    # The form displayed to the user
    form = Form(db.product, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)

    # Form information was successfully taken in
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form)

# Uses POST since you are passing data to the server
# The data passed indicates which item to delete in the database

@action('delete_product', method=['GET', 'POST'])
@action.uses('index.html', session, db, signed_url.verify())
def delete_product():

    # Delete the item
    parameters = request.params
    row_id = parameters['product_id']

    del db.product[row_id]

    # Refresh the page
    redirect(URL('index'))








