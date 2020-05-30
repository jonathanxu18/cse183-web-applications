from py4web import action, URL, request
from yatl.helpers import XML
from py4web.utils.url_signer import URLSigner
from py4web.core import Fixture

# ThumbRater is a child class of Fixture
class ThumbRater(Fixture):

    # Syntax for Thumbrater component used in index.html
    THUMBRATER = '<thumbrater url="{url}" callback_url="{callback_url}"></thumbrater>'

    # When ThumbRater object is initialized
    def __init__(self, url, session, signer=None, db=None, auth=None):

        # Creating generic get/set URLS
        self.url = url + '/get'

        self.callback_url = url + '/set'
        
        # Setting URL Signer
        self.signer = signer or URLSigner(session)

        #
        self.__prerequisites__ = [session]

        # Set each element to None in args
        args = list(filter(None, [session, db, auth, self.signer.verify()]))

        # *var in a function call unpacks a list or tuple into positional arguments
        # Gets the rating from database based on id

        # Equivalent of:
        # @action('url/<id>', method=["GET"])
        # @action.uses(session, db, auth, signer.verify())
        # def get_thumb():

        f = action.uses(*args)(self.get_rating)
        action(self.url + "/<id>", method=["GET"])(f)

        # Sets/Updates the rating in database based on id

        # Equivalent of:
        # @action('callback_url</id>', method=["GET"])
        # @action.uses(session, db, auth, signer.verify())
        # def set_thumb():

        f = action.uses(*args)(self.set_rating)
        action(self.callback_url + "/<id>", method=["GET"])(f)

        


        
    # Called when object instantiated from ThumbRater is called
    # Ex. obj = ThumbRater()
    #     obj() <--
    # Filling in placeholders for THUMBRATER string
    # We use call() since we need to know the id before creating the URL 
    def __call__(self, id=None):
        return XML(ThumbRater.THUMBRATER.format(url = URL(self.url, id, signer=self.signer),
            callback_url = URL(self.callback_url, id, signer=self.signer)))
        
    # ------- Generic since the subclass implements the behavior -------

    # See controllers.py for implementation

    # Gets the rating of the object for a given id
    def get_rating(self, id=None):
        return dict(rating=0)

    # Sets the rating of the object for a given id
    def set_rating(self, id=None):
        return "set_rating"


    
