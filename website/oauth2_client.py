from authlib.flask.client import OAuth
from flask import session

oauth2_clients = OAuth()

def init_oauth2_clients(app):
    oauth2_clients.init_app(app)
    oauth2_clients.register('github', fetch_token = fetch_github_access_token, client_kwargs={'scope':''})
    oauth2_clients.register('twitter', save_request_token= store_twitter_req_token, fetch_request_token= fetch_twitter_req_token)

def fetch_github_access_token():
    raise NotImplementedError()
#     return session['access_token_github']

def store_twitter_req_token(token):
    session['request_token_twitter'] = token

def fetch_twitter_req_token():
    return session.pop('request_token_twitter')
