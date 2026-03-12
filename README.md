# HTTP Metadata Inventory Service

A REST API that collects and stores HTTP metadata (headers, cookies, page source) for any given URL.

Built with Python 3.11, FastAPI, MongoDB, and Docker Compose.

## Quick Start

Make sure Docker Desktop is running, then:

```bash
docker compose up --build
```

API is live at http://localhost:8000

Swagger docs at http://localhost:8000/docs

To stop:

```bash
docker compose down
```

## Run Tests

```bash
pip install -r requirements.txt
pytest -v
```

## API Endpoints

### POST /api/v1/metadata/

Fetch a URL and store its metadata.

```bash
curl -X POST http://localhost:8000/api/v1/metadata/ -H "Content-Type: application/json" -d "{\"url\": \"https://example.com\"}"
```

- `201` -- metadata collected and stored
- `409` -- URL already exists
- `422` -- invalid URL
- `502` -- URL unreachable
- `504` -- URL timed out

### GET /api/v1/metadata/?url=...

Retrieve stored metadata for a URL.

```bash
curl "http://localhost:8000/api/v1/metadata/?url=https://example.com"
```

- `200` -- metadata found, full record returned
- `202` -- not yet collected, background task started (retry shortly)
- `422` -- invalid URL
