"""Fixed-window in-memory capture for one human acceptance scenario."""

from __future__ import annotations

import math
from typing import Protocol

from .acceptance import AcceptanceObservation, AcceptanceScenario
from .core import GateEvent, VoiceGate
from .detector import KeywordDetectionSession, StreamingRecognizer


class BlockingInputStream(Protocol):
    def read(self, frames: int) -> tuple[object, bool]: ...


def capture_trial(
    scenario: AcceptanceScenario,
    stream: BlockingInputStream,
    recognizer: StreamingRecognizer,
    gate: VoiceGate,
    *,
    sample_rate: int = 16_000,
    blocksize: int = 4_000,
) -> AcceptanceObservation:
    initial_state = gate.state
    session = KeywordDetectionSession(recognizer, gate)
    events: list[GateEvent] = []
    failed = False
    chunk_count = max(
        1,
        math.ceil(scenario.duration_seconds * sample_rate / blocksize),
    )

    for _ in range(chunk_count):
        try:
            chunk, overflowed = stream.read(blocksize)
            if overflowed:
                result = gate.fail_safe("input overflow")
                failed = True
            else:
                result = session.process_pcm(bytes(chunk))
        except Exception as exc:
            result = gate.fail_safe(f"{type(exc).__name__}: {exc}")
            failed = True

        if result is not None and result.event is not GateEvent.NONE:
            events.append(result.event)
        if failed:
            break

    if not failed:
        try:
            final = session.finish()
        except Exception as exc:
            final = gate.fail_safe(f"{type(exc).__name__}: {exc}")
        if final is not None and final.event is not GateEvent.NONE:
            events.append(final.event)

    return AcceptanceObservation(
        scenario.scenario_id,
        initial_state,
        tuple(events),
        gate.state,
    )
