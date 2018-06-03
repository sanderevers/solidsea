import os
from flask import Flask
from .models import db
from .oauth2 import config_oauth
from .oauth2_client import init_oauth2_clients
from .routes import bp


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
    db.init_app(app)
    config_oauth(app)
    init_oauth2_clients(app)
    app.register_blueprint(bp, url_prefix='')
