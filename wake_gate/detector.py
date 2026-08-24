"""Streaming keyword-detection session with fail-closed behavior."""

from __future__ import annotations

from typing import Protocol

from .core import GateEvent, GateResult, VoiceGate
from .vosk_adapter import RecognitionKind, parse_vosk_result


class StreamingRecognizer(Protocol):
    def AcceptWaveform(self, data: bytes) -> bool: ...

    def Result(self) -> str: ...

    def PartialResult(self) -> str: ...

    def FinalResult(self) -> str: ...


class KeywordDetectionSession:
    def __init__(
        self,
        recognizer: StreamingRecognizer,
        gate: VoiceGate,
        *,
        min_confidence: float = 0.0,
        accept_partial: bool = False,
    ) -> None:
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError("min_confidence must be between 0 and 1")
        self._recognizer = recognizer
        self._gate = gate
        self._min_confidence = min_confidence
        self._accept_partial = accept_partial
        self._last_partial = ""

    def _handle_parsed(self, parsed) -> GateResult | None:
        if parsed.kind is RecognitionKind.ERROR:
            return self._gate.fail_safe("invalid recognizer response")
        if parsed.kind is RecognitionKind.EMPTY:
            return None
        if parsed.kind is RecognitionKind.PARTIAL and not self._accept_partial:
            return None
        if parsed.kind is RecognitionKind.FINAL and self._min_confidence > 0:
            if parsed.confidence is None or parsed.confidence < self._min_confidence:
                return None

        result = self._gate.handle_recognition(parsed.text)
        if result.event is GateEvent.NONE:
            return None
        return result

    def process_pcm(self, data: bytes) -> GateResult | None:
        if self._recognizer.AcceptWaveform(data):
            parsed = parse_vosk_result(self._recognizer.Result())
            self._last_partial = ""
        else:
            parsed = parse_vosk_result(self._recognizer.PartialResult())
            if parsed.kind is RecognitionKind.PARTIAL:
                if parsed.text == self._last_partial:
                    return None
                self._last_partial = parsed.text

        return self._handle_parsed(parsed)

    def finish(self) -> GateResult | None:
        parsed = parse_vosk_result(self._recognizer.FinalResult())
        self._last_partial = ""
        if parsed.kind is RecognitionKind.ERROR:
            return self._gate.fail_safe("invalid final recognizer response")
        return self._handle_parsed(parsed)
