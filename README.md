# 🍳 GoMums Backend API

Smart budget and meal planning backend built with FastAPI and PostgreSQL.

## 📋 Current Status

✅ **Completed:**
- Core project structure
- Database connection pool
- JWT authentication system
- Password hashing with bcrypt
- User registration & login
- Protected routes
- Token refresh mechanism
- Health check endpoints

🚧 **Next Steps:**
- Journal API endpoints
- Budget API endpoints
- Recipes API endpoints
- Meal planning endpoints
- Content management (articles, videos)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 14+
- Git

### 1. Clone & Setup

```powershell
# Navigate to project directory
cd c:\Users\Armando Soto\Documents\GitHub\gomums-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```powershell
# Start PostgreSQL and create database
psql -U postgres

# In psql:
CREATE DATABASE gomums;
\q

# Run schema migration
psql -U postgres -d gomums -f docs\DATABASE_SCHEMA.sql
```

### 3. Environment Configuration

```powershell
# Copy environment template
Copy-Item .env.example .env

# Edit .env and update:
# - DATABASE_PASSWORD (your PostgreSQL password)
# - JWT_SECRET (generate a strong random string)
# - REFRESH_TOKEN_SECRET (generate another strong random string)
```

### 4. Run Server

```powershell
# Make sure virtual environment is activated
python -m uvicorn app.main:app --reload --port 8000
```

### 5. Test Authentication

```powershell
# Run the test script
python test_auth.py

# Or visit the interactive docs
start http://localhost:8000/docs
```

## 📁 Project Structure

```
gomums-backend/
├── app/
│   ├── main.py                    # FastAPI application entry
│   ├── core/
│   │   ├── config.py              # Settings & environment variables
│   │   ├── database.py            # PostgreSQL connection pool
│   │   └── security.py            # JWT & password hashing
│   ├── api/
│   │   ├── routes/
│   │   │   └── auth.py            # ✅ Authentication endpoints
│   │   └── dependencies/
│   ├── models/
│   │   ├── user.py                # User Pydantic schemas
│   │   └── auth.py                # Auth Pydantic schemas
│   ├── db/
│   │   └── repositories/
│   │       └── user_repository.py # User database operations
│   └── services/                  # Business logic (TODO)
├── docs/
│   ├── DATABASE_SCHEMA.sql        # Database schema
│   ├── API_ENDPOINTS.md           # API documentation
│   └── BACKEND_CHECKLIST.md       # Implementation checklist
├── .env                            # Environment variables
├── .env.example                    # Environment template
├── requirements.txt                # Python dependencies
├── SETUP.md                        # Detailed setup guide
├── TEST_AUTH.md                    # Authentication testing guide
└── test_auth.py                    # Automated test script
```

## 🔐 Authentication Endpoints

All authentication endpoints are under `/api/auth`:

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Create new user | ❌ |
| POST | `/login` | Authenticate user | ❌ |
| POST | `/refresh` | Get new access token | ❌ |
| GET | `/me` | Get current user | ✅ |
| POST | `/logout` | Logout user | ✅ |

### Example: Register

```bash
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepass123"
}

