from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import requests


GOOGLEBOT_UA = (
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1;"
    " +http://www.google.com/bot.html) Chrome/113.0.5672.127 Safari/537.36"
)


def _make_mock_response(text: str, encoding: str = "utf-8") -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.text = text
    mock_resp.apparent_encoding = encoding
    return mock_resp


def test_bypass_uses_googlebot_user_agent():
    with patch("requests.get") as mock_get:
        mock_get.return_value = _make_mock_response("<html>ok</html>")
        from importlib import import_module

        bypass = import_module("1337ft.bypass")
        bypass.bypass_paywall("https://example.com/article")

    _, kwargs = mock_get.call_args
    assert "User-Agent" in kwargs["headers"]
    assert "Googlebot" in kwargs["headers"]["User-Agent"]


def test_bypass_sets_timeout():
    with patch("requests.get") as mock_get:
        mock_get.return_value = _make_mock_response("<html>ok</html>")
        from importlib import import_module

        bypass = import_module("1337ft.bypass")
        bypass.bypass_paywall("https://example.com/article")

    _, kwargs = mock_get.call_args
    assert kwargs.get("timeout") is not None


def test_bypass_returns_response_text():
    expected = "<html><body>Full article</body></html>"
    with patch("requests.get") as mock_get:
        mock_get.return_value = _make_mock_response(expected)
        from importlib import import_module

        bypass = import_module("1337ft.bypass")
        result = bypass.bypass_paywall("https://example.com/article")

    assert result == expected


def test_bypass_propagates_request_exception():
    with patch("requests.get", side_effect=requests.Timeout("timed out")):
        from importlib import import_module

        bypass = import_module("1337ft.bypass")
        with pytest.raises(requests.Timeout):
            bypass.bypass_paywall("https://example.com/article")
