"""
# FastAPI Best Practices Enhancement Guide

This document outlines the enhancements applied to your FastAPI project based on 
the best practices from https://github.com/zhanymkanov/fastapi-best-practices.

## Applied Enhancements

### 1. ✅ Domain-Based Project Structure

**What Changed:**
- Reorganized from a flat `app/` structure to domain-specific modules
- Each domain follows the Netflix Dispatch pattern with standardized organization

**New Structure:**
```
app/
├── main.py              # Application factory and router setup
├── config.py            # Global configuration
├── schemas.py           # Custom BaseModel with standardized datetime handling
├── exceptions.py        # Global exception hierarchy
├── dependencies.py      # Shared dependencies (pagination, validation)
├── logger.py            # Logging setup
├── observability.py     # Tracing and profiling setup
│
├── health/              # Health check module
│   ├── __init__.py
│   ├── router.py        # Endpoint definitions
│   ├── schemas.py       # Pydantic models (HealthCheckResponse)
│   ├── service.py       # Business logic (get_health_status)
│   ├── dependencies.py  # Dependencies (valid_health_check)
│   ├── config.py        # Module-specific config (HealthConfig)
│   ├── constants.py     # Module enums and error codes
│   ├── exceptions.py    # Module-specific exceptions
│   └── utils.py         # Utility functions
│
└── observability_endpoints/  # Observability test endpoints
    ├── __init__.py
    ├── router.py        # /observability/* endpoints
    ├── schemas.py       # Response models
    ├── service.py       # Computation logic
    └── config.py        # Module configuration
```

**Benefits:**
- Scalable for larger applications with many domains
- Clear separation of concerns within each domain
- Easy to locate and modify domain-specific code
- Supports team scaling (each team manages their domain)

**Best Practice Reference:** [Project Structure](https://github.com/zhanymkanov/fastapi-best-practices#project-structure)

---

### 2. ✅ Custom Pydantic BaseModel

**What Changed:**
- Created `app/schemas.py` with `CustomModel` base class
- Standardized datetime serialization with UTC timezone handling

**Code Example:**
```python
from app.schemas import CustomModel

class HealthCheckResponse(CustomModel):
    status: HealthStatus
    timestamp: str
    checks: dict[str, Any]
    # Automatically handles datetime encoding to ISO format
```

**Key Features:**
- All datetime fields serialize to ISO 8601 format with explicit timezone
- `serializable_dict()` method returns JSON-safe dictionaries
- `populate_by_name=True` allows both snake_case and camelCase input

**Best Practice Reference:** [Custom Base Model](https://github.com/zhanymkanov/fastapi-best-practices#custom-base-model)

---

### 3. ✅ Dependency Injection & Caching

**What Changed:**
- Created `app/dependencies.py` with reusable dependency patterns
- Implemented `PaginationParams` class for pagination

**Code Example:**
```python
# In dependencies.py
class PaginationParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
    ):
        self.skip = skip
        self.limit = limit

# In your router
@router.get("/items")
async def list_items(
    pagination: dict = Depends(get_pagination_params)
):
    # pagination is cached within this request scope
    items = await get_items(skip=pagination["skip"], limit=pagination["limit"])
    return items
```

**Key Features:**
- Dependencies are cached per-request by FastAPI
- Can chain dependencies (B depends on A, C depends on B)
- Async dependencies preferred (avoid threadpool overhead)
- Reusable across multiple endpoints

**Health Check Example:**
```python
# In health/dependencies.py
async def valid_health_check() -> dict:
    health = await get_health_status()
    return health

# In health/router.py
@router.get("/health")
async def get_health(health_data: dict = Depends(valid_health_check)):
    return HealthCheckResponse(**health_data)
```

**Best Practice Reference:** [Dependencies](https://github.com/zhanymkanov/fastapi-best-practices#dependencies)

---

### 4. ✅ Proper Response Models & HTTP Status Codes

**What Changed:**
- All endpoints now include `response_model`, `status_code`, `description`
- Created response model enums (HealthStatus, ComputationLevel)

**Code Example:**
```python
from fastapi import status
from .schemas import HealthCheckResponse

@router.get(
    "/health",
    response_model=HealthCheckResponse,          # ← Response validation
    status_code=status.HTTP_200_OK,             # ← Explicit status code
    description="Get application health status", # ← Auto docs
    summary="Health Check",
)
async def get_health():
    return HealthCheckResponse(...)
```

**Benefits:**
- FastAPI auto-generates OpenAPI docs from these attributes
- Response data is validated before sending to client
- Clear and discoverable API contracts
- Consistent documentation for all endpoints

**Best Practice Reference:** [Docs](https://github.com/zhanymkanov/fastapi-best-practices#docs)

---

### 5. ✅ Global Exception Handling

**What Changed:**
- Created `app/exceptions.py` with exception hierarchy
- Base `APIException` class for consistent error responses

**Exception Hierarchy:**
```
APIException (HTTPException wrapper)
├── ValidationError           (422)
├── NotFoundError             (404)
├── UnauthorizedError         (401)
├── ForbiddenError            (403)
├── ConflictError             (409)
└── InternalServerError       (500)
```

**Usage Example:**
```python
from app.exceptions import NotFoundError

if not user:
    raise NotFoundError(detail=f"User {user_id} not found")
```

**Best Practice Reference:** [Custom Exceptions](https://github.com/zhanymkanov/fastapi-best-practices#valueErrors-might-become-pydantic-validationerror)

---

### 6. ✅ Decoupled Module Configuration

**What Changed:**
- Each module has its own `config.py` with BaseSettings
- Global `app/config.py` for shared settings

**Example Module Config:**
```python
# app/health/config.py
from pydantic_settings import BaseSettings

class HealthConfig(BaseSettings):
    HEALTH_CHECK_TIMEOUT: int = 5  # seconds

health_settings = HealthConfig()
```

**Usage in module:**
```python
# app/health/router.py
from .config import health_settings

if response_time > health_settings.HEALTH_CHECK_TIMEOUT:
    raise HealthCheckFailed()
```

**Benefits:**
- Separate concerns: global vs module-specific config
- Easy to override per environment
- Cleaner, more maintainable config management
- Supports independent module deployment

**Best Practice Reference:** [Decouple Pydantic BaseSettings](https://github.com/zhanymkanov/fastapi-best-practices#decouple-pydantic-basesettings)

---

### 7. ✅ Async Test Client & Integration Tests

**What Changed:**
- Created `tests/` directory with async test fixtures
- Using `httpx.AsyncClient` from day 0 (prevents event loop issues)

**Test Setup (`tests/conftest.py`):**
```python
import pytest
from httpx import AsyncClient

@pytest.fixture
async def async_client():
    """
    Async test client for integration tests.
    Fixes event loop issues that occur with TestClient.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

