from flask import Blueprint, request, session
from flask import render_template, redirect, jsonify, json, url_for
from authlib.client.errors import OAuthException
from .oauth2_server import auth_server
from .federation import federation
from .user import User


bp = Blueprint(__name__, 'home')

def remember_own_flow_args():
    own_flow_args = {}
    for arg in ('scope','client_id','state','nonce','response_type','redirect_uri'):
        if request.args.get(arg):
            own_flow_args[arg] = request.args[arg] # or encode it in state?
    session['own_flow_args'] = own_flow_args

def recall_own_flow_args():
    return session.pop('own_flow_args')

@bp.route('/authorize')
def authorize():
    federate = request.args.get('federate')
    if federate:
        return federate_login(federate)
    else:
        return render_template('federate.html', qp=request.args)

def federate_login(client_name):
    fed_client = federation.get(client_name)
    if not fed_client:
        return auth_server.create_authorization_response() # access_denied error response
    remember_own_flow_args()
    redirect_uri = url_for('.callback', name=client_name, _external=True)
    return fed_client.authorize_redirect(redirect_uri)

@bp.route('/federate/<name>/callback')
def callback(name):
    own_flow_args = recall_own_flow_args()
    if request.args.get('error'):
        return auth_server.create_authorization_response() # access_denied error response

    fed_client = federation.get(name)
    try:
        fed_client.authorize_access_token()
    except OAuthException:
        return auth_server.create_authorization_response()

    user_info = fed_client.fetch_user_info()
    user = User(user_info.sub, user_info)

    # hack the current request
    # starting authlib 0.8 we can use auth_server.create_authorization_response(request,user)
    request.url = request.url + ''.join('&{}={}'.format(k, v) for k, v in own_flow_args.items())
    return auth_server.create_authorization_response(grant_user=user)

@bp.route('/token', methods=['POST'])
def issue_token():
    return auth_server.create_token_response()

@bp.route('/profile/github')
def profile_github():
    resp = federation.get('github').get('user')
    profile = resp.json()
    return 'got user {}'.format(profile)


# @bp.route('/api/me')
# @require_oauth('profile')
# def api_me():
#     user = current_token.user
#     return jsonify(id=user.id, username=user.username)
