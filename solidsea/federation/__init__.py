from authlib.flask.client import OAuth, RemoteApp
import logging
from importlib import import_module

'''Registers the OAuth clients whose names are included in the config variable FEDERATION.
Clients are configured using variables

{client_name}_CLIENT_ID
{client_name}_CLIENT_SECRET
{client_name}_AUTHORIZE_URL
{client_name}_ACCESS_TOKEN_URL
{client_name}_REQUEST_TOKEN_URL (for OAuth1 clients)

To use a custom Python class (instead of authlib.flask.client.RemoteApp) for a client,
create a module with a class named Client and put its name in
{client_name}_CLIENT_MODULE.
'''
class Federation:
    def __init__(self):
        self.clients = []
        self._authlib_clients = OAuth()

    def register(self, client_name, **kwargs):
        self.clients.append(client_name)
        self._authlib_clients.register(client_name, **kwargs)

    def get(self, client_name):
        if client_name in self.clients:
            return self._authlib_clients.create_client(client_name)
        return None

    def init_app(self, app):
        for client_name in app.config['FEDERATION']:
            log.info('Registering client "{}"'.format(client_name))
            module_name = app.config.get('{}_CLIENT_MODULE'.format(client_name.upper()))
            self.register(client_name, client_cls=get_client_cls(module_name))
        self._authlib_clients.init_app(app)

def get_client_cls(module_name):
    if not module_name:
        return RemoteApp
    pkg = None
    if module_name[0] == '.':
        pkg = __name__
    return import_module(module_name, pkg).Client


log = logging.getLogger(__name__)
federation = Federation()
