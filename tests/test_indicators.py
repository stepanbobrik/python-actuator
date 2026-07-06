"""Tests for health indicator orchestration."""

from dataclasses import dataclass
from importlib import resources
from importlib.util import find_spec
from pathlib import Path
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


def test_health_endpoint_returns_component_health() -> None:
    """Endpoint can return health for a named component."""
    endpoint = HealthEndpoint(
        indicators={
            "broker": PassingIndicator(),
            "db": FailingIndicator(),
        },
    )

    result = endpoint.component_health("db")

    assert result == HealthResult(status=HealthStatus.DOWN)


def test_health_endpoint_returns_instance_health() -> None:
    """Endpoint can return health for a component instance."""
    endpoint = HealthEndpoint(indicators={"broker": BrokerIndicator()})

    result = endpoint.instance_health("broker", "us1")

    assert result == HealthResult(
        status=HealthStatus.UP,
        details={"version": "1.0.2"},
    )


def test_health_endpoint_returns_none_for_missing_instance() -> None:
    """Endpoint returns nothing for an unknown instance."""
    endpoint = HealthEndpoint(indicators={"broker": BrokerIndicator()})

    result = endpoint.instance_health("broker", "eu1")

    assert result is None


def test_package_contains_pep_561_marker() -> None:
    """Package exposes the PEP 561 marker file."""
    marker_file = resources.files("python_actuator").joinpath("py.typed")

    assert marker_file.is_file()


def test_package_is_imported_from_src_layout() -> None:
    """Package import resolves from the src layout."""
    package_spec = find_spec("python_actuator")
    expected_origin = (
        Path(__file__).resolve().parents[1] / "src" / "python_actuator" / "__init__.py"
    )

    assert package_spec is not None
    assert package_spec.origin == str(expected_origin)
