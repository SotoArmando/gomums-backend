# GoMums Backend Setup Guide

## Quick Start

### 1. Install PostgreSQL

Download and install PostgreSQL 14+ from [postgresql.org](https://www.postgresql.org/download/)

After installation, create the database:

```powershell
# Open PowerShell and connect to PostgreSQL
psql -U postgres

# In psql, create the database
CREATE DATABASE gomums;

# Exit psql
\q
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and update the values:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and update:
- `DATABASE_PASSWORD` - your PostgreSQL password
- `JWT_SECRET` - a strong random string for production
- `REFRESH_TOKEN_SECRET` - another strong random string

### 3. Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# You should see (venv) in your prompt
```

### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 5. Create Database Schema

```powershell
# Make sure PostgreSQL is running
# Run the schema file
psql -U postgres -d gomums -f docs\DATABASE_SCHEMA.sql
```

### 6. Run the Server

**Quick Start (Either Platform):**
```bash
# Windows PowerShell
.\start.ps1

# Linux/WSL
chmod +x start.sh
./start.sh
```

**Manual Start:**

**Windows:**
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

**Linux/WSL:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

The server should start at `http://localhost:8000`

### 7. Test the API

Open your browser and visit:
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Project Structure

```
gomums-backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   ├── database.py      # Database connection pool
│   │   └── security.py      # Authentication & JWT
│   ├── api/
│   │   ├── routes/          # API route handlers (TODO)
│   │   └── dependencies/    # Shared dependencies
│   ├── models/              # Pydantic schemas (TODO)
│   ├── services/            # Business logic (TODO)
│   └── db/
│       ├── models.py        # Database models (TODO)
│       └── repositories/    # Database queries (TODO)
├── docs/
│   ├── DATABASE_SCHEMA.sql  # Database schema
│   ├── API_ENDPOINTS.md     # API documentation
│   └── BACKEND_CHECKLIST.md # Setup checklist
├── .env                      # Environment variables (create from .env.example)
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
└── SETUP.md                  # This file
```

## Next Steps

Now that the core is set up, you need to implement:

1. **Authentication Routes** (`app/api/routes/auth.py`)
   - POST `/api/auth/register`
   - POST `/api/auth/login`
   - POST `/api/auth/refresh`
   - GET `/api/auth/me`

2. **Pydantic Models** (`app/models/`)
   - Request/response schemas for all endpoints

3. **Database Repositories** (`app/db/repositories/`)
   - Functions to query and manipulate database

4. **API Routes** (priority order)
   - Journal endpoints
   - Budget endpoints
   - Recipes endpoints
   - User profile endpoints

Refer to `docs/BACKEND_CHECKLIST.md` for detailed implementation steps.

## Troubleshooting

### Database Connection Error

If you see "Database connection failed":
1. Check if PostgreSQL is running
2. Verify credentials in `.env` file
3. Ensure database `gomums` exists
4. Check if PostgreSQL is listening on port 5432

### Module Not Found Error

If you see import errors:
1. Make sure virtual environment is activated
2. Run `pip install -r requirements.txt`
3. Check if you're in the correct directory

### Port Already in Use

If port 8000 is already in use:
1. Change `PORT=8001` in `.env`
2. Or kill the process using port 8000

## Commands Reference

```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn app.main:app --reload --port 8000

# Or run directly
python app/main.py

# Deactivate virtual environment
deactivate

# Connect to PostgreSQL
psql -U postgres -d gomums

# Run database migrations (when you add data)
psql -U postgres -d gomums -f docs\DATABASE_SCHEMA.sql
```
