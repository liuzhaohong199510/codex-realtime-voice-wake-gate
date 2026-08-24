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
    sample_rate: int


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
    hostapis: Iterable[Mapping[str, Any]] = (),
) -> RoutePreflightResult:
    hostapi_list = list(hostapis)
    candidates = [
        (
            RouteTarget(
                index=index,
                name=str(device.get("name", "")),
                sample_rate=sample_rate,
            ),
            int(device.get("hostapi", -1)),
            int(float(device.get("default_samplerate", sample_rate))),
        )
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
    if len(candidates) > 1 and hostapi_list:
        wasapi_candidates = [
            candidate
            for candidate in candidates
            if 0 <= candidate[1] < len(hostapi_list)
            and str(hostapi_list[candidate[1]].get("name", "")).casefold()
            == "windows wasapi"
        ]
        if len(wasapi_candidates) == 1:
            candidates = wasapi_candidates

    if len(candidates) != 1:
        return RoutePreflightResult(
            RouteStatus.AMBIGUOUS,
            None,
            f"Expected one CABLE Input playback endpoint, found {len(candidates)}.",
        )

    target = candidates[0][0]
    native_sample_rate = candidates[0][2]
    try:
        check_output_settings(
            device=target.index,
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
        )
    except Exception as exc:
        if native_sample_rate <= 0 or native_sample_rate == sample_rate:
            return RoutePreflightResult(
                RouteStatus.INCOMPATIBLE,
                None,
                f"{type(exc).__name__}: {exc}",
            )
        try:
            check_output_settings(
                device=target.index,
                samplerate=native_sample_rate,
                channels=1,
                dtype="int16",
            )
        except Exception as native_exc:
            return RoutePreflightResult(
                RouteStatus.INCOMPATIBLE,
                None,
                f"{type(native_exc).__name__}: {native_exc}",
            )
        target = RouteTarget(
            index=target.index,
            name=target.name,
            sample_rate=native_sample_rate,
        )

    return RoutePreflightResult(RouteStatus.READY, target)
