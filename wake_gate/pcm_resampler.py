"""Small in-memory PCM16 mono resampler for the virtual-cable boundary."""

from __future__ import annotations

import numpy as np


def resample_pcm16_mono(
    pcm: bytes,
    input_sample_rate: int,
    output_sample_rate: int,
) -> bytes:
    if input_sample_rate <= 0 or output_sample_rate <= 0:
        raise ValueError("sample rates must be positive")
    if len(pcm) % 2:
        raise ValueError("PCM16 audio must contain complete two-byte samples")
    if input_sample_rate == output_sample_rate or not pcm:
        return bytes(pcm)

    samples = np.frombuffer(pcm, dtype=np.int16)
    output_frames = round(len(samples) * output_sample_rate / input_sample_rate)
    source_positions = (
        np.arange(output_frames, dtype=np.float64)
        * input_sample_rate
        / output_sample_rate
    )
    resampled = np.interp(
        source_positions,
        np.arange(len(samples), dtype=np.float64),
        samples.astype(np.float64),
    )
    return np.rint(resampled).clip(-32768, 32767).astype(np.int16).tobytes()
