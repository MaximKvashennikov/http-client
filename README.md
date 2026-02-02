# 🚀 HTTP Client

**Modern HTTP client for Python with full type safety.** Built on `httpx`.

## ✨ Features
- 🔄 **Auto retry** with tenacity
- 🔐 **Bearer auth** included
- 📦 **Clean API** – simple methods

## ⚡ Quick Start

```python
from http_client import HttpClient

client = HttpClient(
    base_url="https://api.example.com",
    timeout=30.0
)

# Простой GET запрос
response = client.get("/users/1")
user_data = response.json()

# POST запрос с JSON
response = client.post(
    "/items",
    json={"name": "New Item", "price": 100}
)
```

## 📦 Installation

```bash

pip install httpx pydantic tenacity allure-pytest curlify2

# Clone repo and use
```

## 🔧 Usage

### Basic Client
```python
from http_client import HttpClient

# 1. Создаем клиент
client = HttpClient("https://jsonplaceholder.typicode.com")

# 2. Делаем запросы
response = client.get("/posts/1")
data = response.json()
print(f"Post title: {data['title']}")

# 3. POST запрос с данными
new_post = client.post(
    "/posts",
    json={
        "title": "foo",
        "body": "bar",
        "userId": 1
    }
)
print(f"Created post ID: {new_post.json()['id']}")

# 4. Запрос с кастомными заголовками
response = client.get(
    "/users/1",
    headers={
        "Authorization": "Bearer token123",
        "X-Custom-Header": "value"
    }
)
```

### With Retry Logic
```python
from tenacity import retry, stop_after_attempt, wait_fixed

# Создаем стратегию retry
retry_strategy = retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1)
)

# Используем retry в конкретном запросе
response = client.get(
    "/unstable-endpoint",
    retry=retry_strategy  # 🔄 Применяется только к этому запросу
)

# Другая стратегия для другого запроса
aggressive_retry = retry(
    stop=stop_after_attempt(5), 
    wait=wait_fixed(0.5)
)
response = client.post(
    "/critical-data",
    json=data,
    retry=aggressive_retry
)
```

## 🔧 Authentication

### Basic Auth
``` python
import httpx

client = HttpClient(
    base_url="https://httpbin.org",
    auth=httpx.BasicAuth("user", "pass")  # 🔐 Basic authentication
)

# All requests will include Basic auth headers
response = client.get("/basic-auth/user/pass")
``` 

### Bearer Token Auth
``` python
client = HttpClient(
    base_url="https://api.example.com",
    auth=httpx.BearerToken("your-token-here")
)
```
### Custom Auth

``` python
# Custom auth class
class CustomAuth(httpx.Auth):
    def auth_flow(self, request):
        request.headers["X-API-Key"] = "your-api-key"
        yield request

client = HttpClient(
    base_url="https://api.example.com",
    auth=CustomAuth()  # 🛠️ Custom authentication
)
```

### Per-Request Auth
``` python
# Override auth for specific request
response = client.get(
    "/admin/data",
    auth=httpx.BasicAuth("admin", "admin123")  # 🎯 Different auth for this request
)
```
## 🎭 Event Handlers
📋 Overview
Event handlers allow you to intercept HTTP requests and responses for logging, debugging, or attaching data to reports. The client supports multiple handlers that work together.

### Create client with logging
``` python
client = HttpClient(
    base_url="https://api.example.com",
    handlers=[LoggingHandler()]
)
```
All requests will be logged with INFO level
Errors (status >= 300) include headers and body
Success responses log basic info only
### Curl Command Handler
``` python
from src.clients.http_client.core.event_hooks.curl_handler import CurlHandler

client = HttpClient(
    base_url="https://api.example.com",
    handlers=[CurlHandler()]
)
```
Each request will generate equivalent curl command
Useful for debugging and reproducing requests
### Allure Report Handler
``` python
from src.clients.http_client.core.event_hooks.allure_handler import AllureHandler

client = HttpClient(
    base_url="https://api.example.com",
    handlers=[AllureHandler()]
)
```
Automatically attaches request/response data to Allure reports
Great for test automation and CI/CD pipelines
### 🎯 Using Multiple Handlers
``` python
from src.clients.http_client import HttpClient
from src.clients.http_client.core.event_hooks import (
    LoggingHandler,
    CurlHandler,
    AllureHandler
)

client = HttpClient(
    base_url="https://api.example.com",
    handlers=[
        LoggingHandler(),    # 📝 Console logs
        CurlHandler(),       # 🔗 Curl commands for debugging
        AllureHandler()      # 📊 Allure report attachments
    ]
)

# All handlers will process each request/response
response = client.get("/data")
```
### ➕ Adding Handlers Dynamically
``` python
client = HttpClient(base_url="https://api.example.com")

# Add handlers after client creation
client.add_handler(LoggingHandler())
client.add_handler(CurlHandler())

# Now requests will use all added handlers
response = client.post("/submit", json={"data": "test"})
```
### ✨ Custom Handlers
Create your own handler by extending AbstractHookHandler:

``` python
from src.clients.http_client.core.event_hooks.abstract_hook_handler import AbstractHookHandler
import httpx

class MetricsHandler(AbstractHookHandler):
    """Custom handler for collecting request metrics."""
    
    @staticmethod
    def request_hook(request: httpx.Request) -> None:
        # Track request start time
        request.context["start_time"] = time.time()
    
    @staticmethod
    def response_hook(response: httpx.Response) -> None:
        # Calculate and log response time
        elapsed = time.time() - response.request.context["start_time"]
        print(f"Request took {elapsed:.2f}s")

# Use custom handler
client = HttpClient(
    base_url="https://api.example.com",
    handlers=[MetricsHandler()]
)
```
