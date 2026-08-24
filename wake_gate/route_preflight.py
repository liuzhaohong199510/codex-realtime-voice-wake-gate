"""Read-only checks for the dedicated VB-CABLE playback endpoint."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any


class RouteStatus(str, Enum):
    READY = "ready"
    MISSING = "missing"
    AMBIGUOUS = "ambiguous"
    INCOMPATIBLE = "incompatible"


@dataclass(frozen=True)
class RouteTarget:
    index: int
    name: str


@dataclass(frozen=True)
class RoutePreflightResult:
    status: RouteStatus
    target: RouteTarget | None
    reason: str | None = None


def preflight_virtual_cable(
    devices: Iterable[Mapping[str, Any]],
    check_output_settings: Callable[..., object],
    *,
    sample_rate: int = 16_000,
    name_fragment: str = "CABLE Input",
) -> RoutePreflightResult:
    candidates = [
        RouteTarget(index=index, name=str(device.get("name", "")))
        for index, device in enumerate(devices)
        if int(device.get("max_output_channels", 0)) > 0
        and name_fragment.casefold() in str(device.get("name", "")).casefold()
    ]

    if not candidates:
        return RoutePreflightResult(
            RouteStatus.MISSING,
            None,
            "Dedicated CABLE Input playback endpoint was not found.",
        )
    if len(candidates) != 1:
        return RoutePreflightResult(
            RouteStatus.AMBIGUOUS,
            None,
            f"Expected one CABLE Input playback endpoint, found {len(candidates)}.",
        )

    target = candidates[0]
    try:
        check_output_settings(
            device=target.index,
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
        )
    except Exception as exc:
        return RoutePreflightResult(
            RouteStatus.INCOMPATIBLE,
            None,
            f"{type(exc).__name__}: {exc}",
        )

    return RoutePreflightResult(RouteStatus.READY, target)
