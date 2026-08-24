"""Run the stage-A keyword detector. No audio is saved or transmitted."""

from __future__ import annotations

import argparse
from pathlib import Path

from wake_gate.live import run_live_detector


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=int, default=None)
    parser.add_argument("--seconds", type=float, default=None)
    parser.add_argument("--min-confidence", type=float, default=0.65)
    args = parser.parse_args()
    model_path = Path(__file__).parent / "models" / "vosk-model-small-cn-0.22"
    return run_live_detector(
        model_path,
        device=args.device,
        duration_seconds=args.seconds,
        min_confidence=args.min_confidence,
    )


if __name__ == "__main__":
    raise SystemExit(main())
