import importlib

import pytest


_pkg = importlib.import_module("1337ft")
create_app = _pkg.create_app


@pytest.fixture()
def app():
    application = create_app()
    application.config["TESTING"] = True
    application.config["RATELIMIT_ENABLED"] = False
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()
