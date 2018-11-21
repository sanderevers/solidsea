from authlib.specs.oidc import grants as oidc_grants
from authlib.specs.rfc7519 import JWT
from authlib.specs.rfc6749.util import scope_to_list
from authlib.specs.oidc.models import AuthorizationCodeMixin
from authlib.specs.oidc import UserInfo

from .encryption import encryption
from .user import User

import json
import time

class OpenIDCodeGrant(oidc_grants.OpenIDCodeGrant):
    def create_authorization_code(self, client, grant_user, request):

        # instead of creating a shared-secret auth code bound to the client in the DB,
        # we already create the id token info but send it to the client encrypted.

        token_info = {
            'sub' : grant_user.generate_user_info(scope_to_list(request.scope))['sub'],
            'scope': request.scope,
            'auth_time': int(time.time()),
            'redirect_uri': client.redirect_uri,
            'client_id' : client.client_id,
            'nonce': request.data.get('nonce'),
        }

        return encryption.encrypt_and_serialize(json.dumps(token_info))

    def parse_authorization_code(self, code, client):
        jwt_string = encryption.deserialize_and_decrypt(code)

        # issuer = self.server.config['jwt_iss']
        # options = {
        #     'iss' : {'essential':True, 'value':issuer},
        #     'aud' : {'essential':True, 'value':client.client_id},
        #     'exp' : {'essential':True}
        # }
        # id_token = JWT().decode(jwt_string, encryption.pubkey_data, claims_options=options)
        # id_token.validate()

        return IdTokenAuthorizationCode(json.loads(jwt_string))

    # we don't support nonce checking
    def exists_nonce(self, nonce, request):
        return False

    def delete_authorization_code(self, authorization_code):
        pass

    def authenticate_user(self, authorization_code):
        return authorization_code.get_user()


class IdTokenAuthorizationCode(AuthorizationCodeMixin):
    def __init__(self, id_token):
        self.id_token = id_token

    def get_redirect_uri(self):
        return self.id_token.get('redirect_uri')

    def get_user(self):
        sub = self.id_token.get('sub')
        return User(sub, UserInfo(sub=sub))

    def get_scope(self):
        return 'openid'

    def get_nonce(self):
        return self.id_token.get('nonce')

    def get_auth_time(self):
        return self.id_token.get('auth_time')

