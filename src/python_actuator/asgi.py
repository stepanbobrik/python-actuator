# SPDX-FileCopyrightText: 2026 Bobrik Stepan
#
# SPDX-License-Identifier: MIT

"""ASGI adapter for the health endpoint."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol, final

from python_actuator.models import HealthResult, HealthStatus

if TYPE_CHECKING:

    class HealthEndpointLike(Protocol):
        """Contract required by the ASGI health adapter."""

        def health(self) -> HealthResult:
            """Return overall application health."""

        def component_health(self, component: str) -> HealthResult | None:
            """Return health for a named component."""

        def instance_health(
            self,
            component: str,
            instance: str,
        ) -> HealthResult | None:
            """Return health for a named component instance."""


# ASGI integration uses framework-defined dynamic message shapes.
type ASGIMessage = dict[str, object]
type ASGIReceive = Callable[[], Awaitable[ASGIMessage]]
type ASGIScope = dict[str, object]
type ASGISend = Callable[[ASGIMessage], Awaitable[None]]

_HTTP_SCOPE_TYPE = "http"
_GET_METHOD = "GET"
_HEAD_METHOD = "HEAD"
_ALLOWED_METHODS = frozenset((_GET_METHOD, _HEAD_METHOD))
_METHOD_NOT_ALLOWED_STATUS = 405
_NOT_FOUND_STATUS = 404
_SERVICE_UNAVAILABLE_STATUS = 503
_OK_STATUS = 200
_HEADERS = (
    (b"content-type", b"application/vnd.spring-boot.actuator.v2+json;charset=utf-8"),
)
_METHOD_NOT_ALLOWED_HEADERS = (*_HEADERS, (b"allow", b"GET, HEAD"))
_COMPONENT_ROUTE_PARTS = 1
_INSTANCE_ROUTE_PARTS = 2
_UNSUPPORTED_SCOPE_MESSAGE = "ASGI scope type must be http"


@final
@dataclass(frozen=True, slots=True)
class HealthASGIApp:
    """Expose health information as an ASGI application."""

    endpoint: HealthEndpointLike
    path: str = field(default="/actuator/health")

    async def __call__(
        self,
        scope: ASGIScope,
        _receive: ASGIReceive,
        send: ASGISend,
    ) -> None:
        """Handle an ASGI HTTP request."""
        if _scope_text(scope, "type") != _HTTP_SCOPE_TYPE:
            message = _UNSUPPORTED_SCOPE_MESSAGE
            raise ValueError(message)

        method = _scope_text(scope, "method")
        if method not in _ALLOWED_METHODS:
            await _send_json(
                send=send,
                status=_METHOD_NOT_ALLOWED_STATUS,
                payload={"error": "Method Not Allowed"},
                head_only=method == _HEAD_METHOD,
                headers=_METHOD_NOT_ALLOWED_HEADERS,
            )
            return

        health_result = self._route(_scope_text(scope, "path"))
        if health_result is None:
            await _send_json(
                send=send,
                status=_NOT_FOUND_STATUS,
                payload={"error": "Not Found"},
                head_only=method == _HEAD_METHOD,
                headers=_HEADERS,
            )
            return

        await _send_json(
            send=send,
            status=_http_status(health_result.status),
            payload=health_result.to_response(),
            head_only=method == _HEAD_METHOD,
            headers=_HEADERS,
        )

    def _route(self, path: str) -> HealthResult | None:
        normalized_base_path = _normalize_path(self.path)
        normalized_path = _normalize_path(path)

        if normalized_path == normalized_base_path:
            return self.endpoint.health()

        route_prefix = f"{normalized_base_path}/"
        if not normalized_path.startswith(route_prefix):
            return None

        route_tail = normalized_path.removeprefix(route_prefix)
        route_parts = route_tail.split("/")

        if len(route_parts) == _COMPONENT_ROUTE_PARTS:
            return self.endpoint.component_health(route_parts[0])
        if len(route_parts) == _INSTANCE_ROUTE_PARTS:
            return self.endpoint.instance_health(route_parts[0], route_parts[1])
        return None


def _scope_text(scope: ASGIScope, key: str) -> str:
    scope_value = scope.get(key)
    if isinstance(scope_value, str):
        return scope_value
    return ""


def _normalize_path(path: str) -> str:
    if path == "/":
        return path
    return path.rstrip("/")


def _http_status(status: HealthStatus) -> int:
    if status in {HealthStatus.DOWN, HealthStatus.OUT_OF_SERVICE}:
        return _SERVICE_UNAVAILABLE_STATUS
    return _OK_STATUS


async def _send_json(
    send: ASGISend,
    status: int,
    payload: Mapping[str, object],
    *,
    head_only: bool,
    headers: tuple[tuple[bytes, bytes], ...],
) -> None:
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": list(headers),
        },
    )
    await send(
        {
            "type": "http.response.body",
            "body": b"" if head_only else json.dumps(payload).encode(),
        },
    )
