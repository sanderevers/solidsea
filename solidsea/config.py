# This is the default configuration for solidsea.
# To make your instance work, you have to add some configuration of your own.
#
# First, create an 'instance' folder: http://flask.pocoo.org/docs/1.0/config/#instance-folders
# (you can provide a custom location using the env var INSTANCE_PATH )
# Then copy this file there and uncomment the following settings.


# (1) generate a session encryption secret using: python -c 'import os; print(os.urandom(16))'
# uncomment the following line and paste it there.
# SECRET_KEY = ''


# (2) in your instance folder, run the following commands (don't add a passphrase):
#
# ssh-keygen -t rsa -b 4096 -f jwtRS256.key
# openssl rsa -in jwtRS256.key -pubout -outform PEM -out jwtRS256.key.pub

IDP_JWT_PRIV_KEY_PATH = 'jwtRS256.key'
IDP_JWT_PUB_KEY_PATH = 'jwtRS256.key.pub'


# (3) where are you running this instance?
OAUTH2_JWT_ISS = 'http://localhost:5000'


# (4) decide to which providers you want to federate your authentication.
# At these providers, obtain client_id/secret credentials for your application and fill them in below.
# As a redirect URI, use <instance_URL_root>/federate/<client_name>/callback

FEDERATION = ['github','twitter','google']

# GITHUB_CLIENT_ID = ''
# GITHUB_CLIENT_SECRET = ''

# TWITTER_CLIENT_ID = ''
# TWITTER_CLIENT_SECRET = ''

# GOOGLE_CLIENT_ID = ''
# GOOGLE_CLIENT_SECRET = ''

# You can also add other federation clients. For these, also provide
# <client_name>_AUTHORIZE_URL
# <client_name>_ACCESS_TOKEN_URL


# (5) Configure to which clients you provide OIDC.
#
# For a client with authorization_code grant, make up a client_id + secret.
# authorize endpoint is: <instance_URL_root>/authorize
# token endpoint is: <instance_URL_root>/token
#
# For a client with implicit grant, make up a client_id.
# authorize endpoint is: <instance_URL_root>/authorize
#
# The endpoints are also listed at:
# <instance_URL_root>/.well-known/openid-configuration

# MY_CLIENTS = [
#     {
#         'client_id': '',
#         'client_secret': '', # only for authorization code grant
#         'grant_type': 'authorization_code', # 'implicit'
#         'redirect_uri': '',
#     },
# ]


# You probably don't need to alter the settings below.
# You can delete them from your instance config.py because the default config is also always loaded.

OAUTH2_JWT_ENABLED = True,
OAUTH2_JWT_ALG = 'RS256'

GITHUB_CLIENT_MODULE = '.github'
GITHUB_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
GITHUB_ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'
GITHUB_API_BASE_URL = 'https://api.github.com/'

TWITTER_CLIENT_MODULE = '.twitter'
TWITTER_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
TWITTER_AUTHORIZE_URL = 'https://api.twitter.com/oauth/authorize'
TWITTER_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'

GOOGLE_CLIENT_MODULE = '.google'
GOOGLE_DISCOVERY_URL = 'https://accounts.google.com/.well-known/openid-configuration'

# (RSA keygen taken from https://gist.github.com/ygotthilf/baa58da5c3dd1f69fae9 )
