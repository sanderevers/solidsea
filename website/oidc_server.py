from authlib.flask.oauth2 import AuthorizationServer
from authlib.specs.oidc.grants import OpenIDImplicitGrant

from .oidc_flow import OpenIDCodeGrant
from .myclients import find_client
from .encryption import encryption
import json

def save_token(token, client):
    pass

# sorry, we'll leave this to the client
def exists_nonce(nonce,request):
    return False

def oidc_server_init_app(app):

    app.config['OAUTH2_JWT_KEY'] = json.loads(encryption.privkey_json)
    auth_server.init_app(app)

    # support all grants
    auth_server.register_grant(OpenIDImplicitGrant)
    auth_server.register_grant(OpenIDCodeGrant)
    auth_server.register_hook('exists_nonce', exists_nonce)

auth_server = AuthorizationServer(query_client=find_client, save_token=save_token)

