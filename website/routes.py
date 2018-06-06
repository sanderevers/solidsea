from flask import Blueprint, request, session
from flask import render_template, redirect, jsonify, json, url_for
from werkzeug.security import gen_salt
from authlib.flask.oauth2 import current_token
from authlib.specs.rfc6749 import OAuth2Error
from .oauth2_server import auth_server
from .oauth2_client import oauth2_clients
from .user import User

bp = Blueprint(__name__, 'home')

@bp.route('/authorize', methods=['GET', 'POST'])
def authorize():
    federate = request.args.get('federate') or session.get('federate')
    own_flow_args = {}
    for arg in ('scope','client_id','state','nonce','response_type','redirect_uri'):
        if request.args.get(arg):
            own_flow_args[arg] = request.args[arg] # or encode it in state?
    if federate == 'twitter':
        session['twitter_state'] = own_flow_args
        return federate_login(federate)
    elif federate == 'github':
        return federate_login(federate, **own_flow_args)
    else:
        return render_template('federate.html',qp=request.args)

@bp.route('/federate/<name>')
def federate_login(name, **extra_args):
    fed_client = oauth2_clients.create_client(name)
    redirect_uri = url_for('.callback', name=name, _external=True, **extra_args)
    return fed_client.authorize_redirect(redirect_uri)

@bp.route('/federate/<name>/callback')
def callback(name):
    client = oauth2_clients.create_client(name)
    token = client.authorize_access_token()
    if name=='twitter':
        username = 'twitter/' + token['screen_name']
        own_flow_args = session.pop('twitter_state')
        request.url = request.url + ''.join('&{}={}'.format(k,v) for k,v in own_flow_args.items())
    elif name=='github':
        github_user = oauth2_clients.github.get('user').json()
        username = 'github/' + github_user['login']
    grant_user = User(username)

    # request.args = request.args.copy()
    # for arg in ('scope','client_id','state','nonce','response_type','redirect_uri'):
    #     if request.args.get('own_'+arg):
    #         request.args[arg] = request.args['own_'+arg] # or encode it in state?

    return auth_server.create_authorization_response(grant_user=grant_user) # use request param starting authlib 0.8

@bp.route('/token', methods=['POST'])
def issue_token():
    return auth_server.create_token_response()

@bp.route('/profile/github')
def profile_github():
    resp = oauth2_clients.github.get('user')
    profile = resp.json()
    return 'got user {}'.format(profile)


# @bp.route('/api/me')
# @require_oauth('profile')
# def api_me():
#     user = current_token.user
#     return jsonify(id=user.id, username=user.username)
