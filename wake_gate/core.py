"""Privacy-preserving state and audio gating primitives."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re

import numpy as np


class GateState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"


class GateEvent(str, Enum):
    NONE = "none"
    OPENED = "opened"
    CLOSED = "closed"
    FAILED_SAFE = "failed_safe"


@dataclass(frozen=True)
class GateResult:
    event: GateEvent
    state: GateState
    forward_text: bool
    reason: str | None = None


def _normalize_phrase(value: str) -> str:
    """Remove separators so short Chinese control phrases match reliably."""
    return re.sub(r"[\s\W_]+", "", value, flags=re.UNICODE).casefold()


class VoiceGate:
    """Two-state gate that fails closed and never forwards control phrases."""

    def __init__(self, wake_phrase: str, stop_phrase: str) -> None:
        wake = _normalize_phrase(wake_phrase)
        stop = _normalize_phrase(stop_phrase)
        if not wake or not stop:
            raise ValueError("wake_phrase and stop_phrase must not be empty")
        if wake == stop:
            raise ValueError("wake_phrase and stop_phrase must differ")

        self._wake_phrase = wake
        self._stop_phrase = stop
        self._state = GateState.CLOSED

    @property
    def state(self) -> GateState:
        return self._state

    def handle_recognition(self, text: str) -> GateResult:
        normalized = _normalize_phrase(text)

        if normalized == self._wake_phrase and self._state is GateState.CLOSED:
            self._state = GateState.OPEN
            return GateResult(GateEvent.OPENED, self._state, False)

        if normalized == self._stop_phrase and self._state is GateState.OPEN:
            self._state = GateState.CLOSED
            return GateResult(GateEvent.CLOSED, self._state, False)

        if normalized in {self._wake_phrase, self._stop_phrase}:
            return GateResult(GateEvent.NONE, self._state, False)

        return GateResult(
            GateEvent.NONE,
            self._state,
            forward_text=self._state is GateState.OPEN and bool(normalized),
        )

    def fail_safe(self, reason: str) -> GateResult:
        self._state = GateState.CLOSED
        return GateResult(GateEvent.FAILED_SAFE, self._state, False, reason)

    def apply_audio(self, samples: np.ndarray) -> np.ndarray:
        if self._state is GateState.CLOSED:
            return np.zeros_like(samples)
        return samples.copy()
