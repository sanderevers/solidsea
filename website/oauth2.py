from authlib.flask.oauth2 import AuthorizationServer, ResourceProtector
from authlib.flask.oauth2.sqla import (
    create_query_client_func,
    create_save_token_func,
    create_revocation_endpoint,
    create_bearer_token_validator,
)
from authlib.specs.rfc6749 import grants
from authlib.specs.rfc6749.wrappers import OAuth2Request
from authlib.specs.oidc import grants as oidc_grants
from authlib.specs.rfc7519 import JWT

from authlib.specs.oidc.models import AuthorizationCodeMixin

from flask import request as flask_req

from .models import db, User
from .models import OAuth2Client #, OAuth2AuthorizationCode, OAuth2Token
from jwcrypto import jwe, jwk
from jwcrypto.common import json_encode

class OpenIDCodeGrant(oidc_grants.OpenIDCodeGrant):
    def create_authorization_code(self, client, grant_user, request):

        # instead of creating a shared-secret auth code bound to the client in the DB,
        # we already create the id token but send it to the client encrypted.

        # token = self.generate_token(
        #     client,
        #     self.GRANT_TYPE,
        #     scope=request.scope,
        #     include_refresh_token=client.has_client_secret(),
        # )

        token = {'scope': request.scope}

        # openid request MAY have "nonce" parameter
        nonce = request.data.get('nonce')

        id_token = self.generate_id_token(token, request, nonce=nonce)

        return _encrypt_and_serialize(id_token)

    # hack to get redirect_uri into the authorization code
    def generate_user_info(self, user, scopes):
        user_info = super().generate_user_info(user,scopes)
        user_info['redirect_uri'] = _create_oauth2_request(flask_req).redirect_uri
        return user_info

    def parse_authorization_code(self, code, client):
        jwt_string = _deserialize_and_decrypt(code)

        pubkey_data = auth_server.config['jwt_pub_key_data']
        issuer = auth_server.config['jwt_iss']

        options = {
            'iss' : {'essential':True, 'value':issuer},
            'aud' : {'essential':True, 'value':client.client_id},
            'exp' : {'essential':True}
        }
        id_token = JWT().decode(jwt_string, pubkey_data, claims_options=options)
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
        return User.query.filter_by(id=self.id_token.get('sub')).first()

    def get_scope(self):
        return 'openid'

    def get_nonce(self):
        return self.id_token.get('nonce')

    def get_auth_time(self):
        return self.id_token.get('auth_time')


# class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):
#     def authenticate_user(self, username, password):
#         user = User.query.filter_by(username=username).first()
#         if user.check_password(password):
#             return user
#
#
# class RefreshTokenGrant(grants.RefreshTokenGrant):
#     def authenticate_refresh_token(self, refresh_token):
#         item = OAuth2Token.query.filter_by(refresh_token=refresh_token).first()
#         if item and not item.is_refresh_token_expired():
#             return item
#
#     def authenticate_user(self, credential):
#         return User.query.get(credential.user_id)


auth_server = AuthorizationServer()
require_oauth = ResourceProtector()


def save_token(token, client):
    pass

# sorry, we'll leave this to the client
def exists_nonce(nonce,request):
    return False

def config_oauth(app):

    with app.open_instance_resource(app.config['IDP_JWT_PUB_KEY_PATH'], 'rb') as f:
        pubkey_data = f.read()
        auth_server.config['jwt_pub_key_data'] = pubkey_data

    with app.open_instance_resource(app.config['IDP_JWT_PRIV_KEY_PATH'], 'r') as f:
        app.config['OAUTH2_JWT_KEY'] = f.read()

    query_client = create_query_client_func(db.session, OAuth2Client)
    # save_token = create_save_token_func(db.session, OAuth2Token)
    auth_server.init_app(
        app, query_client=query_client, save_token=save_token)

    # support all grants
    auth_server.register_grant(grants.ImplicitGrant)
    auth_server.register_grant(grants.ClientCredentialsGrant)
    auth_server.register_grant(OpenIDCodeGrant)
    auth_server.register_hook('exists_nonce', exists_nonce)
#    authorization.register_grant(AuthorizationCodeGrant)
#     authorization.register_grant(PasswordGrant)
#     authorization.register_grant(RefreshTokenGrant)

    # support revocation
    # revocation_cls = create_revocation_endpoint(db.session, OAuth2Token)
    # authorization.register_endpoint(revocation_cls)

    # protect resource
    # bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
    # require_oauth.register_token_validator(bearer_cls())




def _encrypt_and_serialize(id_token):
    pubkey_data = auth_server.config['jwt_pub_key_data']
    pubkey = jwk.JWK.from_pem(pubkey_data)

    eprot = {'alg': 'RSA-OAEP', 'enc': 'A256GCM'}
    encrypted_id_token = jwe.JWE(id_token.encode('utf-8'), json_encode(eprot))
    encrypted_id_token.add_recipient(pubkey)

    return encrypted_id_token.serialize(compact=True)

def _deserialize_and_decrypt(auth_code):
    privkey_str = auth_server.config['jwt_key']
    privkey = jwk.JWK.from_pem(privkey_str.encode('utf-8'))

    jwe_token = jwe.JWE()
    jwe_token.deserialize(auth_code, key=privkey)
    return str(jwe_token.payload, 'utf-8')

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
