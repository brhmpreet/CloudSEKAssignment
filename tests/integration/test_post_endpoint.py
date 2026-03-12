import respx
import httpx

FAKE_URL = "https://example.com/"

@respx.mock
async def test_post_valid_url_returns_201(async_client):
    url = FAKE_URL

    respx.get(url).mock(return_value=httpx.Response(
        200,
        text="<html><body>Example</body></html>",
        headers={"Content-Type": "text/html"},
    ))

    response = await async_client.post("/api/v1/metadata/", json={"url": url})

    assert response.status_code == 201
    body = response.json()
    assert body["url"] == url
    assert body["status"] == "collected"
    assert "<html>" in body["page_source"]


@respx.mock
async def test_post_duplicate_url_returns_409(async_client):
    url = FAKE_URL
    respx.get(url).mock(return_value=httpx.Response(200, text="<html></html>"))

    # First time: should work
    first = await async_client.post("/api/v1/metadata/", json={"url": url})
    assert first.status_code == 201

    # Second time: should be rejected as duplicate
    second = await async_client.post("/api/v1/metadata/", json={"url": url})
    assert second.status_code == 409


async def test_post_invalid_url_returns_422(async_client):
    response = await async_client.post("/api/v1/metadata/", json={"url": "not-a-url"})
    assert response.status_code == 422
    
