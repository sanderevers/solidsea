import os
from flask import Flask
from .oidc_server import oidc_server_init_app
from .federation import federation
from .routes import bp
from .encryption import encryption
from .myclients import init_my_clients


def create_app():
    instance_path = os.environ.get('INSTANCE_PATH')
    app = Flask('solidsea', instance_path=instance_path, instance_relative_config=True)

    # default config
    app.config.from_object('solidsea.default_config')

    # instance config
    app.config.from_pyfile('config.py')

    setup_app(app)
    return app


def setup_app(app):
    federation.init_app(app)
    encryption.init_app(app)
    oidc_server_init_app(app)
    init_my_clients(app)
    app.register_blueprint(bp, url_prefix='')
