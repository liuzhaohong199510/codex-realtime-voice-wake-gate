"""Run the local wake-word gate and route allowed speech to VB-CABLE."""

from __future__ import annotations

import argparse
from pathlib import Path

from wake_gate.live_bridge import run_virtual_cable_bridge


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-device", type=int, default=None)
    parser.add_argument("--seconds", type=float, default=None)
    parser.add_argument(
        "--model",
        type=Path,
        default=(
            Path(__file__).parent
            / "models"
            / "sherpa-onnx-kws-zipformer-zh-en-3M-2025-12-20"
        ),
    )
    parser.add_argument(
        "--keywords-file",
        type=Path,
        default=Path(__file__).parent / "config" / "keywords.txt",
    )
    args = parser.parse_args()
    return run_virtual_cable_bridge(
        args.model,
        keywords_file=args.keywords_file,
        input_device=args.input_device,
        duration_seconds=args.seconds,
    )


if __name__ == "__main__":
    raise SystemExit(main())
