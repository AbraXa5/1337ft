import importlib
from unittest.mock import patch

import requests as req


_views = importlib.import_module("1337ft.views")


def test_get_returns_form(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Bypass Paywall" in response.data


def test_post_no_url_returns_form(client):
    response = client.post("/", data={"url": ""})
    assert response.status_code == 200
    assert b"Bypass Paywall" in response.data


def test_post_invalid_scheme_blocked(client):
    response = client.post("/", data={"url": "ftp://example.com/article"})
    assert response.status_code == 400
    assert b"Only http and https" in response.data


def test_post_file_scheme_blocked(client):
    response = client.post("/", data={"url": "file:///etc/passwd"})
    assert response.status_code == 400
    assert b"Only http and https" in response.data


def test_post_ssrf_loopback_blocked(client):
    response = client.post("/", data={"url": "http://127.0.0.1/"})
    assert response.status_code == 400
    assert b"private or reserved" in response.data


def test_post_ssrf_private_range_blocked(client):
    response = client.post("/", data={"url": "http://192.168.1.1/"})
    assert response.status_code == 400
    assert b"private or reserved" in response.data


def test_post_ssrf_link_local_blocked(client):
    response = client.post(
        "/", data={"url": "http://169.254.169.254/latest/meta-data/"}
    )
    assert response.status_code == 400
    assert b"private or reserved" in response.data


def test_post_valid_url_returns_content(client):
    with (
        patch.object(_views, "_validate_url"),
        patch.object(_views, "bypass_paywall") as mock_bypass,
    ):
        mock_bypass.return_value = "<html><body><p>Article content</p></body></html>"
        response = client.post("/", data={"url": "https://example.com/article"})
    assert response.status_code == 200
    assert b"Article content" in response.data
    assert response.content_type.startswith("text/html")


def test_post_valid_url_content_not_jinja_rendered(client):
    """Ensure fetched content with Jinja2 syntax is NOT executed server-side."""
    with (
        patch.object(_views, "_validate_url"),
        patch.object(_views, "bypass_paywall") as mock_bypass,
    ):
        mock_bypass.return_value = "<html><body>{{ 7 * 7 }}</body></html>"
        response = client.post("/", data={"url": "https://example.com/article"})
    assert response.status_code == 200
    # Must be returned as literal text, not evaluated to 49
    assert b"{{ 7 * 7 }}" in response.data
    assert b"49" not in response.data


def test_post_fetch_failure_returns_502(client):
    with (
        patch.object(_views, "_validate_url"),
        patch.object(
            _views, "bypass_paywall", side_effect=req.RequestException("timeout")
        ),
    ):
        response = client.post("/", data={"url": "https://example.com/article"})
    assert response.status_code == 502
    assert b"Failed to fetch" in response.data
    assert b"Failed to fetch" in response.data
