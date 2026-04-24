import random
import urllib.parse

import requests


_BOT_USER_AGENTS = [
    # Googlebot Desktop
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/125.0.0.0 Safari/537.36",
    # Bingbot
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    # Facebookbot
    "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
    # Twitterbot
    "Twitterbot/1.0",
    # LinkedInBot
    "LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)",
]

_REFERERS = [
    "https://www.google.com/",
    "https://www.facebook.com/",
    "https://t.co/",
    "https://www.linkedin.com/",
]

_TIMEOUT = 10


def _direct_fetch(url: str) -> str:
    """Fetch with a randomly chosen bot UA and a spoofed search-engine referer."""
    ua = random.choice(_BOT_USER_AGENTS)  # noqa: S311
    referer = random.choice(_REFERERS)  # noqa: S311
    response = requests.get(
        url,
        headers={"User-Agent": ua, "Referer": referer},
        timeout=_TIMEOUT,
        allow_redirects=True,
    )
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response.text


def _google_cache_fetch(url: str) -> str:
    """Fetch the page via Google's cache proxy."""
    cache_url = (
        "https://webcache.googleusercontent.com/search?q=cache:"
        + urllib.parse.quote(url, safe="")
    )
    response = requests.get(
        cache_url,
        headers={"User-Agent": _BOT_USER_AGENTS[0]},
        timeout=_TIMEOUT,
        allow_redirects=True,
    )
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response.text


def _archive_fetch(url: str) -> str:
    """Fetch the most recent Wayback Machine snapshot of the page."""
    archive_url = "https://web.archive.org/web/" + urllib.parse.quote(url, safe=":/")
    response = requests.get(
        archive_url,
        headers={"User-Agent": _BOT_USER_AGENTS[0]},
        timeout=_TIMEOUT,
        allow_redirects=True,
    )
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response.text


def bypass_paywall(url: str) -> str:
    """Try multiple strategies to bypass a paywall, in order:

    1. Direct fetch with a rotating bot User-Agent and referer spoofing.
    2. Google Cache proxy (``webcache.googleusercontent.com``).
    3. Wayback Machine snapshot (``web.archive.org``).

    Returns the HTML content of the first strategy that succeeds.
    Raises :class:`requests.RequestException` if every strategy fails.
    """
    strategies = [_direct_fetch, _google_cache_fetch, _archive_fetch]
    last_exc: Exception | None = None
    for fetch_fn in strategies:
        try:
            content = fetch_fn(url)
            if content and content.strip():
                return content
        except requests.RequestException as exc:
            last_exc = exc
    msg = f"All bypass strategies failed for {url!r}"
    raise requests.RequestException(msg) from last_exc
