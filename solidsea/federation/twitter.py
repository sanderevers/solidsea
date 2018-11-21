from authlib.flask.client import RemoteApp
from authlib.specs.oidc import UserInfo

from flask import session

class Client(RemoteApp):
    def __init__(self, name, **kwargs):
        super().__init__(name, save_request_token=self.save_request_token, fetch_request_token=self.fetch_request_token, **kwargs)

    def save_request_token(self, token):
        session['request_token_twitter'] = token

    def fetch_request_token(self):
        return session.pop('request_token_twitter')

    def fetch_user_info(self):
        sub = self.name + '/' + self.token['screen_name']
        return UserInfo(sub=sub)