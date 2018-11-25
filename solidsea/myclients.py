from authlib.specs.rfc6749.models import ClientMixin

class StaticClient(ClientMixin):
    def __init__(self, client_id, grant_type, redirect_uri, client_secret=None):
        self.client_id = client_id # is read in OpenIDMixin.generate_id_token
        self.client_secret = client_secret
        self.grant_type = grant_type
        self.redirect_uri = redirect_uri
        if grant_type=='authorization_code':
            assert client_secret
        elif grant_type=='implicit':
            assert not client_secret
        else:
            raise Exception('grant_type should be authorization_code or implicit')

    def check_redirect_uri(self, redirect_uri):
        return self.redirect_uri == redirect_uri

    def has_client_secret(self):
        return bool(self.client_secret)

    def check_client_secret(self, client_secret):
        return client_secret==self.client_secret

    def check_token_endpoint_auth_method(self, method):
        if self.has_client_secret():
            return method == 'client_secret_basic'
        else:
            return method == 'none'

    def check_response_type(self, response_type):
        grant_response_types = {
            'authorization_code' : 'code',
            'implicit': 'id_token'
        }
        return response_type == grant_response_types[self.grant_type]

    def check_grant_type(self, grant_type):
        return grant_type==self.grant_type

    def check_requested_scopes(self, scopes):
        return set(scopes) == {'openid'}

static_clients = {}

def init_my_clients(app):
    for client_conf in app.config['MY_CLIENTS']:
        static_clients[client_conf['client_id']] = StaticClient(**client_conf)

def find_client(client_id):
    return static_clients.get(client_id)