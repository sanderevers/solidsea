# generate using: python -c 'import os; print(os.urandom(16))'
# SECRET_KEY = ''

# (from https://gist.github.com/ygotthilf/baa58da5c3dd1f69fae9 )
# in your instance folder, run the following commands (don't add a passphrase):
#
# ssh-keygen -t rsa -b 4096 -f jwtRS256.key
# openssl rsa -in jwtRS256.key -pubout -outform PEM -out jwtRS256.key.pub
#
# and uncomment these options:
#
# IDP_JWT_PRIV_KEY_PATH = 'jwtRS256.key'
# IDP_JWT_PUB_KEY_PATH = 'jwtRS256.key.pub'

OAUTH2_JWT_ENABLED = True,
OAUTH2_JWT_ISS = 'http://localhost:5000'
OAUTH2_JWT_ALG = 'RS256'


# GITHUB_CLIENT_ID = ''
# GITHUB_CLIENT_SECRET = ''

GITHUB_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
GITHUB_ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'
GITHUB_API_BASE_URL = 'https://api.github.com/'


# TWITTER_CLIENT_ID = ''
# TWITTER_CLIENT_SECRET = ''

TWITTER_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
TWITTER_AUTHORIZE_URL = 'https://api.twitter.com/oauth/authorize'
TWITTER_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'


# GOOGLE_CLIENT_ID = ''
# GOOGLE_CLIENT_SECRET = ''

GOOGLE_DISCOVERY_URL = 'https://accounts.google.com/.well-known/openid-configuration'


# MY_CLIENT_ID = ''
# MY_CLIENT_SECRET = ''
# MY_CLIENT_REDIRECT_URI = ''