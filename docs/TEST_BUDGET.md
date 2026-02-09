# Testing Budget API Endpoints

This document describes how to test the Budget API endpoints using the provided test script.

## Prerequisites

1. Ensure PostgreSQL is running with the `gomums` database
2. Virtual environment is activated
3. All dependencies are installed (from requirements.txt)
4. Backend server is running on port 8000

## Starting the Server

### On Linux/WSL:
```bash
source venv/bin/activate
python -m app.main
```

Or use the start script:
```bash
bash start.sh
```

### On Windows PowerShell:
```powershell
venv\Scripts\Activate.ps1
python -m app.main
```

Or use the start script:
```powershell
.\start.ps1
```

## Running the Test Script

Once the server is running, open a new terminal and run:

### On Linux/WSL:
```bash
source venv/bin/activate
python test_budget.py
```

### On Windows:
```powershell
venv\Scripts\Activate.ps1
python test_budget.py
```

## What the Test Script Does

The `test_budget.py` script performs comprehensive testing of all Budget API endpoints:

### 1. User Authentication
- Registers a test user (or skips if exists)
- Logs in to get an access token

### 2. Budget Settings
- Creates budget settings (weekly: $150, monthly: $600)
- Retrieves budget settings

### 3. Budget Entries
- Creates 5 sample budget entries with different meals, dates, and categories:
  - Spaghetti Bolognese (Dinner) - $12.50 for 4 servings
  - Chicken Stir Fry (Dinner) - $15.00 for 3 servings
  - Pancakes (Breakfast) - $6.00 for 6 servings
  - Tuna Sandwiches (Lunch) - $8.50 for 4 servings
  - Tacos (Dinner) - $18.00 for 5 servings

- Each entry includes:
  - Date
  - Meal name
  - Total cost
  - Number of servings
  - Category (Breakfast/Lunch/Dinner)
  - Notes
  - Auto-calculated cost per serving

### 4. Retrieve Entries
- Gets all budget entries
- Filters entries by category (Dinner)

### 5. Budget Statistics
- Retrieves weekly budget stats including:
  - Budget Score (0-100)
  - Average cost per meal
  - Savings vs restaurant eating
  - Number of meals this week
  - Total spent
  - Weekly budget limit
  - Remaining budget

### 6. Category Breakdown
- Gets spending breakdown by category
- Shows total spent per category
- Calculates overall total

### 7. Update Operations
- Updates a budget entry (modifies cost and notes)

### 8. Delete Operations
- Deletes a budget entry

### 9. Final Verification
- Retrieves all entries again to confirm changes

## Expected Output

The test script uses colored output:
- 🟢 Green checkmarks (✓) for successful operations
- 🔴 Red X marks (✗) for failures
- 🟡 Yellow info (ℹ) for informational messages
- 🔵 Blue headers for section titles

Example successful output:
```
============================================================
GoMums Budget API - Test Script
============================================================

ℹ Testing API at: http://localhost:8000

============================================================
1. User Registration
============================================================

ℹ User already exists, skipping registration

============================================================
2. User Login
============================================================

✓ Login successful
ℹ Access token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

============================================================
3. Create Budget Settings
============================================================

✓ Budget settings created successfully
Status: 201
Response: {
  "id": "...",
  "user_id": "...",
  "weekly_budget": 150.0,
  "monthly_budget": 600.0,
  "created_at": "...",
  "updated_at": "..."
}

... (continues with all endpoints)

============================================================
Test Summary
============================================================

✅ All budget API endpoints tested successfully!
ℹ Total entries remaining: 4
ℹ API Documentation: http://localhost:8000/docs
```

## Manual Testing with API Documentation

Alternatively, you can test the endpoints manually using the interactive API documentation:

1. Start the server
2. Open your browser to: http://localhost:8000/docs
3. Navigate to the "Budget" section
4. Click on any endpoint to expand it
5. Click "Try it out"
6. Fill in the required parameters
7. Click "Execute"

### Authentication for Manual Testing

1. First, use the `/api/auth/login` endpoint to get a token
2. Click the "Authorize" button at the top right
3. Enter: `Bearer YOUR_ACCESS_TOKEN`
4. Click "Authorize"
5. Now all requests will be authenticated

## Budget API Endpoints

### Settings
- **POST /api/budget/settings** - Create or update budget settings
- **GET /api/budget/settings** - Get current budget settings

### Entries
- **GET /api/budget/entries** - Get all budget entries (with optional filters)
  - Query params: `from_date`, `to_date`, `category`, `limit`, `offset`
- **GET /api/budget/entries/{entry_id}** - Get a specific entry
- **POST /api/budget/entries** - Create a new budget entry
- **PATCH /api/budget/entries/{entry_id}** - Update an entry
- **DELETE /api/budget/entries/{entry_id}** - Delete an entry

### Statistics
- **GET /api/budget/stats** - Get budget statistics
  - Query param: `period` (week/month/year)
- **GET /api/budget/category-breakdown** - Get spending by category
  - Query param: `period` (week/month/year)

## Troubleshooting

### Server Not Running
```
❌ Cannot connect to the API server
ℹ Make sure the server is running at http://localhost:8000
```
**Solution:** Start the server with `python -m app.main`

### Database Connection Error
```
✗ Database connection failed
```
**Solution:** 
- Check if PostgreSQL is running
- Verify .env file has correct credentials
- Ensure `gomums` database exists

### Authentication Failed
```
✗ Login failed
```
**Solution:**
- Ensure the test user exists (run registration first)
- Check credentials in test script match a valid user

### Module Not Found Error
```
ModuleNotFoundError: No module named 'requests'
```
**Solution:**
- Activate virtual environment
- Install dependencies: `pip install -r requirements.txt`

## Database Schema Note

The Budget API uses these database tables:
- `budget_entries` - Stores meal budget entries with calculated cost_per_serving
- `budget_settings` - Stores user budget goals (weekly/monthly)

Ensure your database schema is up to date by running the migrations or SQL schema file.

## Next Steps

After confirming the Budget API works:
1. Test integration with Journal entries (linking budget entries to journal entries)
2. Test budget calculations with different spending patterns
3. Verify budget notifications when approaching limits
4. Test category filtering and reporting
