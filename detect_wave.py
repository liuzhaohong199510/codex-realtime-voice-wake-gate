"""Replay a local WAV file through the detector without recording or uploading."""

from __future__ import annotations

import argparse
from pathlib import Path

import vosk

from wake_gate.core import GateEvent, VoiceGate
from wake_gate.detector import KeywordDetectionSession
from wake_gate.live import keyword_grammar
from wake_gate.wave_input import iter_pcm16_mono


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("wave_file", type=Path)
    args = parser.parse_args()

    root = Path(__file__).parent
    model_path = root / "models" / "vosk-model-small-cn-0.22"
    vosk.SetLogLevel(-1)
    recognizer = vosk.KaldiRecognizer(
        vosk.Model(str(model_path)),
        16_000,
        keyword_grammar("小欧", "结束"),
    )
    gate = VoiceGate("小欧", "结束")
    session = KeywordDetectionSession(recognizer, gate)
    events: list[str] = []

    for chunk in iter_pcm16_mono(args.wave_file):
        result = session.process_pcm(chunk)
        if result is None:
            continue
        if result.event is GateEvent.OPENED:
            events.append("OPENED")
        elif result.event is GateEvent.CLOSED:
            events.append("CLOSED")

    final_result = session.finish()
    if final_result is not None:
        if final_result.event is GateEvent.OPENED:
            events.append("OPENED")
        elif final_result.event is GateEvent.CLOSED:
            events.append("CLOSED")

    print("EVENTS=" + ",".join(events))
    return 0 if events == ["OPENED", "CLOSED"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
