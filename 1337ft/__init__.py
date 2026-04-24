from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .views import main


def create_app():
    app = Flask(__name__)
    Limiter(
        get_remote_address,
        app=app,
        default_limits=["10 per minute"],
        storage_uri="memory://",
    )
    app.register_blueprint(main)
    return app
