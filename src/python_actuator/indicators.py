# SPDX-FileCopyrightText: 2026 Bobrik Stepan
#
# SPDX-License-Identifier: MIT

"""Health indicator orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from python_actuator.asgi import HealthASGIApp
from python_actuator.models import HealthDetails, HealthResult, HealthStatus

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from python_actuator.protocols import HealthIndicator

_UNHEALTHY_STATUSES = frozenset(
    (
        HealthStatus.DOWN,
        HealthStatus.OUT_OF_SERVICE,
    ),
)


@final
@dataclass(frozen=True, slots=True)
class HealthEndpoint:
    """Aggregates several health indicators into one health response."""

    indicators: Mapping[str, HealthIndicator]

    def health(self) -> HealthResult:
        """Return overall health for all configured indicators."""
        components = {
            name: indicator.health() for name, indicator in self.indicators.items()
        }
        return HealthResult(
            status=_overall_status(components.values()),
            details=_component_details(components),
        )

    def component_health(self, component: str) -> HealthResult | None:
        """Return health for a named component."""
        indicator = self.indicators.get(component)
        if indicator is None:
            return None
        return indicator.health()

    def instance_health(self, component: str, instance: str) -> HealthResult | None:
        """Return health for a named component instance."""
        component_result = self.component_health(component)
        if component_result is None:
            return None
        return _instance_health(component_result, instance)

    def asgi_app(self, path: str = "/actuator/health") -> HealthASGIApp:
        """Expose the endpoint through an ASGI-compatible application."""
        return HealthASGIApp(endpoint=self, path=path)


def _overall_status(health_checks: Iterable[HealthResult]) -> HealthStatus:
    for health_check in health_checks:
        if health_check.status in _UNHEALTHY_STATUSES:
            return health_check.status
    return HealthStatus.UP


def _component_details(
    components: dict[str, HealthResult],
) -> HealthDetails:
    return {
        name: health_check.to_response() for name, health_check in components.items()
    }


def _instance_health(
    component_result: HealthResult,
    instance: str,
) -> HealthResult | None:
    instance_payload = component_result.details.get(instance)
    if not isinstance(instance_payload, dict):
        return None
    return _health_result_from_payload(instance_payload)


def _health_result_from_payload(
    payload: dict[str, HealthDetails | str | int | float | bool],
) -> HealthResult | None:
    status_value = payload.get("status")
    if not isinstance(status_value, str):
        return None

    details_value = payload.get("details", {})
    if not isinstance(details_value, dict):
        return None

    try:
        status = HealthStatus(status_value)
    except ValueError:
        return None

    return HealthResult(status=status, details=details_value)