**Usage Example (`tests/health/test_router.py`):**
```python
@pytest.mark.asyncio
async def test_get_health_success(async_client):
    response = await async_client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
```

**pytest Configuration (`pyproject.toml`):**
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
```

**Run Tests:**
```bash
# Using uv
uv run pytest

# With coverage
uv run pytest --cov=app tests/
```

**Best Practice Reference:** [Set tests client async from day 0](https://github.com/zhanymkanov/fastapi-best-practices#set-tests-client-async-from-day-0)

---

### 8. ✅ Code Formatting with Ruff

**What Changed:**
- Added `ruff` to dev dependencies
- Created `scripts/format.sh` for automated formatting
- Added Ruff configuration to `pyproject.toml`

**Ruff Configuration (`pyproject.toml`):**
```toml
[tool.ruff]
line-length = 99
target-version = "py313"

[tool.ruff.lint]
select = [
    "E", "W",      # pycodestyle
    "F",           # Pyflakes
    "I",           # isort (import sorting)
    "B",           # flake8-bugbear
    "C4",          # flake8-comprehensions
    "UP",          # pyupgrade
    "ARG",         # unused arguments
    "SIM",         # flake8-simplify
]
```

**Usage:**
```bash
# Check for issues (auto-fix when possible)
uv run ruff check --fix app tests

# Format code
uv run ruff format app tests

# Or use the provided script
bash scripts/format.sh
```

**Setup Pre-commit Hook (Optional):**
Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
ruff check --fix app tests && ruff format app tests
```

**Benefits:**
- Single tool replaces: black, isort, autoflake, flake8
- Blazingly fast (10-100x faster than black)
- Consistent code style across team
- CI/CD integration ready

