"""Small, dependency-free boundary around Vosk JSON responses."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json


class RecognitionKind(str, Enum):
    EMPTY = "empty"
    PARTIAL = "partial"
    FINAL = "final"
    ERROR = "error"


@dataclass(frozen=True)
class RecognitionResult:
    kind: RecognitionKind
    text: str


def _clean_text(value: object) -> str:
    return " ".join(str(value).replace("[unk]", " ").split())


def parse_vosk_result(payload: str) -> RecognitionResult:
    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return RecognitionResult(RecognitionKind.ERROR, "")

    final_text = _clean_text(data.get("text", ""))
    if final_text:
        return RecognitionResult(RecognitionKind.FINAL, final_text)

    partial_text = _clean_text(data.get("partial", ""))
    if partial_text:
        return RecognitionResult(RecognitionKind.PARTIAL, partial_text)

    return RecognitionResult(RecognitionKind.EMPTY, "")
