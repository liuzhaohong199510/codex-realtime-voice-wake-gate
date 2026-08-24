"""Read-only VB-CABLE preflight. It never opens a stream or changes defaults."""

from __future__ import annotations

from collections.abc import Callable
import sys
from typing import Any

import sounddevice as sd

from wake_gate.audio_devices import console_safe
from wake_gate.route_preflight import RouteStatus, preflight_virtual_cable


def configure_utf8_output(stream: Any = sys.stdout) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")


def run_preflight(
    audio_api: Any = sd,
    emit: Callable[[str], object] = print,
) -> int:
    result = preflight_virtual_cable(
        audio_api.query_devices(),
        audio_api.check_output_settings,
        hostapis=audio_api.query_hostapis(),
    )

    if result.status is RouteStatus.READY:
        target = result.target
        assert target is not None
        name = console_safe(target.name, sys.stdout.encoding)
        emit(
            f"检查通过：将仅路由到 [{target.index}] {name} "
            f"@ {target.sample_rate} Hz。"
        )
        return 0

    emit(
        f"检查未通过（{result.status.value}）：{result.reason} "
        "不会启动音频路由。"
    )
    return 2


if __name__ == "__main__":
    configure_utf8_output()
    raise SystemExit(run_preflight())
