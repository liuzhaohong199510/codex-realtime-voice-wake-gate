"""List readable microphone devices without opening or recording from them."""

from __future__ import annotations

import sys

import sounddevice as sd

from wake_gate.audio_devices import console_safe, input_devices


def main() -> int:
    devices = input_devices(sd.query_devices())
    default_input = sd.default.device[0]
    print(f"Default input index: {default_input}")
    if not devices:
        print("No readable microphone devices were found.")
        return 1

    for index, device in enumerate(sd.query_devices()):
        if int(device.get("max_input_channels", 0)) <= 0:
            continue
        marker = "*" if index == default_input else " "
        name = console_safe(str(device["name"]), sys.stdout.encoding)
        print(
            f"{marker} [{index}] {name} | "
            f"inputs={device['max_input_channels']} | "
            f"rate={int(device['default_samplerate'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
