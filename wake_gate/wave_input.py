"""Read deterministic PCM input for offline keyword replay tests."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
import wave


def iter_pcm16_mono(path: Path, frames_per_chunk: int = 4_000) -> Iterator[bytes]:
    with wave.open(str(path), "rb") as source:
        if source.getnchannels() != 1:
            raise ValueError("wave input must be mono")
        if source.getsampwidth() != 2:
            raise ValueError("wave input must use 16-bit PCM")
        if source.getframerate() != 16_000:
            raise ValueError("wave input must use a 16000 Hz sample rate")

        while True:
            data = source.readframes(frames_per_chunk)
            if not data:
                return
            yield data
