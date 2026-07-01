"""Health response models."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import final

type HealthDetailValue = str | int | float | bool | HealthDetails
type HealthDetails = dict[str, HealthDetailValue]


class HealthStatus(StrEnum):
    """Known Spring Boot health statuses."""

    UP = "UP"
    DOWN = "DOWN"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"
    UNKNOWN = "UNKNOWN"


@final
@dataclass(frozen=True, slots=True)
class HealthResult:
    """Spring Boot compatible health result."""

    status: HealthStatus
    details: HealthDetails = field(default_factory=dict)

    def to_response(self) -> HealthDetails:
        """Return a serializable actuator health payload."""
        response: HealthDetails = {"status": self.status.value}
        if self.details:
            response["details"] = self.details
        return response
