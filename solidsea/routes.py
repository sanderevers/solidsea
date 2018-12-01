from flask import Blueprint, request, session, current_app
from flask import render_template, render_template_string, jsonify, url_for, make_response, Request
from authlib.client.errors import OAuthError
from authlib.specs.rfc6749.errors import OAuth2Error
from .oidc_server import auth_server
from .federation import federation
from .user import User
from .encryption import encryption
import json

bp = Blueprint('home', __name__)

def remember_own_flow():
    own_flow = request.endpoint, request.view_args, request.args
    session['own_flow'] = own_flow

def recall_own_flow():
    return session.pop('own_flow', None)

@bp.route('/.well-known/openid-configuration')
def discovery_document():
    doc = {
        'issuer': auth_server.config['jwt_iss'],
        'authorization_endpoint': url_for('.authorize', _external=True),
        'token_endpoint': url_for('.token', _external=True),
        'jwks_uri': url_for('.jwks', _external=True),
    }
    return jsonify(doc)


@bp.route('/jwks.json')
def jwks():
    jwks = {'keys':[encryption.pubkey_jwk_dict]}
    return make_response(json.dumps(jwks), {'Content-Type':'application/json'})


@bp.route('/authorize')
def authorize():
    try:
        auth_server.validate_consent_request()
    except OAuth2Error:
        return auth_server.create_authorization_response()

    federate = request.args.get('federate')
    if federate:
        return federate_login(federate)
    else:
        try:
            with current_app.open_instance_resource('federate.html','r') as f:
                return render_template_string(f.read(), qp=request.args)
        except IOError:
            return render_template('federate.html', qp=request.args)

def federate_login(client_name):
    fed_client = federation.get(client_name)
    if not fed_client:
        return auth_server.create_authorization_response() # access_denied error response
    remember_own_flow()
    redirect_uri = url_for('.callback', name=client_name, _external=True)
    return fed_client.authorize_redirect(redirect_uri)

@bp.route('/federate/<name>/callback')
def callback(name):
    endpoint, view_args, req_args = recall_own_flow()
    if request.args.get('error'):
        return auth_server.create_authorization_response() # access_denied error response

    fed_client = federation.get(name)
    try:
        fed_client.authorize_access_token()
    except OAuthError:
        return auth_server.create_authorization_response()

    user_info = fed_client.fetch_user_info()
    user = User(user_info.sub, user_info)

    auth_url = url_for(endpoint,**view_args,**req_args,_external=True)
    base_url, query_string = auth_url.split('?',1)
    auth_req =  Request.from_values(base_url=base_url, query_string=query_string.encode())
#    g.redirect_uri = req_args.get('redirect_uri')
    return auth_server.create_authorization_response(auth_req, grant_user=user)

@bp.route('/token', methods=['POST'])
def token():
    return auth_server.create_token_response()
