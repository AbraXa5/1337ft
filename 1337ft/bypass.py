import requests


def bypass_paywall(url: str):
    # https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers#common-crawlers
    # https://explore.whatismybrowser.com/useragents/explore/software_name/googlebot/
    googlebotDesktop_headers = {
        "User-Agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/113.0.5672.127 Safari/537.36"
    }

    response = requests.get(url, headers=googlebotDesktop_headers, timeout=5)
    # https://stackoverflow.com/a/52615216
    response.encoding = response.apparent_encoding
    return response.text
