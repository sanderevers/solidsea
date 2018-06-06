from authlib.specs.oidc import grants as oidc_grants
from authlib.specs.rfc7519 import JWT
from authlib.specs.oidc.models import AuthorizationCodeMixin
from authlib.specs.rfc6749.wrappers import OAuth2Request

from flask import request as flask_req
from .encryption import encryption
from .user import User

class OpenIDCodeGrant(oidc_grants.OpenIDCodeGrant):
    def create_authorization_code(self, client, grant_user, request):

        # openid request MAY have "nonce" parameter
        nonce = request.data.get('nonce')

        # instead of creating a shared-secret auth code bound to the client in the DB,
        # we already create the id token but send it to the client encrypted.

        token = {'scope': request.scope}
        id_token = self.generate_id_token(token, request, nonce=nonce)

        return encryption.encrypt_and_serialize(id_token)

    # hack to get redirect_uri into the authorization code
    def generate_user_info(self, user, scopes):
        user_info = super().generate_user_info(user,scopes)
        user_info['redirect_uri'] = _create_oauth2_request(flask_req).redirect_uri
        return user_info

    def parse_authorization_code(self, code, client):
        jwt_string = encryption.deserialize_and_decrypt(code)

        issuer = self.server.config['jwt_iss']

        options = {
            'iss' : {'essential':True, 'value':issuer},
            'aud' : {'essential':True, 'value':client.client_id},
            'exp' : {'essential':True}
        }
        id_token = JWT().decode(jwt_string, encryption.pubkey_data, claims_options=options)
        id_token.validate()

        return IdTokenAuthorizationCode(id_token)


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
        return User(self.id_token.get('sub'))

    def get_scope(self):
        return 'openid'

    def get_nonce(self):
        return self.id_token.get('nonce')

    def get_auth_time(self):
        return self.id_token.get('auth_time')

def _create_oauth2_request(q):
    if q.method == 'POST':
        body = q.form.to_dict(flat=True)
    else:
        body = None

    return OAuth2Request(
        q.method,
        q.url,
        body,
        q.headers
    )
