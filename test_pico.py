import requests

url = "http://127.0.0.1:5000/scan"

data = {
    "tag": "103701245"
}

response = requests.post(url, json=data)

print("Status:", response.status_code)
print("Response:", response.json())

if response.status_code == 200:
    redirect_url = response.json()["redirect_url"]
    print("Open in browser:", "http://127.0.0.1:5000" + redirect_url)