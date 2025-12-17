import urllib.request
import json

url = 'http://127.0.0.1:8000/api/v1/auth/register'
data = {
    'email': 'daffi@example.com',
    'name': 'Muhammad Daffi',
    'password': 'daffi12345'
}

json_data = json.dumps(data).encode('utf-8')
req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print(f'Status Code: {response.getcode()}')
        print(f'Response: {response.read().decode()}')
except Exception as e:
    print(f'Error: {e}')
