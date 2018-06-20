from authlib.flask.client import OAuth, RemoteApp
from authlib.specs.oidc.grants.base import UserInfo
from authlib.specs.rfc7519 import JWT
from authlib.specs.rfc7517 import JWK
from authlib.specs.rfc7518 import JWK_ALGORITHMS

import json

from flask import session, current_app


class Federation:
    def __init__(self):
        self.clients = set()
        self._authlib_clients = OAuth()

    def register(self, client_name, **kwargs):
        self.clients.add(client_name)
        self._authlib_clients.register(client_name, **kwargs)

    def get(self, client_name):
        if client_name in self.clients:
            return self._authlib_clients.create_client(client_name)
        return None

    def init_app(self, app):
        self._authlib_clients.init_app(app)
        self.register('github', client_cls=GithubClient)
        self.register('twitter', client_cls=TwitterClient)
        self.register('google', client_cls=GoogleClient)


class GithubClient(RemoteApp):
    def __init__(self, name, **kwargs):
        kwargs['client_kwargs'] = {'scope':''}
        super().__init__(name, **kwargs)

    def fetch_user_info(self):
        github_user = self.get('user').json()
        sub = 'github/' + github_user['login']
        return UserInfo(sub=sub)


class TwitterClient(RemoteApp):
    def __init__(self, name, **kwargs):
        super().__init__(name, save_request_token=self.save_request_token, fetch_request_token=self.fetch_request_token, **kwargs)

    def save_request_token(self, token):
        session['request_token_twitter'] = token

    def fetch_request_token(self):
        return session.pop('request_token_twitter')

    def fetch_user_info(self):
        sub = 'twitter/' + self.token['screen_name']
        return UserInfo(sub=sub)

class GoogleClient(RemoteApp):
    def __init__(self, name, **kwargs):
        kwargs['client_kwargs'] = {'scope':'openid email'}
        super().__init__(name, **kwargs)

    def fetch_user_info(self):
        jwt_issuer = 'https://accounts.google.com'
        options = {
            'iss' : {'essential':True, 'value':jwt_issuer},
            'aud' : {'essential':True, 'value':self.client_id},
            'exp' : {'essential':True}
        }
        id_token = JWT().decode(self.token['id_token'], load_key, claims_options=options)
        id_token.validate()
        sub = 'google/' + id_token.sub
        return UserInfo(sub=sub)


def load_key(header, payload):
    kid = header['kid']
    with current_app.open_instance_resource('google_certs', 'r') as f:
        google_certs = f.read()
    jwk = JWK(algorithms=JWK_ALGORITHMS)
    key = jwk.loads(json.loads(google_certs),kid)
    return key

federation = Federation()
