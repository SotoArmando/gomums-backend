# Backend Integration Checklist

## 📋 Overview

This checklist guides you through setting up your PostgreSQL database and Python + FastAPI backend to power the GoMums app.

## ✅ Phase 1: Database Setup

### 1.1 PostgreSQL Installation
- [ ] Install PostgreSQL 14+ on your server
- [ ] Create database: `CREATE DATABASE gomums;`
- [ ] Create database user with appropriate permissions
- [ ] Configure connection settings (host, port, credentials)

### 1.2 Schema Migration
- [ ] Run `DATABASE_SCHEMA.sql` to create all tables
- [ ] Verify all tables created successfully
- [ ] Test triggers (updated_at should auto-update)
- [ ] Test constraints (CHECKs, FOREIGN KEYs)
- [ ] Verify indexes created

### 1.3 Seed Data (Optional)
- [ ] Create some sample recipes
- [ ] Create test missions and challenges
- [ ] Create sample achievements
- [ ] Create default home sections
- [ ] Add sample articles/videos

## ✅ Phase 2: Backend Server Setup

### 2.1 Technology Stack
**Selected: Python + FastAPI**

Install dependencies:
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install FastAPI and dependencies
pip install fastapi uvicorn[standard] psycopg2-binary pydantic pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart

# For Google OAuth (optional)
pip install google-auth google-auth-oauthlib google-auth-httplib2

# Save dependencies
pip freeze > requirements.txt
```

<details>
<summary>Alternative Options (Not Used)</summary>

**Option A: Node.js + Express**
```bash
npm init -y
npm install express pg jsonwebtoken bcryptjs cors dotenv
npm install --save-dev typescript @types/node @types/express ts-node nodemon
```

**Option B: Node.js + Fastify**
```bash
npm init -y
npm install fastify @fastify/cors @fastify/jwt postgres bcryptjs dotenv
```
</details>

### 2.2 Project Structure
- [ ] Create folder structure:
  ```
  backend/
  ├── app/
  │   ├── api/
  │   │   ├── routes/        # API route handlers
  │   │   ├── dependencies/  # Dependency injection
  │   │   └── __init__.py
  │   ├── core/
  │   │   ├── config.py      # Settings & config
  │   │   ├── security.py    # Auth, JWT
  │   │   └── database.py    # DB connection
  │   ├── models/            # Pydantic models (schemas)
  │   ├── services/          # Business logic
  │   ├── db/
  │   │   ├── models.py      # SQLAlchemy models (optional)
  │   │   └── repositories/  # Database queries
  │   └── main.py            # Entry point
  ├── .env                   # Environment variables
  ├── requirements.txt       # Python dependencies
  └── alembic/              # Database migrations (optional)
  ```

### 2.3 Environment Configuration
- [ ] Create `.env` file:
  ```env
  # Database
  DATABASE_HOST=localhost
  DATABASE_PORT=5432
  DATABASE_NAME=gomums
  DATABASE_USER=postgres
  DATABASE_PASSWORD=your_password
  
  # JWT
  JWT_SECRET=your-super-secret-key-change-in-production
  JWT_EXPIRES_IN=24h
  REFRESH_TOKEN_SECRET=your-refresh-secret
  REFRESH_TOKEN_EXPIRES_IN=7d
  
  # Server
  PORT=8000
  ENVIRONMENT=development
  CORS_ORIGINS=["http://localhost:5173"]
  
  # Google OAuth (optional)
  GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
  GOOGLE_CLIENT_SECRET=your-client-secret
  ```

### 2.4 Database Connection
- [ ] Create database connection pool
- [ ] Test connection on startup
- [ ] Handle connection errors gracefully
- [ ] Implement connection retry logic

Example (Python with psycopg2):
```python
# app/core/database.py
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import os

class Database:
    def __init__(self):
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,
            host=os.getenv('DATABASE_HOST'),
            port=os.getenv('DATABASE_PORT', '5432'),
            database=os.getenv('DATABASE_NAME'),
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD')
        )
    
    @contextmanager
    def get_connection(self):
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, commit=False):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                if commit:
                    conn.commit()
            finally:
                cursor.close()

db = Database()
```

## ✅ Phase 3: Authentication Implementation

### 3.1 Password Hashing
- [ ] Implement bcrypt password hashing
- [ ] Hash on user registration
- [ ] Verify on login

Example:
```python
# app/core/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 3.2 JWT Token Generation
- [ ] Generate access token on login
- [ ] Generate refresh token
- [ ] Include user ID in token payload
- [ ] Set appropriate expiration times

Example:
```python
# app/core/security.py
from jose import jwt
from datetime import datetime, timedelta
import os

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, 
        os.getenv('JWT_SECRET'), 
        algorithm='HS256'
    )
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        os.getenv('REFRESH_TOKEN_SECRET'),
        algorithm='HS256'
    )
    return encoded_jwt
```

### 3.3 Authentication Middleware
- [ ] Create dependency to verify JWT
- [ ] Extract user from token
- [ ] Inject user into request
- [ ] Handle expired tokens

