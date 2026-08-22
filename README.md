<!--
SPDX-FileCopyrightText: 2026 Bobrik Stepan
SPDX-License-Identifier: MIT
-->

# Python Actuator

Small, typed health checks for Python ASGI applications, inspired by the
Spring Boot Actuator health API.

## Installation

```bash
pip install python-actuator
```

## Quick start

Create a health indicator for each component you want to monitor:

```python
from python_actuator.indicators import HealthEndpoint
from python_actuator.models import HealthResult, HealthStatus


class DatabaseHealth:
    def health(self) -> HealthResult:
        return HealthResult(status=HealthStatus.UP)


health_endpoint = HealthEndpoint(
    indicators={"database": DatabaseHealth()},
)
app = health_endpoint.asgi_app()
```

The ASGI application exposes:

- `GET /actuator/health` for the overall application status;
- `GET /actuator/health/{component}` for one component;
- `GET /actuator/health/{component}/{instance}` for a component instance;
- `HEAD` requests for the same routes.

Healthy responses use HTTP `200`. `DOWN` and `OUT_OF_SERVICE` responses use
HTTP `503`.

## Health results

Health results can include additional details:

```python
HealthResult(
    status=HealthStatus.UP,
    details={"message": "Database connection is ready"},
)
```

The response follows the Spring Boot Actuator shape:

```json
{
  "status": "UP",
  "details": {
    "message": "Database connection is ready"
  }
}
```

## Development

The project uses `uv`, `pytest`, Ruff, `mypy`, and `ty`:

```bash
make test
make check
```

## License

MIT
