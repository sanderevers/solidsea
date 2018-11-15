from flask import Blueprint, request, session, g
from flask import render_template, redirect, jsonify, url_for, make_response, Request
from authlib.client.errors import OAuthError
from authlib.common.security import generate_token
from .oidc_server import auth_server
from .federation import federation
from .user import User
from .encryption import encryption
from copy import copy
from urllib.parse import quote_plus
import json

bp = Blueprint('home', __name__)

def remember_own_flow():
    own_flow = request.endpoint, request.view_args, request.args
    session['own_flow'] = own_flow

def recall_own_flow():
    return session.pop('own_flow', None)

# def remember_own_flow_args():
#     own_flow_args = {}
#     for arg in ('scope','client_id','state','nonce','response_type','redirect_uri'):
#         if request.args.get(arg):
#             own_flow_args[arg] = request.args[arg] # or encode it in state?
#     session['own_flow_args'] = own_flow_args
#
# def recall_own_flow_args():
#     return session.pop('own_flow_args')

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
    jwks = {'keys':[json.loads(encryption.pubkey_json)]}
    return make_response(json.dumps(jwks), {'Content-Type':'application/json'})

@bp.route('/authorize')
def authorize():
    #validate_consent_request ?
    federate = request.args.get('federate')
    if federate:
        return federate_login(federate)
    else:
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
    g.redirect_uri = req_args.get('redirect_uri')
    return auth_server.create_authorization_response(auth_req, grant_user=user)

@bp.route('/token', methods=['POST'])
def token():
    return auth_server.create_token_response()

# @bp.route('/profile/github')
# def profile_github():
#     resp = federation.get('github').get('user')
#     profile = resp.json()
#     return 'got user {}'.format(profile)


# @bp.route('/api/me')
# @require_oauth('profile')
# def api_me():
#     user = current_token.user
#     return jsonify(id=user.id, username=user.username)
