from authlib.flask.oauth2 import AuthorizationServer
from authlib.specs.rfc6749.grants import ImplicitGrant

from .oidc_flow import OpenIDCodeGrant
from .myclients import find_client

auth_server = AuthorizationServer()

def save_token(token, client):
    pass

# sorry, we'll leave this to the client
def exists_nonce(nonce,request):
    return False

def config_oauth(app):

    with app.open_instance_resource(app.config['IDP_JWT_PRIV_KEY_PATH'], 'r') as f:
        app.config['OAUTH2_JWT_KEY'] = f.read()

    auth_server.init_app(
        app, query_client=find_client, save_token=save_token)

    # support all grants
    auth_server.register_grant(ImplicitGrant)
    auth_server.register_grant(OpenIDCodeGrant)
    auth_server.register_hook('exists_nonce', exists_nonce)


