from authlib.flask.client import OAuth, RemoteApp
from authlib.specs.oidc.grants.base import UserInfo

from flask import session


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
        self._authlib_clients.register('github', client_cls=GithubClient)
        self._authlib_clients.register('twitter', client_cls=TwitterClient)


class GithubClient(RemoteApp):
    def __init__(self, name, **kwargs):
        super().__init__(name, fetch_token = self.fetch_token, client_kwargs={'scope':''}, **kwargs)

    def fetch_token(self):
        raise NotImplementedError()

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

federation = Federation()
