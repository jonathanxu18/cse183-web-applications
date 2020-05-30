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
from . models import get_user_email

url_signer = URLSigner(session)

# The auth.user below forces login.
@action('index')
@action.uses('index.html', url_signer, auth.user)
def index():
    get_posts_url = URL('get_posts', signer=url_signer)

    return dict(
        # This is an example of a signed URL for the callback.
        get_posts_url = URL('get_posts', signer=url_signer),
        add_post_url = URL('add_post', signer=url_signer),
        delete_post_url = URL('delete_post', signer=url_signer),
        get_ratings_url = URL('get_ratings', signer=url_signer),
        set_rating_url = URL('set_rating', signer=url_signer),

        user_email = get_user_email(),
        username = auth.current_user.get('first_name') + " " + auth.current_user.get("last_name")
    )

# Loads the posts 
@action('get_posts')
@action.uses(url_signer.verify(), db, auth.user)
def get_posts():

    posts = db(db.post).select().as_list()

    for post in posts:
        # To prevent reassigning first/name again
        if post.get('name') is None:
            email = post['user_email']

            # .first() since only need one element
            p = db(db.auth_user.email == email).select().first()
            name = p.first_name + " " + p.last_name if p is not None else "Unknown"
            post["name"] = name

            #thumbs = db(db.thumb.post_id == post.get('id')) & (db.thumb.user_email == email)).select().as_list()
    return dict(posts=posts)

# Add new post 
@action('add_post', method="POST")
@action.uses(url_signer.verify(), db, auth.user)
def add_post():
    # The insert() method returns the id of the element
    id = db.post.insert(
        post_text = request.json.get('post_text')
    )

    return dict(id=id)

@action('delete_post', method="POST")
@action.uses(url_signer.verify(), db)
def delete_post():
    # ID of post we want to delete
    id = request.json.get('post_id')

    # Deleting element corresponding to post
    del db.post[id]

    return dict()

@action('get_ratings', method="GET")
@action.uses(url_signer.verify(), db, auth.user)
def get_ratings():
    
    id = request.params.get('post_id')
    user_email = auth.current_user.get('email')

    rating_entry = db((db.thumb.post_id == id) & (db.thumb.user_email == user_email)).select().first() 

    rating = rating_entry.rating if rating_entry is not None else 0
    
    return dict(rating=rating)

@action('set_rating', method="POST")
@action.uses(url_signer.verify(), db, auth.user)
def set_rating():
    
    id = request.json.get('post_id')
    rating = request.json.get('post_rating')
    user = auth.current_user.get('email')
    
    db.thumb.update_or_insert( 
        ((db.thumb.user_email == user) & (db.thumb.post_id == id)), 
        rating=rating
    ) 

    # Confirmation in network tab
    return 'good'