"""Privacy-minimal adapter from sherpa-onnx KWS to the gate recognizer API."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class SherpaModelFiles:
    tokens: Path
    encoder: Path
    decoder: Path
    joiner: Path


def resolve_model_files(model_dir: Path) -> SherpaModelFiles:
    names = {
        "tokens": "tokens.txt",
        "encoder": "encoder-epoch-13-avg-2-chunk-16-left-64.int8.onnx",
        "decoder": "decoder-epoch-13-avg-2-chunk-16-left-64.onnx",
        "joiner": "joiner-epoch-13-avg-2-chunk-16-left-64.int8.onnx",
    }
    paths = {key: model_dir / name for key, name in names.items()}
    for key, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"Missing sherpa-onnx {key} file: {path}")
    return SherpaModelFiles(**paths)


def create_keyword_spotter(
    model_dir: Path,
    keywords_file: Path,
    *,
    sherpa_api: object,
    keywords_score: float = 1.0,
    keywords_threshold: float = 0.25,
) -> object:
    files = resolve_model_files(model_dir)
    if not keywords_file.is_file():
        raise FileNotFoundError(f"Missing keywords file: {keywords_file}")
    return sherpa_api.KeywordSpotter(
        tokens=str(files.tokens),
        encoder=str(files.encoder),
        decoder=str(files.decoder),
        joiner=str(files.joiner),
        keywords_file=str(keywords_file),
        num_threads=2,
        max_active_paths=4,
        keywords_score=keywords_score,
        keywords_threshold=keywords_threshold,
        num_trailing_blanks=1,
        provider="cpu",
    )


class SherpaStream(Protocol):
    def accept_waveform(self, sample_rate: int, samples: np.ndarray) -> None: ...


class SherpaKeywordSpotter(Protocol):
    def create_stream(self) -> SherpaStream: ...

    def is_ready(self, stream: SherpaStream) -> bool: ...

    def decode_stream(self, stream: SherpaStream) -> None: ...

    def get_result(self, stream: SherpaStream) -> str: ...

    def reset_stream(self, stream: SherpaStream) -> None: ...


class SherpaKeywordRecognizer:
    """Expose only detected control words; never expose continuous transcripts."""

    def __init__(
        self,
        keyword_spotter: SherpaKeywordSpotter,
        *,
        sample_rate: int = 16_000,
    ) -> None:
        self._keyword_spotter = keyword_spotter
        self._sample_rate = sample_rate
        self._stream = keyword_spotter.create_stream()
        self._last_keyword = ""

    def AcceptWaveform(self, data: bytes) -> bool:
        if len(data) % 2:
            raise ValueError("PCM16 audio must contain complete two-byte samples")

        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        self._stream.accept_waveform(self._sample_rate, samples)
        detected = ""
        while self._keyword_spotter.is_ready(self._stream):
            self._keyword_spotter.decode_stream(self._stream)
            result = self._keyword_spotter.get_result(self._stream)
            if result:
                detected = result
                self._keyword_spotter.reset_stream(self._stream)
                break

        self._last_keyword = detected
        return bool(detected)

    def Result(self) -> str:
        return json.dumps({"text": self._last_keyword}, ensure_ascii=False)

    def PartialResult(self) -> str:
        return '{"partial": ""}'

    def FinalResult(self) -> str:
        return '{"text": ""}'
