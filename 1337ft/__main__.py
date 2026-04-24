import os

from . import create_app


def main():
    app = create_app()
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, port=8008)


if __name__ == "__main__":
    main()
