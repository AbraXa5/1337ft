# 1337ft

A small attempt at trying to replicate [12ft.io](https://12ft.io/)

Since websites want crawlers to index their data, showing crawlers a paywall is counter-intuitive. This is using the same approach by seeting the UserAgent as a [GoogleBot Crawler](https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers#common-crawlers)

## Usage

The application will be hosted at `http://127.0.0.1:8008/`

**Install dependencies**

1. Using poetry (recommended)

```sh
poetry install --no-dev
```

2. Using requirements.txt,

```sh
poetry export -f requirements.txt --without dev --output requirements.txt
pip install -r requirements.txt
```

**Run the flask application**

```sh
python -m 1337ft
```

Using poetry

```sh
poetry run 1337ft
```

**Using Docker**

Build the image

```sh
docker build -t 1337ft .
```

Run the container

```sh
docker run -d --rm -p 8008:8008 --name 1337ft 1337ft
```

## Build package

```sh
poetry build
pipx install dist/*.whl
```

## ToDo

- [ ] Fix rate limiting issue
- [ ] Bypass cloudflare
