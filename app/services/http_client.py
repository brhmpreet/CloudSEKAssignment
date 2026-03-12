import httpx
from app.config import settings
from app.exceptions import URLFetchError, URLTimeoutError


async def fetch_url(url):
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=settings.http_timeout) as client:
            response = await client.get(url)

            return {
                "headers": dict(response.headers),
                "cookies": dict(response.cookies),
                "page_source": response.text,
                "status_code": response.status_code,
            }

    except httpx.TimeoutException:
        raise URLTimeoutError(f"Request timed out for URL: {url}")

    except httpx.RequestError as error:
        raise URLFetchError(f"Failed to fetch URL {url}: {error}")