from authlib.flask.client import RemoteApp
from authlib.specs.oidc import UserInfo

class Client(RemoteApp):
    def __init__(self, name, **kwargs):
        kwargs['client_kwargs'] = {'scope':''}
        super().__init__(name, **kwargs)

    def fetch_user_info(self):
        github_user = self.get('user').json()
        sub = self.name + '/' + github_user['login']
        return UserInfo(sub=sub)