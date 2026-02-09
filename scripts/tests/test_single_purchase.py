import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:8000/api'

# Login
print("Logging in...")
response = requests.post(f'{BASE_URL}/auth/login', json={
    'email': 'master_test@gomums.com',
    'password': 'Test1234!'
})
token = response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
print(f"✅ Logged in")

# Create a simple purchase entry
print('\n📦 Creating purchase entry...')
purchase_data = {
    'type': 'purchase',
    'title': 'Test Groceries',
    'store': 'Test Store',
    'timestamp': datetime.now().isoformat(),
    'items': [{'name': 'Test Item', 'cost': 15.0, 'quantity': '1'}]
}

response = requests.post(f'{BASE_URL}/journal', json=purchase_data, headers=headers)
print(f'Response: {response.status_code}')
if response.status_code == 200 or response.status_code == 201:
    print(f'✅ Purchase created')
    print(json.dumps(response.json(), indent=2))
else:
    print(f'❌ Error: {response.text}')