Example:
```python
# app/core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token, 
            os.getenv('JWT_SECRET'), 
            algorithms=['HS256']
        )
        user_id: str = payload.get('sub')
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token'
            )
        return {'id': user_id, **payload}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token'
        )
```

### 3.4 Auth Endpoints
- [ ] POST `/auth/register`
- [ ] POST `/auth/login`
- [ ] POST `/auth/logout`
- [ ] POST `/auth/refresh`
- [ ] GET `/auth/me`

## ✅ Phase 4: Core API Implementation

Implement endpoints in priority order:

### 4.1 Priority 1: Essential User Flow
- [x] **Auth endpoints** (login, register, logout, refresh, me) - ✅ 5 endpoints complete
- [x] **Journal**: GET `/journal/entries`, POST `/journal/entries` - ✅ 8 endpoints complete (full CRUD + linking)
- [x] **Budget**: GET `/budget/stats`, GET `/budget/entries` - ✅ 9 endpoints complete (full CRUD + stats)
- [x] **Recipes**: GET `/recipes`, GET `/recipes/:id` - ✅ 3 endpoints complete (list, get by ID, count)

### 4.2 Priority 2: Main Features
- [x] **Journal**: PATCH/DELETE entries, link meals to purchases - ✅ Already complete (8 endpoints)
- [x] **Budget**: POST/PATCH/DELETE entries, category breakdown - ✅ Already complete (9 endpoints)
- [x] **Missions**: GET active, update progress - ✅ **4 endpoints complete** (active, update progress, stats, assign daily)
  - ✅ **Event-driven auto-updates**: Missions automatically update when journal/budget entries are created
    - Integrated with journal_repository.py (line 92) and budget_repository.py (line 58)
    - Handles transaction isolation: COUNT queries adjusted for uncommitted entries
    - Non-blocking: Mission errors don't fail journal/budget operations
  - ✅ **Auto-expiration**: Daily missions expire after 24 hours, status automatically updated on fetch
  - ✅ **Point rewards**: Completed missions automatically award points to user_stats
    - Uses INSERT...ON CONFLICT pattern to handle missing user_stats rows
    - Column names: total_meals_cooked, total_money_saved, current_streak
  - ✅ **Budget validation**: Daily budget missions compare spending vs (weekly_budget / 7)
  - ✅ **Test automation**: 3 test scripts (test_mission_automation.py, cleanup_test_user.py, simulate_mission_time.py)
  - **Technical notes**: Mission updates run synchronously in the same transaction as the triggering action. The service accounts for transaction isolation by adding +1 to COUNT results since the current entry isn't yet visible to the query.
- [x] **User**: GET/PATCH profile, preferences, stats - ✅ 6 endpoints complete (profile, preferences, stats CRUD)

### 4.3 Priority 3: Advanced Features
- [ ] **Challenges**: Join, update goals
- [ ] **Meal Plans**: CRUD operations
- [ ] **Home**: Sections, smart suggestions
- [ ] **Content**: Articles, videos

### 4.4 Priority 4: Nice-to-Have
- [ ] Search functionality
- [ ] Filtering and pagination
- [ ] Bulk operations
- [ ] Export data

## ✅ Phase 5: Frontend Integration

### 5.1 Environment Setup
Add to frontend `.env`:
```env
VITE_API_BASE_URL=http://localhost:3000/api
```

### 5.2 Create Services Layer
- [ ] Create `src/services/api/` directory
- [ ] Implement `http-client.ts` from API_INTEGRATION.md
- [ ] Create `config.ts` with endpoints
- [ ] Implement service files (journal, budget, etc.)

### 5.3 Create Transformers
- [ ] Create `src/services/transformers/` directory
- [ ] Implement transformers to convert between DTOs and frontend types
- [ ] Handle date conversions (string ↔ Date)
- [ ] Handle field name conversions (snake_case ↔ camelCase)

### 5.4 Update Stores
- [ ] Remove mock data from stores
- [ ] Add `loading` and `error` state
- [ ] Implement `fetch` methods to call API
- [ ] Update mutation methods to call API
- [ ] Add error handling

Example:
```typescript
// src/stores/journal-store.ts
async fetchEntries(): Promise<void> {
  this.loading = true
  this.error = null
  this.notify()

  try {
    const dtos = await journalService.getEntries()
    this.entries = JournalTransformer.toJournalEntries(dtos)
  } catch (error) {
    this.error = error as Error
  } finally {
    this.loading = false
    this.notify()
  }
}
```

### 5.5 Update Views
- [ ] Call `store.fetchEntries()` in `connectedCallback()`
- [ ] Show loading spinner when `store.isLoading()`
- [ ] Display error message when `store.getError()`
- [ ] Handle empty states

Example:
```typescript
// src/views/diary-view.ts
async connectedCallback() {
  super.connectedCallback()
  await journalStore.fetchEntries()
}

render() {
  if (journalStore.isLoading()) {
    return html`<loading-spinner></loading-spinner>`
  }
  
  if (journalStore.getError()) {
    return html`<div class="error">${journalStore.getError()?.message}</div>`
  }
  
  return html`...`
}
```

