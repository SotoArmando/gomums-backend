#!/bin/bash

# GoMums Backend Quick Start Script (Linux/WSL)
# This script helps you set up and run the backend on Linux/WSL

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║              🍳 GoMums Backend Setup (Linux/WSL)          ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Check if Python is installed
echo -e "\n[1/7] Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Python is installed: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✓ Python is installed: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "✗ Python is not installed. Please install Python 3.8+"
    echo "  Run: sudo apt update && sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

# Check if virtual environment exists
echo -e "\n[2/7] Checking virtual environment..."
if [ -d "venv" ]; then
    echo "✓ Virtual environment exists"
else
    echo "→ Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo -e "\n[3/7] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo -e "\n[4/7] Installing dependencies..."
pip install -r requirements.txt --quiet
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Check if .env exists
echo -e "\n[5/7] Checking environment configuration..."
if [ -f ".env" ]; then
    echo "✓ .env file exists"
else
    echo "→ Creating .env from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠ IMPORTANT: Edit .env and update DATABASE_PASSWORD and JWT secrets!"
    
    read -p "Do you want to edit .env now? (y/n): " edit_choice
    if [ "$edit_choice" == "y" ]; then
        ${EDITOR:-nano} .env
    fi
fi

# Check PostgreSQL connection
echo -e "\n[6/7] Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    PSQL_VERSION=$(psql --version)
    echo "✓ PostgreSQL is installed: $PSQL_VERSION"
    
    # Check if PostgreSQL is running
    if sudo service postgresql status > /dev/null 2>&1 || systemctl is-active --quiet postgresql; then
        echo "✓ PostgreSQL is running"
    else
        echo "→ Starting PostgreSQL..."
        sudo service postgresql start
    fi
    
    echo "→ Checking if 'gomums' database exists..."
    DB_EXISTS=$(sudo -u postgres psql -lqt | grep -w gomums | wc -l)
    
    if [ "$DB_EXISTS" -eq 1 ]; then
        echo "✓ Database 'gomums' exists"
    else
        echo "⚠ Database 'gomums' not found"
        read -p "Do you want to create it now? (y/n): " create_db
        
        if [ "$create_db" == "y" ]; then
            echo "→ Creating database..."
            sudo -u postgres psql -c "CREATE DATABASE gomums;"
            
            if [ $? -eq 0 ]; then
                echo "✓ Database created"
                
                read -p "Do you want to run the schema migration? (y/n): " run_schema
                if [ "$run_schema" == "y" ]; then
                    echo "→ Running schema migration..."
                    sudo -u postgres psql -d gomums -f docs/DATABASE_SCHEMA.sql
                    if [ $? -eq 0 ]; then
                        echo "✓ Schema migration completed"
                    else
                        echo "✗ Schema migration failed"
                    fi
                fi
            fi
        fi
    fi
else
    echo "✗ PostgreSQL is not installed or not in PATH"
    echo "  Please install PostgreSQL:"
    echo "  sudo apt update && sudo apt install postgresql postgresql-contrib"
fi

# Start server
echo -e "\n[7/7] Starting server..."
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║                 🚀 Server Starting...                      ║"
echo "║                                                            ║"
echo "║  API Documentation: http://localhost:8000/docs             ║"
echo "║  Health Check:     http://localhost:8000/health            ║"
echo "║                                                            ║"
echo "║  Press Ctrl+C to stop the server                          ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

sleep 2

$PYTHON_CMD -m uvicorn app.main:app --reload --port 8000
