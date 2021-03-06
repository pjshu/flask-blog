import json

from flask import g

from app.api_limiter import limiter
from app.create_app import create_app
from app.logging_manager import register_logging, register_log_query_and_response_time
from app.myType import FlaskInstance, Response
from .token_manager import jwt


def register_refresh_token(app: FlaskInstance):
    @app.after_request
    def after_all_request(response: Response):
        # 用于刷新token
        if hasattr(g, 'refresh_token'):
            res = json.loads(response.get_data())
            if 'data' not in res:
                res['data'] = {
                    'token': g.refresh_token,
                    'id': g.id
                }
            response.set_data(json.dumps(res))
        return response


def register_blueprint(app: FlaskInstance):
    from app.app_admin.api.blueprint import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)


def register_config(app: FlaskInstance):
    # register_signal()
    register_blueprint(app)
    register_refresh_token(app)
    jwt.init_app(app)
    limiter.init_app(app)
    if app.env == 'production':
        register_logging(app)
        register_log_query_and_response_time(app)


def create_admin_app(env=None):
    app = create_app(
        register_config,
        __name__,
        static_folder='static/',
        static_url_path='',
        env=env
    )
    return app
