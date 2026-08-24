"""Fail-closed bridge from local keyword recognition to gated PCM audio."""

from __future__ import annotations

from .audio_delay_gate import DelayedAudioGate
from .core import GateEvent, GateState, VoiceGate
from .detector import KeywordDetectionSession, StreamingRecognizer


class LocalAudioRouter:
    """Process one PCM chunk at a time without opening any audio device."""

    def __init__(
        self,
        recognizer: StreamingRecognizer,
        *,
        wake_phrase: str = "小欧",
        stop_phrase: str = "结束",
        delay_chunks: int = 4,
        min_confidence: float = 0.65,
    ) -> None:
        self._gate = VoiceGate(wake_phrase, stop_phrase)
        self._session = KeywordDetectionSession(
            recognizer,
            self._gate,
            min_confidence=min_confidence,
            accept_partial=False,
        )
        self._audio_gate = DelayedAudioGate(delay_chunks)
        self._last_event = GateEvent.NONE
        self._failure_reason: str | None = None

    @property
    def state(self) -> GateState:
        return self._gate.state

    @property
    def last_event(self) -> GateEvent:
        return self._last_event

    @property
    def failure_reason(self) -> str | None:
        return self._failure_reason

    def process_chunk(self, chunk: bytes) -> bytes:
        event = GateEvent.NONE
        try:
            result = self._session.process_pcm(chunk)
            if result is not None:
                event = result.event
                self._failure_reason = result.reason
        except Exception as exc:
            result = self._gate.fail_safe(f"{type(exc).__name__}: {exc}")
            event = result.event
            self._failure_reason = result.reason

        self._last_event = event
        return self._audio_gate.process_chunk(chunk, event)
