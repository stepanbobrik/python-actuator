"""Tests for health indicator orchestration."""

from dataclasses import dataclass
from typing import final

from python_actuator.indicators import HealthEndpoint
from python_actuator.models import HealthResult, HealthStatus


@final
@dataclass(frozen=True, slots=True)
class PassingIndicator:
    """Health indicator used by tests."""

    def health(self) -> HealthResult:
        """Return healthy status."""
        return HealthResult(
            status=HealthStatus.UP,
            details={"version": "1.0.2"},
        )


@final
@dataclass(frozen=True, slots=True)
class FailingIndicator:
    """Health indicator used by tests."""

    def health(self) -> HealthResult:
        """Return unhealthy status."""
        return HealthResult(status=HealthStatus.DOWN)


def test_health_endpoint_returns_component_details() -> None:
    """Endpoint returns details keyed by component name."""
    endpoint = HealthEndpoint(indicators={"broker": PassingIndicator()})

    result = endpoint.health()

    assert result.to_response() == {
        "status": "UP",
        "details": {
            "broker": {
                "status": "UP",
                "details": {"version": "1.0.2"},
            },
        },
    }


def test_health_endpoint_returns_down_when_component_is_down() -> None:
    """Endpoint returns down when any component is down."""
    endpoint = HealthEndpoint(
        indicators={
            "broker": PassingIndicator(),
            "db": FailingIndicator(),
        },
    )

    result = endpoint.health()

    assert result.status is HealthStatus.DOWN
