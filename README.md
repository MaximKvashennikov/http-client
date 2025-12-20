# 🚀 HTTP Client

**Modern HTTP client for Python with full type safety.** Built on `httpx` + `pydantic`.

## ✨ Features
- ✅ **Full type safety** with Pydantic v2
- 🔄 **Auto retry** with tenacity
- 🔐 **Bearer auth** included
- 📦 **Clean API** – simple methods

## ⚡ Quick Start

```python
from http_client import HttpClient
from http_client.models import Pet

# 1. Create client
client = HttpClient("https://petstore.swagger.io/v2")

# 2. Create model
pet = Pet(
    id=123,
    name="Fluffy",
    photo_urls=["photo.jpg"],
    status="available"
)

# 3. Make request
created = client.post(
    "/pet",
    request_model=pet,      # 📤 Send as JSON
    response_model=Pet,     # 📥 Validate response
    expected_status=200     # 🎯 Check status
)

print(f"Created: {created.name}")  # ✅ Typed response
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

client = HttpClient(
    base_url="https://api.example.com",
    auth_token="your-token",
    timeout=30.0
)

# GET with validation
user = client.get("/users/1", response_model=User)

# POST with data
result = client.post("/items", request_model=item)
```

### With Retry Logic
```python
from tenacity import retry, stop_after_attempt, wait_fixed

# Create retry strategy
retry_strategy = retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1)
)

# Use per-request retry
response = client.get(
    "/users/1",
    response_model=User,
    retry=retry_strategy  # 🔄 Apply only to this request
)

# Or different retry for another request
aggressive_retry = retry(stop=stop_after_attempt(5), wait=wait_fixed(0.5))
client.post("/data", request_model=data, retry=aggressive_retry)
```

## 🎯 API

| Method | Example |
|--------|---------|
| `GET` | `client.get("/users", response_model=List[User])` |
| `POST` | `client.post("/users", request_model=user)` |
| `PUT` | `client.put("/users/1", request_model=update)` |
| `PATCH` | `client.patch("/users/1", request_model=partial)` |
| `DELETE` | `client.delete("/users/1", expected_status=204)` |


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
## 🔗 Allure result
![img.png](allure_example.png)
## 🔧 Custom Models

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int
    name: str
    email: str = Field(alias="userEmail")  # 🔄 Auto convert
    roles: list[str] = []
    
    class Config:
        populate_by_name = True  # 🎯 Support aliases
```