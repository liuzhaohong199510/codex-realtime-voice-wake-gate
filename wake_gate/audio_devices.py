"""Audio-device discovery without changing Windows defaults."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def console_safe(value: str, encoding: str | None) -> str:
    target_encoding = encoding or "utf-8"
    return value.encode(target_encoding, errors="replace").decode(target_encoding)


def input_devices(devices: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        dict(device)
        for device in devices
        if int(device.get("max_input_channels", 0)) > 0
    ]
