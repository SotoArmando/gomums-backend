# GoMums Backend Quick Start Script
# This script helps you set up and run the backend

Write-Host @"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              🍳 GoMums Backend Setup                      ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Check if Python is installed
Write-Host "`n[1/7] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python is installed: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python is not installed. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
Write-Host "`n[2/7] Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "→ Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`n[3/7] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host "`n[4/7] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Check if .env exists
Write-Host "`n[5/7] Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file exists" -ForegroundColor Green
} else {
    Write-Host "→ Creating .env from template..." -ForegroundColor Cyan
    Copy-Item .env.example .env
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host "⚠ IMPORTANT: Edit .env and update DATABASE_PASSWORD and JWT secrets!" -ForegroundColor Yellow
    
    $edit = Read-Host "`nDo you want to edit .env now? (y/n)"
    if ($edit -eq "y") {
        notepad .env
    }
}

# Check PostgreSQL connection
Write-Host "`n[6/7] Checking PostgreSQL..." -ForegroundColor Yellow
$pgCheck = psql --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PostgreSQL is installed: $pgCheck" -ForegroundColor Green
    
    Write-Host "`n→ Checking if 'gomums' database exists..." -ForegroundColor Cyan
    $dbCheck = psql -U postgres -lqt 2>&1 | Select-String -Pattern "gomums"
    
    if ($dbCheck) {
        Write-Host "✓ Database 'gomums' exists" -ForegroundColor Green
    } else {
        Write-Host "⚠ Database 'gomums' not found" -ForegroundColor Yellow
        $createDb = Read-Host "Do you want to create it now? (y/n)"
        
        if ($createDb -eq "y") {
            Write-Host "→ Creating database..." -ForegroundColor Cyan
            psql -U postgres -c "CREATE DATABASE gomums;"
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Database created" -ForegroundColor Green
                
                $runSchema = Read-Host "Do you want to run the schema migration? (y/n)"
                if ($runSchema -eq "y") {
                    Write-Host "→ Running schema migration..." -ForegroundColor Cyan
                    psql -U postgres -d gomums -f docs\DATABASE_SCHEMA.sql
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "✓ Schema migration completed" -ForegroundColor Green
                    } else {
                        Write-Host "✗ Schema migration failed" -ForegroundColor Red
                    }
                }
            }
        }
    }
} else {
    Write-Host "✗ PostgreSQL is not installed or not in PATH" -ForegroundColor Red
    Write-Host "  Please install PostgreSQL 14+ from: https://www.postgresql.org/download/" -ForegroundColor Yellow
}

# Start server
Write-Host "`n[7/7] Starting server..." -ForegroundColor Yellow
Write-Host @"

╔════════════════════════════════════════════════════════════╗
║                                                            ║
║                 🚀 Server Starting...                      ║
║                                                            ║
║  API Documentation: http://localhost:8000/docs             ║
║  Health Check:     http://localhost:8000/health            ║
║                                                            ║
║  Press Ctrl+C to stop the server                          ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

Write-Host "Starting in 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

python -m uvicorn app.main:app --reload --port 8000
