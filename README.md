# 1337ft

A small attempt at trying to replicate [12ft.io](https://12ft.io/)

Since websites want crawlers to index their data, showing crawlers a paywall is counter-intuitive. This project exploits that by cycling through several bypass strategies:

1. **Bot UA + Referer spoofing** — Rotate through Googlebot, Bingbot, Facebookbot, Twitterbot, and LinkedInBot user-agents with a matching search-engine referer header.
2. **Google Cache proxy** — Fetch the cached version via `webcache.googleusercontent.com`.
3. **Wayback Machine fallback** — Retrieve the latest snapshot from `web.archive.org`.

Strategies are tried in order; the first successful response is returned.

## Usage

The application runs at `http://127.0.0.1:8008/`

**Install dependencies**

```sh
uv sync
```

Or with plain pip using the exported lockfile:

```sh
pip install -r requirements.txt
```

**Run the flask application**

```sh
uv run python -m 1337ft
```

Or via the installed script:

```sh
uv run 1337ft
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

## Development

```sh
# Install all deps including dev tools
uv sync

# Run tests
uv run pytest tests/ -v

# Format & lint
uv run ruff format .
uv run ruff check .
uv run mypy 1337ft/
```

## Build package

```sh
uv build
```

## ToDo

- [ ] Fix rate limiting issue
- [ ] Bypass Cloudflare
