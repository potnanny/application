import os
import logging
from quart import Quart, redirect, url_for
from quart_wtf.csrf import CSRFProtect
from quart_auth import QuartAuth, Unauthorized
from potnanny.models.user import SessionUser


# globals #
BASEDIR = os.path.abspath(os.path.dirname(__file__))
auth_manager = QuartAuth()
auth_manager.user_class = SessionUser
logger = logging.getLogger(__name__)


def init_application(config):
    logger.debug(f"App basedir: {BASEDIR}")
    app = Quart(__name__, root_path=BASEDIR)
    configure_app(app)
    csrf = CSRFProtect(app)
    auth_manager.init_app(app)
    load_blueprints(app)
    load_views()
    load_handlers(app)
    return app


def configure_app(app):
    app.config['SECRET_KEY'] = os.getenv('POTNANNY_SECRET')
    app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('POTNANNY_SECRET')
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['EXPLAIN_TEMPLATE_LOADING'] = False

    ## development ##
    app.config['QUART_AUTH_COOKIE_SECURE'] = False


def load_blueprints(app):
    """
    Load flask blueprints from web apps

    args:
        - Flask app instance
    """

    from potnanny.api.environments.views import bp as environments
    from potnanny.api.rooms.views import bp as rooms
    from potnanny.api.devices.views import bp as devices
    from potnanny.api.keychains.views import bp as keychains
    from potnanny.api.graphs.views import bp as graphs
    from potnanny.api.utils.views import bp as utils
    from potnanny.api.settings.views import bp as settings
    from potnanny.api.controls.views import bp as controls
    from potnanny.api.features.views import bp as features
    from potnanny.api.auth.views import bp as auth
    from potnanny.api.about.views import bp as about

    app.register_blueprint(environments)
    app.register_blueprint(rooms)
    app.register_blueprint(devices)
    app.register_blueprint(keychains)
    app.register_blueprint(graphs)
    app.register_blueprint(utils)
    app.register_blueprint(settings)
    app.register_blueprint(controls)
    app.register_blueprint(features)
    app.register_blueprint(auth)
    app.register_blueprint(about)


def load_views():
    """
    Load views from any of the web apps
    """

    from potnanny.api.environments import views
    from potnanny.api.rooms import views
    from potnanny.api.devices import views
    from potnanny.api.keychains import views
    from potnanny.api.graphs import views
    from potnanny.api.utils import views
    from potnanny.api.settings import views
    from potnanny.api.controls import views
    from potnanny.api.features import views
    from potnanny.api.auth import views
    from potnanny.api.about import views


def load_handlers(app):
    @app.errorhandler(Unauthorized)
    async def redirect_to_login(Exception):
        return redirect(url_for("auth.login"))
