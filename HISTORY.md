# History

## 0.2.0 (2026-04-24)

* Migrated from Poetry to [uv](https://github.com/astral-sh/uv) as package manager (PEP 621 `pyproject.toml`, `uv.lock`).
* Dropped `black` and `isort` in favour of `ruff format` and `ruff`'s built-in isort.
* Updated `.pre-commit-config.yaml` to use `uv run` and removed the isort/black hooks.
* Updated `Dockerfile` to use the official `ghcr.io/astral-sh/uv` base image.
* Enhanced paywall bypass with a multi-strategy fallback chain:
  * Direct fetch with rotating bot User-Agents (Googlebot, Bingbot, Facebookbot, Twitterbot, LinkedInBot) and spoofed search-engine referer headers.
  * Google Cache proxy (`webcache.googleusercontent.com`).
  * Wayback Machine fallback (`web.archive.org`).
* Added `bandit` to dev dependencies and wired into `make check-safety`.

## 0.1.0 (2023-05-23)

* First release on PyPI.
