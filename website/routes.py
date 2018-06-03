from flask import Blueprint, request, session
from flask import render_template, redirect, jsonify, json, url_for
from werkzeug.security import gen_salt
from authlib.flask.oauth2 import current_token
from authlib.specs.rfc6749 import OAuth2Error
from .models import db, User, OAuth2Client
from .oauth2 import auth_server, require_oauth

from .oauth2_client import oauth2_clients


bp = Blueprint(__name__, 'home')


def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None

def get_or_create_user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
    return user


@bp.route('/', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        session['id'] = user.id
        return redirect('/')
    user = current_user()
    if user:
        clients = OAuth2Client.query.filter_by(user_id=user.id).all()
    else:
        clients = []
    return render_template('home.html', user=user, clients=clients)


@bp.route('/create_client', methods=('GET', 'POST'))
def create_client():
    user = current_user()
    if not user:
        return redirect('/')
    if request.method == 'GET':
        return render_template('create_client.html')
    client = OAuth2Client(**request.form.to_dict(flat=True))
    client.user_id = user.id
    client.client_id = gen_salt(24)
    if client.token_endpoint_auth_method == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)
    db.session.add(client)
    db.session.commit()
    return redirect('/')


@bp.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize_old():
    user = current_user()
    if request.method == 'GET':
        try:
            grant = auth_server.validate_consent_request(end_user=user)
        except OAuth2Error as error:
            return error.error
        return render_template('authorize.html', user=user, grant=grant)
    if not user and 'username' in request.form:
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
    if request.form['confirm']:
        grant_user = user
    else:
        grant_user = None
    return auth_server.create_authorization_response(grant_user=grant_user)

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
    grant_user = get_or_create_user(username)

    # request.args = request.args.copy()
    # for arg in ('scope','client_id','state','nonce','response_type','redirect_uri'):
    #     if request.args.get('own_'+arg):
    #         request.args[arg] = request.args['own_'+arg] # or encode it in state?

    return auth_server.create_authorization_response(grant_user=grant_user) # use request param starting authlib 0.8

    # session['access_token_'+name] = token
    # if name=='twitter':
    #     uid = token['user_id'] #int?
    #     username = token['screen_name']
    # return 'got token {}'.format(token)

@bp.route('/profile/github')
def profile_github():
    resp = oauth2_clients.github.get('user')
    profile = resp.json()
    return 'got user {}'.format(profile)



@bp.route('/oauth/token', methods=['POST'])
def issue_token():
    print(request.form)
    return auth_server.create_token_response()


@bp.route('/oauth/revoke', methods=['POST'])
def revoke_token():
    return auth_server.create_endpoint_response('revocation')


@bp.route('/api/me')
@require_oauth('profile')
def api_me():
    user = current_token.user
    return jsonify(id=user.id, username=user.username)
