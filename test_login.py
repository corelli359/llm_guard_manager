import requests

url = "http://127.0.0.1:9001/api/v1/login/access-token"

data = {
    "username": "llm_guard",
    "password": "68-8CtBhug"
}

proxies = {
    "http": None,
    "https": None,
}

response = requests.post(url, data=data, proxies=proxies)

print(response.status_code)
print(response.json())