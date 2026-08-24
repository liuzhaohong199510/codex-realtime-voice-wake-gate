"""Fixed-latency audio gate that keeps control phrases out of downstream audio."""

from __future__ import annotations

from collections import deque

from .core import GateEvent


class DelayedAudioGate:
    def __init__(self, delay_chunks: int) -> None:
        if delay_chunks < 0:
            raise ValueError("delay_chunks must not be negative")
        self._delay_chunks = delay_chunks
        self._buffer: deque[bytes] = deque()
        self._open = False

    @property
    def buffered_chunks(self) -> int:
        return len(self._buffer)

    def process_chunk(self, chunk: bytes, event: GateEvent = GateEvent.NONE) -> bytes:
        silence = bytes(len(chunk))

        if event is GateEvent.OPENED:
            self._buffer.clear()
            self._open = True
            return silence

        if event in {GateEvent.CLOSED, GateEvent.FAILED_SAFE}:
            self._buffer.clear()
            self._open = False
            return silence

        if not self._open:
            return silence

        self._buffer.append(bytes(chunk))
        if len(self._buffer) <= self._delay_chunks:
            return silence
        return self._buffer.popleft()
