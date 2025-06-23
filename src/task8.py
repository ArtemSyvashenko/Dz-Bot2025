import time
import requests 
from datetime import datetime

class AuthProxy:
    def __init__(self, auth_type="api_key", token=""):
        self.auth_type = auth_type
        self.token = token

    def _get_headers(self):
        headers = {}
        if self.auth_type == "api_key":
            headers["X-API-Key"] = self.token
        elif self.auth_type == "jwt":
            headers["Authorization"] = f"Bearer {self.token}"
        elif self.auth_type == "basic":
            headers["Authorization"] = f"Basic {self.token}"
        return headers

    def get(self, url):
        headers = self._get_headers()
        response = requests.get(url, headers=headers)
        self._log_request("GET", url, response.status_code)
        return response

    def post(self, url, data=None):
        headers = self._get_headers()
        response = requests.post(url, headers=headers, json=data)
        self._log_request("POST", url, response.status_code)
        return response

    def _log_request(self, method, url, status_code):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {method} {url} → {status_code}")

if __name__ == "__main__":
    proxy = AuthProxy(auth_type="jwt", token="abc123")
    response = proxy.get("https://httpbin.org/get")
    print(response.json())
