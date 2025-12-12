# Project Architecture Diagram

## Overall Application Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                             │
│                      (app/main.py)                                   │
│                                                                       │
│  - Lifespan Manager (setup tracing, profiling)                       │
│  - Prometheus Metrics Mount                                          │
│  - OpenTelemetry Instrumentation                                     │
└──────────────────┬──────────────────┬───────────────────────────────┘
                   │                  │
        ┌──────────┴──────┐      ┌────┴───────────┐
        │                 │      │                │
    ┌───▼────────┐   ┌───▼──────▼────┐  ┌────────▼─────┐
    │   Health    │   │ Observability  │  │  Prometheus  │
    │   Router    │   │   Endpoints    │  │   Metrics    │
    │ (/health)   │   │ (/observability)  │  Mount       │
    └────────────┘   └────────────────┘  └──────────────┘
```

## Module Architecture Pattern

Each domain module follows this standardized structure:

```
app/
├── health/                    ← Example Domain Module
│   │
│   ├── __init__.py           (empty)
│   │
│   ├── router.py             ← HTTP Endpoints
│   │   └── GET /health (response_model=HealthCheckResponse)
│   │
│   ├── schemas.py            ← Request/Response Models
│   │   └── HealthCheckResponse(CustomModel)
│   │       └── status: HealthStatus
│   │       └── pod_name: str
│   │       └── timestamp: str (auto-serialized)
│   │
│   ├── service.py            ← Business Logic
│   │   └── async get_health_status() → dict
│   │
│   ├── dependencies.py        ← Route Dependencies (Cached)
│   │   └── async valid_health_check() → dict
│   │
│   ├── config.py             ← Module Settings
│   │   └── class HealthConfig(BaseSettings)
│   │       └── HEALTH_CHECK_TIMEOUT: int = 5
│   │
│   ├── constants.py          ← Enums & Constants
│   │   ├── class HealthStatus(str, Enum)
│   │   └── class HealthErrorCode(str, Enum)
│   │
│   ├── exceptions.py         ← Module Exceptions
│   │   └── class HealthCheckFailed(HTTPException)
│   │
│   └── utils.py              ← Helper Functions
│       └── get_current_timestamp_iso() → str
│
└── [repeat pattern for each domain module]
```

## Request-Response Flow

```
CLIENT REQUEST
     │
     ▼
┌─────────────────────────────┐
│  FastAPI Route Handler      │  (e.g., GET /health)
│  @router.get(               │
│    response_model=...,      │
│    status_code=...,         │
│    description=...          │
│  )                          │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Dependencies (Cached)      │  ← Called once per request
│  async valid_health_check() │
│      ↓                      │
│  Calls service.py           │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Business Logic (service.py)│
│  async get_health_status()  │
│      ↓                      │
│  Returns dict               │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Schema Validation          │  ← Validates response data
│  HealthCheckResponse(data)  │
│      ↓                      │
│  CustomModel handles        │
│  datetime serialization     │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  HTTP Response              │
│  status_code=200            │
│  body={JSON}                │
└──────────┬──────────────────┘
           │
           ▼
      CLIENT RESPONSE
```

## Dependency Injection & Caching

```
Request Scope
┌─────────────────────────────────────────────────┐
│                                                 │
│  async valid_health_check()  ← First call      │
│      ↓                                          │
│  Computes result                               │
│      ↓                                          │
│  Result cached in scope                        │
│      ↑                         ↑                │
│      │ (cached)                │ (cached)       │
│  Route Handler 1          Route Handler 2      │
│      │                         │                │
│  Uses dependency          Uses dependency      │
│      │                         │                │
│      └────────┬────────────────┘               │
│              ▼                                  │
│         Same instance returned                 │
│         (no re-computation)                    │
│                                                 │
└─────────────────────────────────────────────────┘
         ↓ (scope ends)
    Dependency garbage collected
```

## Exception Handling Flow

```
┌──────────────────────────┐
│  Exception Raised        │
│  in service.py           │
└────────────┬─────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Custom Exception Caught            │
│  (e.g., HealthCheckFailed)          │
│                                     │
│  from app.health.exceptions import │
│  HealthCheckFailed                  │
└────────────┬────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  HTTPException Response              │
│  {                                   │
│    "status_code": 503,               │
│    "detail": "Health check failed"   │
│  }                                   │
└──────────────────────────────────────┘
```

## Configuration Hierarchy

```
Environment Variables
         ↓
┌────────────────────┐
│ app/config.py      │ ← Global config
│ (Settings)         │   ├─ APP_NAME
└────────┬───────────┘   ├─ APP_VERSION
         │               ├─ ENV
         ├─ Loaded by ── ├─ ENABLE_METRICS
         │               └─ POD_NAME
         │
         ▼
┌─────────────────────────────────────┐
│ Module-Specific Config              │
├─────────────────────────────────────┤
│ app/health/config.py                │
│   └─ HEALTH_CHECK_TIMEOUT           │
│                                     │
│ app/observability_endpoints/config  │
│   ├─ COMPUTATION_TIMEOUT            │
│   └─ ENABLE_HEAVY_ENDPOINTS         │
└─────────────────────────────────────┘
```

## Testing Architecture

```
Test Execution
     │
     ▼
┌──────────────────────────┐
│ tests/conftest.py        │
│                          │
│ @pytest.fixture          │
│ async def async_client   │
│     ↓                    │
│ AsyncClient(app=app)     │
└──────────┬───────────────┘
           │
           ▼
┌────────────────────────────────────┐
│ Test Functions                     │
│                                    │
│ @pytest.mark.asyncio               │
│ async def test_get_health(         │
│     async_client                   │
│ ):                                 │
│     response = await async_client. │
│         get("/health")             │
│     assert response.status_code==200
│     assert data["status"]=="healthy"
│                                    │
└────────────────────────────────────┘
```

## Datetime Serialization Pipeline

```
Input: datetime object (possibly naive)
    │
    ▼
CustomModel.datetime_to_iso_with_tz()
    │
    ├─ Check if timezone-aware
    │  ├─ Yes: Use as-is
    │  └─ No: Add UTC timezone
    │
    ▼
Convert to ISO 8601 string format
    │
    └─ Example: "2024-12-12T15:30:45+0000"
           │
           ▼
    JSON Response
```

## Module Inclusion in Main App

```
app/main.py
    │
    ├─ from .health.router import router as health_router
    │  └─ Include: app.include_router(health_router)
    │     ├─ Prefix: /health
    │     └─ Endpoints: GET /health
    │
    └─ from .observability_endpoints.router import router as obs_router
       └─ Include: app.include_router(obs_router)
          ├─ Prefix: /observability
          └─ Endpoints: GET /observability/root
                        GET /observability/heavy
                        GET /observability/light
```

## OpenAPI/Swagger Documentation Generation

```
Endpoint Definition
    │
    ├─ response_model: HealthCheckResponse
    ├─ status_code: 200
    ├─ description: "Get application health status"
    ├─ summary: "Health Check"
    └─ tags: ["health"]
    │
    ▼
Swagger UI (/docs)
    │
    ├─ Endpoint listed: GET /health
    ├─ Description shown
    ├─ Request/Response models documented
    ├─ Status codes displayed
    └─ "Try it out" button for testing
```

---

This architecture provides:
✅ **Scalability** - Add modules without modifying existing code
✅ **Maintainability** - Clear structure and separation of concerns
✅ **Reusability** - Shared patterns across domains
✅ **Testability** - Each module can be tested independently
✅ **Documentation** - Auto-generated from code
✅ **Production Ready** - Follows industry best practices
