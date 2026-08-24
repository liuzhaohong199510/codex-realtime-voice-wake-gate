"""Live, local-only keyword detector wiring for the no-driver prototype."""

from __future__ import annotations

from pathlib import Path
import queue
import time

import sounddevice as sd

from .core import GateEvent, VoiceGate
from .detector import KeywordDetectionSession
from .sherpa_adapter import SherpaKeywordRecognizer, create_keyword_spotter


SAMPLE_RATE = 16_000


def run_live_detector(
    model_path: Path,
    *,
    keywords_file: Path,
    device: int | None = None,
    duration_seconds: float | None = None,
    audio_api: object = sd,
    sherpa_api: object | None = None,
) -> int:
    if sherpa_api is None:
        import sherpa_onnx as sherpa_api

    keyword_spotter = create_keyword_spotter(
        model_path,
        keywords_file,
        sherpa_api=sherpa_api,
    )
    recognizer = SherpaKeywordRecognizer(keyword_spotter, sample_rate=SAMPLE_RATE)
    gate = VoiceGate("小欧", "结束")
    session = KeywordDetectionSession(recognizer, gate)
    audio_queue: queue.Queue[bytes] = queue.Queue(maxsize=32)

    def callback(indata, _frames, _time_info, status) -> None:
        if status:
            gate.fail_safe(str(status))
        try:
            audio_queue.put_nowait(bytes(indata))
        except queue.Full:
            gate.fail_safe("audio queue overflow")

    started = time.monotonic()
    print("状态：未唤醒。说“小欧”开始，说“结束”关闭。按 Ctrl+C 停止。")
    try:
        with audio_api.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=4_000,
            device=device,
            dtype="int16",
            channels=1,
            callback=callback,
        ):
            while duration_seconds is None or time.monotonic() - started < duration_seconds:
                try:
                    chunk = audio_queue.get(timeout=0.25)
                except queue.Empty:
                    continue
                result = session.process_pcm(chunk)
                if result is None:
                    continue
                if result.event is GateEvent.OPENED:
                    print("状态：已唤醒，正在放行。")
                elif result.event is GateEvent.CLOSED:
                    print("状态：已结束，恢复静音。")
                elif result.event is GateEvent.FAILED_SAFE:
                    print("状态：检测异常，已安全静音。")
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        gate.fail_safe(str(exc))
        print(f"状态：音频设备异常，已安全静音。{type(exc).__name__}")
        return 1
    finally:
        gate.fail_safe("detector stopped")

    print("状态：检测已停止，保持静音。")
    return 0
