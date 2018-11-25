from authlib.flask.oauth2 import AuthorizationServer
from authlib.specs.oidc.grants import OpenIDImplicitGrant

from .auth_code_flow import OpenIDCodeGrant
from .myclients import find_client
from .encryption import encryption

def save_token(token, client):
    pass

class MyOpenIDImplicitGrant(OpenIDImplicitGrant):
    # we don't support nonce checking
    def exists_nonce(self, nonce, request):
        return False

def oidc_server_init_app(app):
    app.config['OAUTH2_JWT_KEY'] = encryption.privkey_jwk_dict
    auth_server.init_app(app)

    auth_server.register_grant(MyOpenIDImplicitGrant)
    auth_server.register_grant(OpenIDCodeGrant)

auth_server = AuthorizationServer(query_client=find_client, save_token=save_token)

