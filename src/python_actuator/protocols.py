# SPDX-FileCopyrightText: 2026 Bobrik Stepan
#
# SPDX-License-Identifier: MIT

"""Health check contracts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from python_actuator.models import HealthResult


class HealthIndicator(Protocol):
    """Contract for a component that reports health."""

    def health(self) -> HealthResult:
        """Return current component health."""
        ...
