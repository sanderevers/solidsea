from authlib.specs.rfc6749.models import ClientMixin

class StaticClient(ClientMixin):
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id # is read in OpenIDMixin.generate_id_token
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def check_redirect_uri(self, redirect_uri):
        return self.redirect_uri == redirect_uri

    def has_client_secret(self):
        return self.client_secret is not None

    def check_client_secret(self, client_secret):
        return client_secret==self.client_secret

    def check_token_endpoint_auth_method(self, method):
        if self.has_client_secret():
            return method=='client_secret_basic'
        else:
            return method=='none'

    def check_response_type(self, response_type):
        return response_type in ('code','id_token token')

    def check_grant_type(self, grant_type):
        return grant_type in ('authorization_code','implicit')

    def check_requested_scopes(self, scopes):
        return set(scopes) == {'openid'}

static_clients = {}

def init_my_clients(app):
    client_id = app.config['MY_CLIENT_ID']
    client_secret = app.config['MY_CLIENT_SECRET']
    redirect_uri = app.config['MY_CLIENT_REDIRECT_URI']
    static_clients[client_id] = StaticClient(client_id, client_secret, redirect_uri)
    static_clients['nonconf'] = StaticClient('nonconf', None, redirect_uri)

def find_client(client_id):
    return static_clients.get(client_id)