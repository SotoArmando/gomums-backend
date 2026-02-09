# Authentication API Testing Guide

## 🧪 Test Your Authentication Endpoints

After starting your server, you can test the authentication endpoints using these methods:

### Method 1: Interactive API Docs (Recommended)

1. Start your server:
   ```powershell
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. Open http://localhost:8000/docs

3. Test the endpoints directly in your browser!

### Method 2: PowerShell (curl alternative)

#### 1. Register a New User

```powershell
$body = @{
    name = "Test User"
    email = "test@example.com"
    password = "testpass123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

# Save the token for later use
$token = $response.token
$refreshToken = $response.refresh_token

# Display response
$response | ConvertTo-Json -Depth 5
```

#### 2. Login

```powershell
$body = @{
    email = "test@example.com"
    password = "testpass123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

# Save the token
$token = $response.token
$refreshToken = $response.refresh_token

# Display response
$response | ConvertTo-Json -Depth 5
```

#### 3. Get Current User (Protected Route)

```powershell
$headers = @{
    "Authorization" = "Bearer $token"
}

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/me" `
    -Method GET `
    -Headers $headers

$response | ConvertTo-Json -Depth 5
```

#### 4. Refresh Token

```powershell
$body = @{
    refresh_token = $refreshToken
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/refresh" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

# Update tokens
$token = $response.access_token
$refreshToken = $response.refresh_token

$response | ConvertTo-Json -Depth 5
```

#### 5. Logout

```powershell
$headers = @{
    "Authorization" = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/logout" `
    -Method POST `
    -Headers $headers

Write-Host "Logged out successfully"
```

### Method 3: Python Script

Create a file `test_auth.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/auth"

# 1. Register
print("1. Testing Register...")
response = requests.post(f"{BASE_URL}/register", json={
    "name": "Test User",
    "email": "test@example.com",
    "password": "testpass123"
})
print(f"Status: {response.status_code}")
data = response.json()
print(json.dumps(data, indent=2))

token = data["token"]
refresh_token = data["refresh_token"]

# 2. Login
print("\n2. Testing Login...")
response = requests.post(f"{BASE_URL}/login", json={
    "email": "test@example.com",
    "password": "testpass123"
})
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

# 3. Get Current User
print("\n3. Testing Get Current User...")
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/me", headers=headers)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

# 4. Refresh Token
print("\n4. Testing Refresh Token...")
response = requests.post(f"{BASE_URL}/refresh", json={
    "refresh_token": refresh_token
})
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

# 5. Logout
print("\n5. Testing Logout...")
response = requests.post(f"{BASE_URL}/logout", headers=headers)
print(f"Status: {response.status_code}")
print("Logged out successfully" if response.status_code == 204 else "Logout failed")
```

Run it:
```powershell
python test_auth.py
```

## 📋 Expected Responses

### Register/Login Response (200/201)
```json
{
  "user": {
    "id": "uuid-here",
    "name": "Test User",
    "email": "test@example.com",
    "is_active": true,
    "is_premium": false,
    "created_at": "2026-02-07T10:00:00"
  },
  "token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "token_type": "bearer"
}
```

### Get Current User Response (200)
```json
{
  "id": "uuid-here",
  "name": "Test User",
  "email": "test@example.com",
  "is_active": true,
  "is_premium": false,
  "created_at": "2026-02-07T10:00:00"
}
```

### Common Error Responses

#### 400 - Email Already Registered
```json
{
  "detail": "Email already registered"
}
```

#### 401 - Invalid Credentials
```json
{
  "detail": "Invalid email or password"
}
```

#### 401 - Invalid Token
```json
{
  "detail": "Invalid or expired token"
}
```

#### 422 - Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## 🔍 Troubleshooting

### Error: Connection refused
- Make sure the server is running: `python -m uvicorn app.main:app --reload --port 8000`
- Check if port 8000 is available

### Error: Database connection failed
- Ensure PostgreSQL is running
- Verify `.env` database credentials
- Make sure `gomums` database exists

### Error: Email already registered
- The email is already in use
- Try a different email or delete the existing user from the database:
  ```sql
  DELETE FROM users WHERE email = 'test@example.com';
  ```

### Error: Import errors
- Make sure you're in the virtual environment: `.\venv\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`

## ✅ Success Checklist

- [ ] Server starts without errors
- [ ] Can access http://localhost:8000/docs
- [ ] Can register a new user
- [ ] Can login with credentials
- [ ] Can access `/api/auth/me` with token
- [ ] Can refresh token
- [ ] Can logout
- [ ] Proper error messages for invalid credentials
- [ ] Proper validation errors for bad input

Once all tests pass, you're ready to implement the next features (Journal, Budget, Recipes)!
