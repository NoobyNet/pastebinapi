# Pastebin API Wrapper

A modern FastAPI-based wrapper for the Pastebin API, providing clean, type-safe endpoints for authentication, paste creation, and paste management.

## Features

- **Type-safe API**: Built with Pydantic models for request/response validation
- **Modern Python**: Uses Python 3.14+ with modern syntax (union types, etc.)
- **Dependency Injection**: FastAPI's IoC container for clean architecture
- **Custom Exception Handling**: Domain-specific exceptions with centralized error handling
- **Async Support**: Fully asynchronous using aiohttp
- **Syntax Highlighting**: Support for 200+ programming languages via PasteFormat enum

## Project Structure

```
.
├── config.py                 # Environment-based configuration using Pydantic Settings
├── exceptions.py             # Custom domain exceptions
├── main.py                   # FastAPI application with exception handlers
├── models/                   # Pydantic models
│   ├── api_response.py       # Generic type-safe response wrapper
│   ├── login/                # Authentication models
│   └── paste/                # Paste-related models
├── routers/                  # FastAPI routers
│   ├── auth.py               # Authentication endpoints
│   └── paste.py              # Paste management endpoints
└── services/                 # Business logic layer
    ├── pastebin_service.py   # Pastebin API integration
    └── xml_service.py        # XML parsing utilities
```

## Requirements

- Python 3.14+
- Dependencies managed via `uv`

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PasteBinApi
```

2. Create a `.env` file with your Pastebin credentials:
```bash
PASTEBIN_BASE_URL=https://pastebin.com/api
DEV_API_KEY=your_developer_api_key
USER_NAME=your_username
USER_PASSWORD=your_password
```

3. Install dependencies:
```bash
uv sync
```

## Running the Application

### Local Development

Start the development server:
```bash
uv run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker

Build and run with Docker:

```bash
# Build the Docker image
docker build -t pastebin-api .

# Run the container
docker run -d \
  --name pastebin-api \
  -p 8000:8000 \
  -e PASTEBIN_BASE_URL=https://pastebin.com/api \
  -e DEV_API_KEY=your_dev_api_key \
  -e USER_NAME=your_username \
  -e USER_PASSWORD=your_password \
  pastebin-api

# Or use environment file
docker run -d \
  --name pastebin-api \
  -p 8000:8000 \
  --env-file .env \
  pastebin-api
```

Using Docker Compose (create `docker-compose.yml`):

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PASTEBIN_BASE_URL=${PASTEBIN_BASE_URL}
      - DEV_API_KEY=${DEV_API_KEY}
      - USER_NAME=${USER_NAME}
      - USER_PASSWORD=${USER_PASSWORD}
    restart: unless-stopped
```

Then run:
```bash
docker-compose up -d
```

## API Documentation

Once the server is running, visit:
- **Interactive API docs (Swagger)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Authentication

#### `POST /auth/login`
Authenticate with Pastebin and receive a user session key.

**Request:**
```json
{
  "api_user_name": "your_username",
  "api_user_password": "your_password"
}
```

**Response:**
```json
{
  "data": {
    "api_user_key": "session_key_here"
  }
}
```

### Paste Management

#### `POST /paste/create`
Create a new paste on Pastebin.

**Request:**
```json
{
  "api_paste_code": "print('Hello, World!')",
  "api_paste_name": "My Python Script",
  "api_paste_format": "python",
  "api_paste_private": 0,
  "api_paste_expire_date": "10M",
  "api_user_key": "session_key_from_login"
}
```

**Response:**
```json
{
  "data": {
    "paste_url": "https://pastebin.com/abc123"
  }
}
```

#### `POST /paste/list`
List all pastes for an authenticated user.

**Request:**
```json
{
  "api_user_key": "session_key_from_login",
  "api_results_limit": 50
}
```

**Response:**
```json
{
  "data": {
    "pastes": [
      {
        "key": "abc123",
        "date": "2026-03-10T12:00:00",
        "title": "My Python Script",
        "size": 1024,
        "expire_date": 0,
        "private": 0,
        "format_long": "Python",
        "format_short": "python",
        "url": "https://pastebin.com/abc123",
        "hits": 42
      }
    ]
  }
}
```

## Architecture

### Layered Architecture
1. **Routers** - Define API endpoints and handle HTTP concerns
2. **Services** - Contain business logic and external API integration
3. **Models** - Provide type-safe contracts for requests/responses
4. **Configuration** - Centralized environment-based settings

### Dependency Injection
- `Settings` injected into services via `get_settings()`
- `PastebinService` injected into routers via `get_pastebin_service()`

### Exception Handling
- Domain exceptions raised in service layer
- Custom exception handlers in `main.py` translate to HTTP responses
- Consistent error response format across all endpoints

## Configuration

All configuration is managed through environment variables in `.env`:

| Variable | Description |
|----------|-------------|
| `PASTEBIN_BASE_URL` | Base URL for Pastebin API |
| `DEV_API_KEY` | Your Pastebin developer API key |
| `USER_NAME` | Test username (optional) |
| `USER_PASSWORD` | Test password (optional) |

## Development

### Running Tests
```bash
uv run pytest
```

### Code Style
- Use `snake_case` for files and variables
- Use `PascalCase` for class names
- Modern Python syntax: `str | None` instead of `Optional[str]`
- Explicit `default=` in Pydantic Field()

## Testing

HTTP request examples are available in `test_main.http` for manual API testing with tools like VS Code REST Client or JetBrains HTTP Client.

## CI/CD

This project uses GitHub Actions for continuous integration and deployment:

### Test Workflow
- Runs on every push and pull request to `main` and `develop` branches
- Tests against Python 3.14
- Generates test coverage reports
- Uploads coverage to Codecov

### Docker Build & Publish Workflow
- Runs on pushes to `main` branch and on version tags
- Runs tests before building
- Builds multi-platform Docker images (amd64, arm64)
- Publishes to Docker Hub: `noobynet/pastebinapi`
- Automatically tags with:
  - `latest` (main branch)
  - Semantic version tags (from git tags)
  - Branch names
  - Git SHA

### Required GitHub Secrets
To enable Docker publishing, add these secrets to your repository:
- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Your Docker Hub access token

## Docker Hub

Docker images are available at: **[noobynet/pastebinapi](https://hub.docker.com/r/noobynet/pastebinapi)**

Pull the latest image:
```bash
docker pull noobynet/pastebinapi:latest
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
