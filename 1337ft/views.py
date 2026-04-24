import ipaddress
import socket
from urllib.parse import urlparse

import requests
from flask import Blueprint
from flask import Response
from flask import render_template
from flask import request

from .bypass import bypass_paywall


main = Blueprint("main", __name__)

_BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("255.255.255.255/32"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def _validate_url(url: str) -> None:
    """Validate a URL, blocking SSRF targets (private/reserved addresses)."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        msg = "Only http and https URLs are allowed."
        raise ValueError(msg)
    if not parsed.hostname:
        msg = "URL must have a valid hostname."
        raise ValueError(msg)
    try:
        addr_infos = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror:
        msg = "Unable to resolve hostname."
        raise ValueError(msg)
    _private_msg = "Requests to private or reserved addresses are not allowed."
    for _family, _type, _proto, _canonname, sockaddr in addr_infos:
        ip = ipaddress.ip_address(sockaddr[0])
        if ip.is_loopback or ip.is_link_local or ip.is_multicast:
            raise ValueError(_private_msg)
        for network in _BLOCKED_NETWORKS:
            if ip in network:
                raise ValueError(_private_msg)


@main.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if url:
            try:
                _validate_url(url)
                content = bypass_paywall(url)
                return Response(content, content_type="text/html; charset=utf-8")
            except ValueError as exc:
                return render_template("index.html", error=str(exc)), 400
            except requests.RequestException:
                return (
                    render_template(
                        "index.html", error="Failed to fetch the requested URL."
                    ),
                    502,
                )

    return render_template("index.html")