Response (201):
{
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "is_active": true,
    "is_premium": false,
    "created_at": "2026-02-07T10:00:00"
  },
  "token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "token_type": "bearer"
}
```

### Using Protected Endpoints

```bash
GET /api/auth/me
Authorization: Bearer <your_token_here>
```

## 📚 Documentation

- **Interactive API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Setup Guide**: [SETUP.md](SETUP.md)
- **Testing Guide**: [TEST_AUTH.md](TEST_AUTH.md)
- **Implementation Checklist**: [docs/BACKEND_CHECKLIST.md](docs/BACKEND_CHECKLIST.md)

## 🧪 Testing

### Automated Test Script

```powershell
python test_auth.py
```

### Manual Testing (PowerShell)

```powershell
# Register
$body = @{name="Test User"; email="test@example.com"; password="test123"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" -Method POST -ContentType "application/json" -Body $body

# Login
$body = @{email="test@example.com"; password="test123"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -ContentType "application/json" -Body $body
$token = $response.token

# Get current user
$headers = @{Authorization="Bearer $token"}
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/me" -Method GET -Headers $headers
```

## 🗄️ Database Schema

The database includes tables for:
- ✅ Users (with authentication)
- 📝 Journal entries
- 💰 Budget entries & categories
- 🍽️ Recipes, ingredients, meal plans
- 🎯 Missions, challenges, achievements
- 📱 Home sections & content

See [docs/DATABASE_SCHEMA.sql](docs/DATABASE_SCHEMA.sql) for full schema.

## 🔧 Configuration

Environment variables (in `.env`):

```env
# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=gomums
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# JWT
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN=24h
REFRESH_TOKEN_SECRET=your-refresh-secret
REFRESH_TOKEN_EXPIRES_IN=7d

# Server
PORT=8000
ENVIRONMENT=development
CORS_ORIGINS=["http://localhost:5173"]
```

## 📝 Next Implementation Steps

Follow [docs/BACKEND_CHECKLIST.md](docs/BACKEND_CHECKLIST.md) for detailed guidance.

### Priority 1: Core Features
1. **Journal Endpoints** - Daily meal tracking
   - `GET /api/journal/entries`
   - `POST /api/journal/entries`
   - `PATCH /api/journal/entries/:id`
   - `DELETE /api/journal/entries/:id`

2. **Budget Endpoints** - Expense tracking
   - `GET /api/budget/entries`
   - `POST /api/budget/entries`
   - `GET /api/budget/stats`
   - `GET /api/budget/categories`

3. **Recipes Endpoints** - Recipe management
   - `GET /api/recipes`
   - `GET /api/recipes/:id`
   - `POST /api/recipes` (admin)

### Priority 2: Extended Features
- Meal planning
- Missions & challenges
- User preferences & stats
- Content management

## 🌎 Regional Recipe Generation

GoMums now supports AI-powered regional recipe generation! Generate 100 culturally-authentic recipes for different regions using local ingredient data.

### Supported Regions
- **🇩🇴 Dominican Republic** - Traditional Caribbean cuisine
- **🌾 Kansas** - Midwestern American & BBQ

### Quick Start

```bash
# Generate recipes (requires OpenAI API key)
python scripts/seeds/seed_regional_recipes.py
```

**What it does:**
- Reads local ingredient prices from CSV files
- Generates authentic regional recipes using AI
- Includes nutrition info, difficulty levels, and step-by-step instructions
- Seeds recipes directly into your database

**Requirements:**
- OpenAI API key (add `OPENAI_API_KEY` to `.env`)
- Cost: ~$1-2 for 200 recipes

📖 See [docs/REGIONAL_RECIPES_GUIDE.md](docs/REGIONAL_RECIPES_GUIDE.md) for detailed instructions.

## 🐛 Troubleshooting

### Server won't start
- Check if PostgreSQL is running
- Verify `.env` configuration
- Ensure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`

### Database connection error
- Verify PostgreSQL is running: `psql -U postgres`
- Check credentials in `.env`
- Ensure `gomums` database exists
- Check port 5432 is not blocked

### Import errors
- Activate virtual environment: `.\venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Port already in use
- Change `PORT` in `.env` to 8001
- Or kill process on port 8000

## 🤝 Contributing

1. Follow the structure in [docs/BACKEND_CHECKLIST.md](docs/BACKEND_CHECKLIST.md)
2. Create Pydantic models in `app/models/`
3. Create repositories in `app/db/repositories/`
4. Create routes in `app/api/routes/`
5. Register routes in `app/main.py`
6. Test with `http://localhost:8000/docs`

## 📄 License

[Your License Here]

---

**Built with ❤️ using FastAPI + PostgreSQL**
