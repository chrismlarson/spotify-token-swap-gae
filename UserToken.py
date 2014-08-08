from google.appengine.ext import ndb


class UserToken(ndb.Model):
    username = ndb.StringProperty(required=True)
    refresh_token = ndb.StringProperty(required=True)