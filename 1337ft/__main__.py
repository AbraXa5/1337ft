from . import create_app


def main():
    app = create_app()
    app.run(debug=True, port=8008)


if __name__ == "__main__":
    main()
