"""Tests for the ASGI health application."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import final

from python_actuator.indicators import HealthEndpoint
from python_actuator.models import HealthResult, HealthStatus


@final
@dataclass(frozen=True, slots=True)
class DatabaseIndicator:
    """Health indicator used by ASGI tests."""

    def health(self) -> HealthResult:
        """Return database status."""
        return HealthResult(
            status=HealthStatus.DOWN,
            details={"database": "offline"},
        )


@final
@dataclass(frozen=True, slots=True)
class BrokerIndicator:
    """Health indicator with multiple broker instances."""

    def health(self) -> HealthResult:
        """Return health for several broker instances."""
        return HealthResult(
            status=HealthStatus.UP,
            details={
                "us1": {
                    "status": "UP",
                    "details": {"version": "1.0.2"},
                },
                "us2": {
                    "status": "UP",
                    "details": {"version": "1.0.4"},
                },
            },
        )


@final
@dataclass(frozen=True, slots=True)
class ASGIResponse:
    """Collected ASGI response data."""

    status: int
    body: dict[str, object]


def test_asgi_app_returns_application_health() -> None:
    """ASGI app exposes the overall health route."""
    endpoint = HealthEndpoint(
        indicators={
            "db": DatabaseIndicator(),
            "broker": BrokerIndicator(),
        },
    )

    response = asyncio.run(_request(endpoint, "/actuator/health"))

    assert response == ASGIResponse(
        status=503,
        body={
            "status": "DOWN",
            "details": {
                "db": {
                    "status": "DOWN",
                    "details": {"database": "offline"},
                },
                "broker": {
                    "status": "UP",
                    "details": {
                        "us1": {
                            "status": "UP",
                            "details": {"version": "1.0.2"},
                        },
                        "us2": {
                            "status": "UP",
                            "details": {"version": "1.0.4"},
                        },
                    },
                },
            },
        },
    )


def test_asgi_app_returns_component_health() -> None:
    """ASGI app exposes a component health route."""
    endpoint = HealthEndpoint(indicators={"db": DatabaseIndicator()})

    response = asyncio.run(_request(endpoint, "/actuator/health/db"))

    assert response == ASGIResponse(
        status=503,
        body={
            "status": "DOWN",
            "details": {"database": "offline"},
        },
    )


def test_asgi_app_returns_instance_health() -> None:
    """ASGI app exposes an instance health route."""
    endpoint = HealthEndpoint(indicators={"broker": BrokerIndicator()})

    response = asyncio.run(_request(endpoint, "/actuator/health/broker/us1"))

    assert response == ASGIResponse(
        status=200,
        body={
            "status": "UP",
            "details": {"version": "1.0.2"},
        },
    )


def test_asgi_app_returns_not_found_for_unknown_component() -> None:
    """ASGI app returns 404 for an unknown component."""
    endpoint = HealthEndpoint(indicators={"db": DatabaseIndicator()})

    response = asyncio.run(_request(endpoint, "/actuator/health/broker"))

    assert response == ASGIResponse(
        status=404,
        body={"error": "Not Found"},
    )


async def _request(endpoint: HealthEndpoint, path: str) -> ASGIResponse:
    messages: list[dict[str, object]] = []
    app = endpoint.asgi_app()

    async def receive() -> dict[str, object]:
        return {
            "type": "http.request",
            "body": b"",
            "more_body": False,
        }

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    await app(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "headers": [],
        },
        receive,
        send,
    )

    status_value = messages[0]["status"]
    body_value = messages[1]["body"]

    assert isinstance(status_value, int)
    assert isinstance(body_value, bytes)

    return ASGIResponse(
        status=status_value,
        body=json.loads(body_value),
    )
