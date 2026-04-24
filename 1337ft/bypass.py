import random
import re
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

# ---------------------------------------------------------------------------
# Medium / freedium
# ---------------------------------------------------------------------------

# Matches medium.com and any subdomain (e.g. username.medium.com)
_MEDIUM_HOSTNAME_RE = re.compile(r"^(?:[a-z0-9-]+\.)?medium\.com$", re.IGNORECASE)

# Well-known publications that are hosted on Medium's infrastructure
_MEDIUM_PUBLICATION_HOSTNAMES: frozenset[str] = frozenset(
    [
        "towardsdatascience.com",
        "betterprogramming.pub",
        "levelup.gitconnected.com",
        "javascript.plainenglish.io",
        "python.plainenglish.io",
        "itnext.io",
        "uxdesign.cc",
        "entrepreneurshandbook.co",
        "codeburst.io",
        "proandroiddev.com",
        "infosecwriteups.com",
    ]
)

# Primary mirror first, fallback second (mirrors the Android app logic)
_FREEDIUM_DOMAINS = ("freedium.cfd", "freedium-mirror.cfd")


def _is_medium_url(url: str) -> bool:
    """Return True if *url* is hosted on medium.com or a known Medium publication."""
    hostname = urllib.parse.urlparse(url).hostname or ""
    return (
        bool(_MEDIUM_HOSTNAME_RE.match(hostname))
        or hostname in _MEDIUM_PUBLICATION_HOSTNAMES
    )


def _freedium_fetch(url: str) -> str:
    """Fetch a Medium article via freedium.cfd, falling back to freedium-mirror.cfd.

    The technique mirrors `medium-unlocker <https://github.com/inulute/medium-unlocker>`_:
    prepend ``https://freedium.cfd/`` to the full original URL so that
    freedium's proxy serves the unpaywalled version.
    """
    last_exc: Exception | None = None
    for domain in _FREEDIUM_DOMAINS:
        proxy_url = f"https://{domain}/{url}"
        try:
            response = requests.get(
                proxy_url,
                headers={"User-Agent": _BOT_USER_AGENTS[0]},
                timeout=_TIMEOUT,
                allow_redirects=True,
            )
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            content = response.text
            if content and content.strip():
                return content
        except requests.RequestException as exc:
            last_exc = exc
    msg = f"All freedium mirrors failed for {url!r}"
    raise requests.RequestException(msg) from last_exc


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
    """Try multiple strategies to bypass a paywall, in order.

    **Medium articles** (``medium.com``, subdomains, and known publications):

    1. Freedium proxy (``freedium.cfd`` → ``freedium-mirror.cfd`` fallback).
    2. Direct fetch with a rotating bot User-Agent and referer spoofing.
    3. Google Cache proxy (``webcache.googleusercontent.com``).
    4. Wayback Machine snapshot (``web.archive.org``).

    **All other URLs**:

    1. Direct fetch with a rotating bot User-Agent and referer spoofing.
    2. Google Cache proxy (``webcache.googleusercontent.com``).
    3. Wayback Machine snapshot (``web.archive.org``).

    Returns the HTML content of the first strategy that succeeds.
    Raises :class:`requests.RequestException` if every strategy fails.
    """
    if _is_medium_url(url):
        strategies = [
            _freedium_fetch,
            _direct_fetch,
            _google_cache_fetch,
            _archive_fetch,
        ]
    else:
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
