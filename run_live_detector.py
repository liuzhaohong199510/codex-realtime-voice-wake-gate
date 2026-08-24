"""Run the stage-A keyword detector. No audio is saved or transmitted."""

from __future__ import annotations

import argparse
from pathlib import Path

from wake_gate.live import run_live_detector


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=int, default=None)
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
    return run_live_detector(
        args.model,
        keywords_file=args.keywords_file,
        device=args.device,
        duration_seconds=args.seconds,
    )


if __name__ == "__main__":
    raise SystemExit(main())
