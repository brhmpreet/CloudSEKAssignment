import respx
import httpx
import asyncio


@respx.mock
async def test_get_existing_url_returns_200(async_client):
    url = "https://example.com/"
    respx.get(url).mock(return_value=httpx.Response(
        200,
        text="<html><body>Hello</body></html>",
        headers={"Content-Type": "text/html"},
    ))

    await async_client.post("/api/v1/metadata/", json={"url": url})

    response = await async_client.get("/api/v1/metadata/", params={"url": url})

    assert response.status_code == 200
    body = response.json()
    assert body["url"] == url
    assert body["status"] == "collected"


async def test_get_missing_url_returns_202(async_client):
    url = "https://never-seen-before.com/"

    response = await async_client.get("/api/v1/metadata/", params={"url": url})

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "pending"
    assert "message" in body


@respx.mock
async def test_get_after_background_completes(async_client):
    url = "https://background-test.com/"
    respx.get(url).mock(return_value=httpx.Response(200, text="<html>bg</html>"))

    # First GET: triggers background collection, returns 202
    first = await async_client.get("/api/v1/metadata/", params={"url": url})

    assert first.status_code == 202

    await asyncio.sleep(0.5)

    second = await async_client.get("/api/v1/metadata/", params={"url": url})
    assert second.status_code == 200
    assert second.json()["status"] == "collected"