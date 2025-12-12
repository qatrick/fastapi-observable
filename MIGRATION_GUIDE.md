"""Migration Guide: Updating Your Existing Code

This guide helps you migrate your existing endpoints to the new best practices structure.

## Example: Moving an Existing Endpoint

### Before (Old Structure)
```python
# app/main.py (mixed everything)
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.get_user(user_id)
    return user  # Direct dict response
```

### After (New Structure with Best Practices)

#### 1. Create Module Structure
```bash
mkdir -p app/users
touch app/users/{__init__,router,schemas,service,dependencies,config,constants,exceptions}.py
```

#### 2. Define Schemas (`app/users/schemas.py`)
```python
from app.schemas import CustomModel
from pydantic import Field

class UserResponse(CustomModel):
    id: int = Field(description="User ID")
    username: str = Field(min_length=1, max_length=128)
    email: str = Field(pattern=r"^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$")
    created_at: str = Field(description="ISO format timestamp")
```

#### 3. Define Constants (`app/users/constants.py`)
```python
from enum import Enum

class UserErrorCode(str, Enum):
    USER_NOT_FOUND = "USER_NOT_FOUND"
    INVALID_EMAIL = "INVALID_EMAIL"
    USERNAME_EXISTS = "USERNAME_EXISTS"

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
```

#### 4. Define Exceptions (`app/users/exceptions.py`)
```python
from fastapi import HTTPException, status

class UserNotFound(HTTPException):
    def __init__(self, user_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

class UsernameAlreadyExists(HTTPException):
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{username}' already exists"
        )
```

#### 5. Add Business Logic (`app/users/service.py`)
```python
from .schemas import UserResponse

async def get_user_by_id(user_id: int) -> dict:
    user = await db.get_user(user_id)
    if not user:
        raise UserNotFound(user_id)
    return user

async def create_user(username: str, email: str) -> dict:
    existing = await db.get_by_username(username)
    if existing:
        raise UsernameAlreadyExists(username)
    
    user = await db.create_user(username=username, email=email)
    return user
```

#### 6. Add Dependencies (`app/users/dependencies.py`)
```python
from pydantic import UUID4
from .service import get_user_by_id

async def valid_user_id(user_id: int) -> dict:
    \"\"\"Validate that user exists. Can be reused across routes.\"\"\"
    return await get_user_by_id(user_id)
```

#### 7. Define Routes (`app/users/router.py`)
```python
from fastapi import APIRouter, status, Depends
from .schemas import UserResponse
from .dependencies import valid_user_id
from .service import create_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Retrieve user information by user ID",
)
async def get_user(
    user: dict = Depends(valid_user_id)
) -> UserResponse:
    \"\"\"
    Get a single user by ID.
    
    - **user_id**: User ID to fetch
    
    Returns:
        UserResponse: User information
    \"\"\"
    return UserResponse(**user)

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Create a new user account",
)
async def create_user_endpoint(
    username: str,
    email: str,
) -> UserResponse:
    user = await create_user(username=username, email=email)
    return UserResponse(**user)
```

#### 8. Module Config (`app/users/config.py`)
```python
from pydantic_settings import BaseSettings

class UsersConfig(BaseSettings):
    MAX_USERNAME_LENGTH: int = 128
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_SPECIAL_CHAR: bool = True

users_settings = UsersConfig()
```

#### 9. Include Router in Main (`app/main.py`)
```python
from .users.router import router as users_router

app.include_router(users_router)
```

#### 10. Add Tests (`tests/users/test_router.py`)
```python
import pytest

@pytest.mark.asyncio
async def test_get_user_success(async_client):
    # Assuming user 1 exists in test DB
    response = await async_client.get("/users/1")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "username" in data
    assert "email" in data

@pytest.mark.asyncio
async def test_get_user_not_found(async_client):
    response = await async_client.get("/users/99999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_create_user_success(async_client):
    response = await async_client.post(
        "/users",
        json={"username": "newuser", "email": "test@example.com"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"

@pytest.mark.asyncio
async def test_create_user_duplicate_username(async_client):
    # Assuming 'alice' already exists
    response = await async_client.post(
        "/users",
        json={"username": "alice", "email": "newemail@example.com"}
    )
    
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()
```

## Benefits of This Approach

| Aspect | Before | After |
|--------|--------|-------|
| Code Location | Mixed in main.py | Organized by domain |
| Error Handling | Inline try-catch | Centralized exceptions |
| Reusability | Limited | High (dependencies cached) |
| Testing | Hard | Easy (isolated modules) |
| Documentation | Manual | Auto-generated by FastAPI |
| Scalability | Difficult | Straightforward |
| Team Coordination | Conflicts | Clear ownership |

## Checklist for Each New Module

- [ ] Create module directory with `__init__.py`
- [ ] Define `schemas.py` with Pydantic models
- [ ] Define `constants.py` with enums
- [ ] Define `exceptions.py` with custom exceptions
- [ ] Add `service.py` with business logic
- [ ] Add `dependencies.py` for route validation
- [ ] Create `router.py` with endpoints (with all attributes: response_model, status_code, etc.)
- [ ] Add `config.py` for module-specific settings
- [ ] Add `utils.py` if needed for helpers
- [ ] Include router in `app/main.py`
- [ ] Create tests in `tests/{module_name}/`

## Common Pitfalls to Avoid

❌ **Don't:** Return raw ORM models without response_model
✅ **Do:** Always use Pydantic schemas for response_model

❌ **Don't:** Put all config in app/config.py
✅ **Do:** Use module-specific config.py files

❌ **Don't:** Repeat validation logic in multiple routes
✅ **Do:** Extract to dependencies (they get cached automatically)

❌ **Don't:** Use sync routes for database calls
✅ **Do:** Make routes async and await DB queries

❌ **Don't:** Skip error handling
✅ **Do:** Use custom exceptions from the module

❌ **Don't:** Write tests with TestClient (sync)
✅ **Do:** Use AsyncClient from day 0

## Performance Tips

1. **Dependency caching**: Same dependency called multiple times? FastAPI caches it per request.
   ```python
   @router.get("/items/{id}/details")
   async def get_item_details(
       item: dict = Depends(valid_item_id),  # Called once
       user: dict = Depends(valid_user),     # Called once
       auth: dict = Depends(check_auth),     # Called once
   ):
       # All dependencies cached even if used elsewhere
   ```

2. **Async dependencies**: Use async in dependencies to avoid threadpool overhead
   ```python
   # ✅ Good
   async def valid_item_id(item_id: int) -> dict:
       return await db.get_item(item_id)
   
   # ❌ Avoid
   def valid_item_id(item_id: int) -> dict:  # Runs in threadpool!
       return db.get_item(item_id)
   ```

3. **SQL-first**: Let the database do heavy lifting
   ```python
   # ❌ Avoid: Fetching multiple records and filtering in Python
   users = await db.fetch_all(select(User))
   admins = [u for u in users if u.is_admin]
   
   # ✅ Better: Filter at database level
   admins = await db.fetch_all(select(User).where(User.is_admin == True))
   ```

---

Happy refactoring! 🚀
"""
