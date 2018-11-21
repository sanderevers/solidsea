from authlib.flask.client import RemoteApp
from authlib.specs.oidc import UserInfo
from authlib.specs.rfc7519 import JWT
from authlib.specs.rfc7517 import JWK
from authlib.specs.rfc7518 import JWK_ALGORITHMS

from flask import current_app

import requests
import logging

class Client(RemoteApp):
    def __init__(self, name, **kwargs):
        try:
            discovery_url = current_app.config['GOOGLE_DISCOVERY_URL']
            discovery = self.fetch_discovery(discovery_url)
            self.issuer = discovery['issuer']
            self.jwks_uri = discovery['jwks_uri']
            self.jwks = {'keys':[]}
            kwargs['client_kwargs'] = {'scope':'openid email'}
            kwargs['authorize_url'] = discovery['authorization_endpoint']
            kwargs['access_token_url'] = discovery['token_endpoint']
        except:
            log.error('Client "{}" not configured.'.format(name))
        super().__init__(name, **kwargs)

    def fetch_user_info(self):
        options = {
            'iss' : {'essential':True, 'value':self.issuer},
            'aud' : {'essential':True, 'value':self.client_id},
            'exp' : {'essential':True}
        }
        id_token = JWT().decode(self.token['id_token'], self.load_key, claims_options=options)
        id_token.validate() # checking signature is not strictly necessary but let's do it anyway
        sub = self.name + '/' + id_token.sub
        return UserInfo(sub=sub)

    def fetch_discovery(self, url):
        resp = requests.get(url)
        if not resp.status_code == 200:
            raise Exception('Google discovery URL {} returning {}.'.format(url, resp.status_code))
        return resp.json()

    def load_key(self, header, payload):
        kid = header['kid']
        if not any(key['kid']==kid for key in self.jwks['keys']):
            self.jwks = requests.get(self.jwks_uri).json()
        jwk = JWK(algorithms=JWK_ALGORITHMS)
        key = jwk.loads(self.jwks,kid)
        return key

log = logging.getLogger(__name__)