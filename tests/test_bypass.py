from importlib import import_module
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import requests


bypass = import_module("1337ft.bypass")

_BOT_NAMES = (
    "Googlebot",
    "bingbot",
    "facebookexternalhit",
    "Twitterbot",
    "LinkedInBot",
)


def _make_mock_response(text: str, encoding: str = "utf-8") -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.text = text
    mock_resp.apparent_encoding = encoding
    return mock_resp


# ---------------------------------------------------------------------------
# Direct strategy
# ---------------------------------------------------------------------------


def test_bypass_uses_bot_user_agent():
    """The direct strategy must use a known crawler User-Agent."""
    with patch("requests.get") as mock_get:
        mock_get.return_value = _make_mock_response("<html>ok</html>")
        bypass.bypass_paywall("https://example.com/article")

    _, kwargs = mock_get.call_args
    ua = kwargs["headers"]["User-Agent"]
    assert any(name in ua for name in _BOT_NAMES)


def test_bypass_sets_referer():
    """Direct fetch must include a Referer header."""
    with patch("requests.get") as mock_get:
        mock_get.return_value = _make_mock_response("<html>ok</html>")
        bypass.bypass_paywall("https://example.com/article")

    _, kwargs = mock_get.call_args
    assert "Referer" in kwargs["headers"]


def test_bypass_sets_timeout():
    with patch("requests.get") as mock_get:
        mock_get.return_value = _make_mock_response("<html>ok</html>")
        bypass.bypass_paywall("https://example.com/article")

    _, kwargs = mock_get.call_args
    assert kwargs.get("timeout") is not None


def test_bypass_returns_response_text():
    expected = "<html><body>Full article</body></html>"
    with patch("requests.get") as mock_get:
        mock_get.return_value = _make_mock_response(expected)
        result = bypass.bypass_paywall("https://example.com/article")

    assert result == expected


# ---------------------------------------------------------------------------
# Fallback chain
# ---------------------------------------------------------------------------


def test_bypass_falls_back_to_google_cache():
    """When the direct fetch fails, the Google Cache strategy must be tried."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = [
            requests.ConnectionError("blocked"),  # direct fails
            _make_mock_response("<html>cached</html>"),  # cache succeeds
        ]
        result = bypass.bypass_paywall("https://example.com/article")

    assert result == "<html>cached</html>"
    assert mock_get.call_count == 2
    cache_url = mock_get.call_args_list[1][0][0]
    assert "webcache.googleusercontent.com" in cache_url


def test_bypass_falls_back_to_archive():
    """When direct and cache both fail, Wayback Machine is tried."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = [
            requests.ConnectionError("blocked"),  # direct fails
            requests.ConnectionError("cache unavailable"),  # cache fails
            _make_mock_response("<html>archived</html>"),  # archive succeeds
        ]
        result = bypass.bypass_paywall("https://example.com/article")

    assert result == "<html>archived</html>"
    assert mock_get.call_count == 3
    archive_url = mock_get.call_args_list[2][0][0]
    assert "web.archive.org" in archive_url


def test_bypass_raises_when_all_strategies_fail():
    """Raises RequestException when every strategy fails."""
    with patch("requests.get", side_effect=requests.ConnectionError("blocked")):
        with pytest.raises(requests.RequestException):
            bypass.bypass_paywall("https://example.com/article")