## ✅ Phase 6: Testing

### 6.1 Backend Testing
- [ ] Install testing framework: `pip install pytest pytest-asyncio httpx`
- [ ] Write unit tests for services
- [ ] Write integration tests for API endpoints (use TestClient from FastAPI)
- [ ] Test authentication flow
- [ ] Test error scenarios

Example:
```python
# tests/test_auth.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register():
    response = client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 201
    assert "token" in response.json()

def test_login():
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "token" in response.json()
```

### 6.2 Frontend Testing
- [ ] Test store transformers
- [ ] Test API service calls (with mocked fetch)
- [ ] Test error handling in views

### 6.3 End-to-End Testing
- [ ] Test complete user flows
- [ ] Test with real database
- [ ] Test token refresh flow
- [ ] Test offline behavior (if implemented)

## ✅ Phase 7: Production Preparation

### 7.1 Security
- [ ] Enable CORS with specific origins
- [ ] Implement rate limiting (use `slowapi` library)
- [ ] Add request validation (Pydantic handles this automatically)
- [ ] Sanitize user inputs
- [ ] Use HTTPS in production
- [ ] Secure environment variables
- [ ] Implement SQL injection protection (use parameterized queries)

Example rate limiting:
```python
# pip install slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginData):
    # Login logic
    pass
```

### 7.2 Performance
- [ ] Add database connection pooling
- [ ] Implement pagination for large datasets
- [ ] Add database indexes where needed
- [ ] Enable response compression
- [ ] Consider caching frequently accessed data

### 7.3 Monitoring & Logging
- [ ] Implement logging (Python logging, Loguru, or similar)
- [ ] Log errors with stack traces
- [ ] Log API requests
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Monitor database performance

### 7.4 Deployment
- [ ] Choose hosting platform (AWS, Heroku, DigitalOcean, Railway, Render, etc.)
- [ ] Set up production database (managed PostgreSQL recommended)
- [ ] Configure environment variables
- [ ] Set up CI/CD pipeline
- [ ] Create Dockerfile (optional but recommended)
- [ ] Deploy backend with ASGI server: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] Update frontend API URL
- [ ] Test production deployment

**Python-specific deployment tips:**
- Use `gunicorn` with `uvicorn` workers for production: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker`
- Set up process manager (systemd, supervisor, or Docker)
- Ensure `requirements.txt` is up to date
- Consider using `.env` file or cloud secrets manager

## 🎯 Quick Start Example (FastAPI + Python)

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import db
from app.api.routes import auth, journal
from app.core.config import settings
import uvicorn

app = FastAPI(title="GoMums API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test database connection on startup
@app.on_event("startup")
async def startup():
    try:
        with db.get_cursor() as cursor:
            cursor.execute("SELECT NOW()")
            result = cursor.fetchone()
            print(f"Database connected: {result[0]}")
    except Exception as e:
        print(f"Database connection failed: {e}")
        exit(1)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(journal.router, prefix="/api/journal", tags=["journal"])

# Health check
@app.get("/health")
def health_check():
    from datetime import datetime
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# Run with: uvicorn app.main:app --reload --port 8000
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_HOST: str
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    
    JWT_SECRET: str
    JWT_EXPIRES_IN: str = "24h"
    REFRESH_TOKEN_SECRET: str
    REFRESH_TOKEN_EXPIRES_IN: str = "7d"
    
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## 📚 Reference Documentation

- **Database Schema**: `DATABASE_SCHEMA.sql`
- **API Endpoints**: `API_ENDPOINTS.md`
- **Integration Guide**: `API_INTEGRATION.md`
- **Type Definitions**: `src/stores/types.ts`
- **Store Architecture**: `STATE_MANAGEMENT.md`

## 🆘 Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check credentials in `.env`
- Ensure database exists
- Check firewall rules

### CORS Errors
- Set correct `CORS_ORIGIN` in backend
- Include credentials if needed: `credentials: true`
- Check request headers

### Authentication Errors
- Verify JWT_SECRET is set
- Check token expiration
- Ensure token is sent in Authorization header

### Type/Schema Errors
- Ensure Pydantic models match frontend types
- Check transformer implementations
- Verify DTO/schema definitions
- Use Pydantic for request/response validation

## 💡 Tips

1. **Start Small**: Implement auth + one feature (journal) first, then expand
2. **Test Early**: Test each endpoint as you build it (use Postman/Thunder Client)
3. **Use Type Hints**: Pydantic models and Python type hints prevent many errors
4. **Consistent Naming**: Follow snake_case for DB and Python, camelCase for frontend
5. **Error Messages**: Provide clear, actionable error messages
6. **Documentation**: Keep API_ENDPOINTS.md updated as you build
7. **Auto Docs**: FastAPI generates interactive docs at `/docs` and `/redoc`
