# 🚀 HTTP Client

**HTTP-клиент для Python с полной поддержкой типов.** 
Построен на основе `httpx`.

## Возможности
- Повторные попытки через tenacity
- Bearer auth аутентификация
- Гибкая система обработчиков запросов (event hooks). Реализованы AllureHandler, CurlHandler, LoggingHandler
- Отправка запросов от разных пользователей
- Поддержка контекстного менеджера для автоматического управления соединением

## Внесение изменений
1. Создать МР, поднять версию пакета в **pyproject.toml**
2. Получить апрув от лида QA
3. После влития в main лид создает тег с версией как в **pyproject.toml**
4. Запускает build пакета

## 📦 Установка

```bash
pip install pt-http-client
```

## 🔧 Использование

### Простое использование
```python
from pt_http_client import HttpClient

with HttpClient(base_url="https://api.example.com") as client:
    response = client.get("/users/1")
    data = response.json()
```

### С аутентификацией
```python
from pt_http_client.auth.bearer import BearerTokenAuth

auth = BearerTokenAuth(
    token_url="https://api.example.com/oauth/token",
    client_id="your-client-id",
    client_secret="your-client-secret",
    username="user@example.com",
    password="password",
    scope="api"
)

with HttpClient(
    base_url="https://api.example.com",
    auth=auth
) as client:
    response = client.get("/protected/resource")
```

### Временное переключение пользователя
```python
with auth.switch_to_user("other_user", "other_password"):
    # Запросы выполняются от другого пользователя
    response = client.get("/user/data")
```

### Повторные попытки
```python
from tenacity import retry, stop_after_attempt, wait_fixed

retry_decorator = retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1)
)

with HttpClient(base_url="https://api.example.com") as client:
    response = client.get(
        "/unstable/endpoint",
        retry=retry_decorator
    )
```