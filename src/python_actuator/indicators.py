"""Health indicator orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

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


def _overall_status(health_checks: Iterable[HealthResult]) -> HealthStatus:
    for health_check in health_checks:
        if health_check.status in _UNHEALTHY_STATUSES:
            return health_check.status
    return HealthStatus.UP


def _component_details(
    components: Mapping[str, HealthResult],
) -> HealthDetails:
    return {
        name: health_check.to_response() for name, health_check in components.items()
    }