**Best Practice Reference:** [Use Ruff](https://github.com/zhanymkanov/fastapi-best-practices#use-ruff)

---

## Async Routes Best Practice

Your project already demonstrates good async patterns. Key reminders:

**For I/O Operations (database, API calls):**
```python
# ✅ Good - use async/await
@router.get("/items")
async def get_items():
    items = await db.fetch_all(query)  # Non-blocking
    return items
```

**For Blocking I/O:**
```python
# ✅ Good - use threadpool for sync libraries
from fastapi.concurrency import run_in_threadpool

@router.get("/compute")
async def heavy_task():
    result = await run_in_threadpool(sync_blocking_call)
    return result
```

**For CPU-Intensive Tasks:**
```python
# ⚠️ Consider: Move to background workers or separate process
# ThreadPool/Async won't help due to GIL
# Use: Celery, RQ, or similar task queue
```

**Reference:** [Async Routes](https://github.com/zhanymkanov/fastapi-best-practices#async-routes)

---

## Next Steps & Recommendations

### 1. Add More Domain Modules
Create additional modules following the same pattern:
```bash
mkdir -p app/items app/users app/orders
# Each with: router.py, schemas.py, service.py, etc.
```

### 2. Implement Database Integration
- Use `SQLAlchemy` with proper naming conventions
- Add Alembic for migrations
- Follow SQL-first, Pydantic-second principle

### 3. Add Authentication/Authorization
- Create `app/auth/` module
- Implement JWT token validation as dependency
- Chain with other dependencies (e.g., valid_user -> valid_admin)

### 4. Error Handling Middleware
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "path": str(request.url)},
    )
```

### 5. Request Logging Middleware
```python
@app.middleware("http")
async def log_request_details(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    logger.info(
        f"{request.method} {request.url.path}",
        extra={"status": response.status_code, "duration_ms": duration}
    )
    return response
```

### 6. Environment-Specific Docs
```python
# Only show docs in development
if settings.ENV not in ("production",):
    app_configs["openapi_url"] = "/openapi.json"
else:
    app_configs["openapi_url"] = None
```

---

## File Organization Summary

```
fastapi-observable/
├── app/
│   ├── main.py                      # Application factory
│   ├── config.py                    # Global settings
│   ├── schemas.py                   # Custom BaseModel
│   ├── exceptions.py                # Exception hierarchy
│   ├── dependencies.py              # Shared dependencies
│   ├── logger.py                    # Logging setup
│   ├── observability.py             # Tracing/profiling
│   │
│   ├── health/                      # Health check domain
│   │   ├── __init__.py
│   │   ├── router.py               # Endpoints
│   │   ├── schemas.py              # Response models
│   │   ├── service.py              # Business logic
│   │   ├── dependencies.py         # Route dependencies
│   │   ├── config.py               # Module config
│   │   ├── constants.py            # Enums/constants
│   │   ├── exceptions.py           # Module exceptions
│   │   └── utils.py                # Helpers
│   │
│   └── observability_endpoints/    # Demo endpoints
│       ├── router.py
│       ├── schemas.py
│       ├── service.py
│       └── config.py
│
├── tests/                           # Test directory
│   ├── conftest.py                 # Pytest fixtures
│   ├── __init__.py
│   ├── health/
│   │   ├── __init__.py
│   │   └── test_router.py          # Health tests
│   │
│   └── observability_endpoints/    # Additional tests
│
├── k8s/                            # Kubernetes configs
│   ├── deployment.yaml
│   ├── fluent-bit-parser.conf
│   └── prometheus-config-snippet.yaml
│
├── scripts/
│   ├── uv_setup.sh
│   └── format.sh                   # Ruff formatting
│
├── Dockerfile                       # Container build
├── pyproject.toml                   # Dependencies & config
├── README.md                        # Documentation
└── locustfile.py                    # Load testing
```

---

## Commands Reference

```bash
# Development setup
uv sync

# Run app
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest
uv run pytest --cov=app tests/

# Code formatting
uv run ruff check --fix app tests
uv run ruff format app tests
# OR
bash scripts/format.sh

# Type checking (optional, add mypy)
uv run mypy app

# Docker build/run
docker build -t fastapi-obs:latest .
docker run -p 8000:8000 --env-file .env fastapi-obs:latest
```

---

## Key Takeaways

1. **Domain-based structure** scales better than file-type organization
2. **Custom BaseModel** ensures consistent serialization across your app
3. **Dependencies are powerful** for reusable validation and authorization
4. **Proper response models** auto-document your API
5. **Global exceptions** provide consistent error handling
6. **Async from day 0** prevents tech debt and event loop issues
7. **Ruff** catches bugs and maintains code style automatically
8. **Decoupled config** makes environment management easy

Start with these 8 patterns, and your FastAPI project will be well-structured,
maintainable, and aligned with production best practices!

---

**Happy coding!** 🚀
"""
