import os
from flask import Flask
from .oauth2_server import config_oauth
from .federation import federation
from .routes import bp
from .encryption import encryption
from .myclients import init_my_clients


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)

    # load default configuration
    app.config.from_object('website.settings')

    # load environment configuration
    if 'WEBSITE_CONF' in os.environ:
        app.config.from_envvar('WEBSITE_CONF')

    # load app sepcified configuration
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py') or config.endswith('.cfg'):
            app.config.from_pyfile(config)

    setup_app(app)
    return app


def setup_app(app):
    config_oauth(app)
    federation.init_app(app)
    encryption.init_app(app)
    init_my_clients(app)
    app.register_blueprint(bp, url_prefix='')
