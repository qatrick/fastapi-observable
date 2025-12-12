# Quick Start Guide - FastAPI Best Practices Stack

Get your enhanced FastAPI Observable project running in minutes!

## 1️⃣ Install Dependencies

```bash
# Setup the environment with uv
uv sync
```

This installs all dependencies from `pyproject.toml`:
- FastAPI, Uvicorn, Pydantic
- OpenTelemetry (tracing)
- Prometheus (metrics)
- Pytest, HTTPx (testing)
- Ruff (linting/formatting)

## 2️⃣ Start the Application

```bash
# Run with auto-reload for development
uv run uvicorn app.main:app --reload
```

**Output should show:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
Starting fastapi-observable v0.1.0 in local
```

## 3️⃣ Test the Endpoints

### In your browser or curl:

```bash
# Health Check Endpoint
curl http://localhost:8000/health
# Returns: {"status":"healthy","pod_name":"unknown-pod",...}

# Lightweight Async Computation
curl http://localhost:8000/observability/light
# Returns: {"result":50005000,"computation_type":"async","duration_ms":...}

# CPU-Intensive Computation (runs in threadpool)
curl http://localhost:8000/observability/heavy
# Returns: {"result":49999995000000,"computation_type":"cpu-intensive","duration_ms":...}

# Simple Response
curl http://localhost:8000/observability/root
# Returns: {"message":"Observability Ready","pod":"unknown-pod"}
```

## 4️⃣ View API Documentation

**Option A: Swagger UI (Interactive)**
```
http://localhost:8000/docs
```

**Option B: ReDoc (Clean)**
```
http://localhost:8000/redoc
```

**Option C: OpenAPI JSON**
```
http://localhost:8000/openapi.json
```

## 5️⃣ Run Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage report
uv run pytest --cov=app tests/

# Run specific test file
uv run pytest tests/health/test_router.py

# Run specific test
uv run pytest tests/health/test_router.py::test_get_health_success
```

**Expected output:**
```
tests/health/test_router.py::test_get_health_success PASSED
tests/health/test_router.py::test_get_health_response_format PASSED
========================= 2 passed in 0.15s =========================
```

## 6️⃣ Format Your Code

### Option A: Using the script
```bash
bash scripts/format.sh
```

### Option B: Direct commands
```bash
# Check for issues (auto-fix)
uv run ruff check --fix app tests

# Format code
uv run ruff format app tests
```

## 📁 Key Files to Understand

| File | Purpose |
|------|---------|
| `app/main.py` | Application factory & router setup |
| `app/config.py` | Global configuration settings |
| `app/schemas.py` | Custom BaseModel with datetime handling |
| `app/exceptions.py` | Exception hierarchy |
| `app/dependencies.py` | Shared dependencies |
| `app/health/router.py` | Health check endpoints |
| `app/observability_endpoints/router.py` | Demo observability endpoints |
| `tests/conftest.py` | Test fixtures |
| `pyproject.toml` | Dependencies & configuration |

## 🎯 Common Tasks

### Add a New Endpoint to Existing Module
```python
# In app/health/router.py
@router.get(
    "/status",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def get_status():
    """Get current status."""
    return {"status": "ok"}
```

### Create a New Domain Module

```bash
# 1. Create directory structure
mkdir -p app/items
touch app/items/{__init__,router,schemas,service,dependencies,config,constants,exceptions,utils}.py

# 2. Use app/health/ as template
# 3. Include router in app/main.py:
#    from .items.router import router as items_router
#    app.include_router(items_router)
```

### Write a Test
```python
# In tests/items/test_router.py
import pytest

@pytest.mark.asyncio
async def test_get_item(async_client):
    response = await async_client.get("/items/1")
    assert response.status_code == 200
```

### Check Types (Optional)
```bash
# Install mypy first
uv pip install mypy

# Check for type errors
uv run mypy app
```

## 🚀 Environment Configuration

### Using .env file
```bash
# Create .env file
cat > .env << EOF
APP_NAME=my-fastapi-app
ENV=development
ENABLE_METRICS=true
POD_NAME=dev-pod-01
EOF

# App automatically reads from .env
uv run uvicorn app.main:app --reload
```

### Override with environment variables
```bash
# Linux/Mac
ENV=production uv run uvicorn app.main:app

# Windows PowerShell
$env:ENV="production"; uv run uvicorn app.main:app

# Windows Command Prompt
set ENV=production && uv run uvicorn app.main:app
```

## 📚 Documentation Files

After starting the app, review these for deeper understanding:

1. **ENHANCEMENT_SUMMARY.md** - What was changed and why
2. **BEST_PRACTICES_GUIDE.md** - Detailed explanations with examples
3. **MIGRATION_GUIDE.md** - How to convert existing code
4. **ARCHITECTURE.md** - Visual diagrams and flows
5. **ENHANCEMENT_VALIDATION_CHECKLIST.md** - Verification of all features

## ⚙️ Docker Support

```bash
# Build image
docker build -t fastapi-observable:latest .

# Run container
docker run -p 8000:8000 \
  --env-file .env \
  fastapi-observable:latest

# Access app
curl http://localhost:8000/health
```

## 🐛 Troubleshooting

**Issue: ModuleNotFoundError when running app**
```bash
# Solution: Make sure dependencies are installed
uv sync
```

**Issue: Port 8000 already in use**
```bash
# Solution: Use a different port
uv run uvicorn app.main:app --port 8001
```

**Issue: Tests fail with event loop error**
```bash
# Solution: Already fixed! Using AsyncClient from day 0
# Just run: uv run pytest
```

**Issue: Ruff formatting issues**
```bash
# Solution: Run formatter
bash scripts/format.sh
```

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] `uv sync` completes without errors
- [ ] `uv run uvicorn app.main:app --reload` starts
- [ ] http://localhost:8000/docs loads Swagger UI
- [ ] http://localhost:8000/health returns 200
- [ ] `uv run pytest` passes all tests
- [ ] `bash scripts/format.sh` formats code without errors
- [ ] API docs show all endpoints with descriptions

## 🎓 Learning Path

1. **Start here:** Read `ARCHITECTURE.md` for visual understanding
2. **Understand patterns:** Read `BEST_PRACTICES_GUIDE.md`
3. **Scale up:** Follow `MIGRATION_GUIDE.md` to add new modules
4. **Write tests:** Use `tests/health/test_router.py` as template
5. **Format code:** Use `scripts/format.sh` regularly

## 💡 Pro Tips

1. **Use async dependencies** - Avoid threadpool overhead
2. **Cache dependencies** - FastAPI caches them per-request automatically
3. **Write response models** - FastAPI validates and documents them
4. **Include descriptions** - Auto-generates OpenAPI docs
5. **Use status_code** - Explicit better than implicit
6. **Chain dependencies** - One dependency can use another
7. **Keep modules small** - Each module should have single responsibility
8. **Test early** - Write tests as you add features

## 📞 Getting Help

**View app logs:**
```bash
# Logs are output to console during development
# Check stdout for errors and info messages
```

**Check endpoint details:**
```bash
# Visit http://localhost:8000/docs
# Click on endpoint to see request/response schemas
```

**Validate structure:**
```bash
# Run this to verify all imports work
python -c "from app.main import app; print('✓ All imports OK')"
```

---

**You're all set!** 🎉

Your FastAPI Observable project now has enterprise-grade structure and best practices built in.

**Next step:** Start exploring the endpoints and review the documentation files to understand the patterns used.

Happy coding! 🚀
