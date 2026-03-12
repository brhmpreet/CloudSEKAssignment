import pytest
import respx
import httpx

from app.services.http_client import fetch_url
from app.exceptions import URLFetchError, URLTimeoutError

FAKE_URL = "https://example.com/"

@respx.mock
async def test_fetch_returns_headers_and_page_source():
    url = FAKE_URL

    respx.get(url).mock(return_value=httpx.Response(
        200,
        text="<html><body>Hello</body></html>",
        headers={"Content-Type": "text/html", "Server": "TestServer"},
    ))

    result = await fetch_url(url)

    assert result["status_code"] == 200
    assert result["page_source"] == "<html><body>Hello</body></html>"
    assert result["headers"]["content-type"] == "text/html"
    assert result["headers"]["server"] == "TestServer"


@respx.mock
async def test_fetch_raises_timeout_error():
    url = FAKE_URL

    respx.get(url).mock(side_effect=httpx.ReadTimeout("timed out"))

    with pytest.raises(URLTimeoutError):
        await fetch_url(url)


@respx.mock
async def test_fetch_raises_error_on_connection_failure():
    url = FAKE_URL

    respx.get(url).mock(side_effect=httpx.ConnectError("connection refused"))

    with pytest.raises(URLFetchError):
        await fetch_url(url)