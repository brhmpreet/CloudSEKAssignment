# HTTP Metadata Inventory Service

A REST API that collects and stores HTTP metadata (headers, cookies, page source) for any given URL.

Built with Python 3.11, FastAPI, MongoDB, and Docker Compose.

## Environment Setup

Copy the example env file to create your local `.env`:

```bash
cp .env.example .env
```

On Windows (PowerShell):

```powershell
Copy-Item .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `MONGO_URI` | MongoDB connection string (uses the Docker service name) | `mongodb://mongodb:27017` |
| `MONGO_DB_NAME` | Database name | `metadata_inventory` |
| `HTTP_TIMEOUT` | Timeout in seconds for outbound HTTP requests | `10` |
| `APP_HOST` | Host the API binds to | `0.0.0.0` |
| `APP_PORT` | Port the API listens on | `8000` |

The defaults work out of the box with `docker compose`, so most users just need to copy the file without changing anything.

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

## Project Structure

```
app/
├── main.py                          # FastAPI app, lifespan hooks, exception handlers
├── config.py                        # Settings loaded from environment / .env
├── exceptions.py                    # Custom error classes
├── api/routes/metadata.py           # Controller — POST and GET endpoint definitions
├── services/
│   ├── metadata_service.py          # Service — business logic, background collection
│   └── http_client.py               # Service — outbound HTTP requests via httpx
├── schemas/metadata.py              # DTOs — Pydantic request/response models
├── repositories/metadata_repository.py  # Repository — MongoDB queries (find, insert, update)
└── database/mongodb.py              # Database — Motor client connection lifecycle
tests/
├── conftest.py                      # Shared fixtures (async test client, mock DB)
├── unit/
│   ├── test_http_client.py          # Unit tests for the HTTP client
│   └── test_metadata_service.py     # Unit tests for the metadata service
└── integration/
    ├── test_post_endpoint.py        # Integration tests for POST /api/v1/metadata/
    └── test_get_endpoint.py         # Integration tests for GET  /api/v1/metadata/
```

| Layer | Path | Responsibility |
|---|---|---|
| Controller | `app/api/routes/` | FastAPI router defining POST/GET endpoints |
| Service | `app/services/` | Business logic, background tasks, outbound HTTP calls |
| DTO / Schema | `app/schemas/` | Pydantic request and response models |
| Repository | `app/repositories/` | MongoDB data access (find, insert, update) |
| Database | `app/database/` | Motor client connection lifecycle and DB handle |
| Tests | `tests/` | Unit and integration tests with mocked MongoDB |

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
