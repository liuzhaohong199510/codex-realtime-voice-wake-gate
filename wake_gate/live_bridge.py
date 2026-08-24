"""Live real-microphone to VB-CABLE bridge with a fail-closed voice gate."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import queue
import time
from typing import Any

import sounddevice as sd

from .audio_router import LocalAudioRouter
from .core import GateEvent
from .pcm_resampler import resample_pcm16_mono
from .route_preflight import RouteStatus, preflight_virtual_cable
from .sherpa_adapter import SherpaKeywordRecognizer, create_keyword_spotter


INPUT_SAMPLE_RATE = 16_000
INPUT_BLOCKSIZE = 4_000


def run_virtual_cable_bridge(
    model_path: Path,
    *,
    keywords_file: Path,
    input_device: int | None = None,
    duration_seconds: float | None = None,
    audio_api: Any = sd,
    sherpa_api: Any | None = None,
    recognizer: Any | None = None,
    delay_chunks: int = 4,
    chunk_limit: int | None = None,
    emit: Callable[[str], object] = print,
) -> int:
    devices = list(audio_api.query_devices())
    route = preflight_virtual_cable(
        devices,
        audio_api.check_output_settings,
        hostapis=audio_api.query_hostapis(),
    )
    if route.status is not RouteStatus.READY:
        emit(f"虚拟音频预检未通过：{route.reason} 保持静音。")
        return 2
    target = route.target
    assert target is not None

    if input_device is None:
        input_device = int(audio_api.default.device[0])
    if not 0 <= input_device < len(devices):
        emit("未找到指定的真实麦克风，保持静音。")
        return 2
    source = devices[input_device]
    source_name = str(source.get("name", ""))
    if (
        int(source.get("max_input_channels", 0)) <= 0
        or "cable" in source_name.casefold()
        or "vb-audio" in source_name.casefold()
    ):
        emit("输入端必须是真实麦克风，不能使用虚拟音频线，保持静音。")
        return 2

    if recognizer is None:
        if sherpa_api is None:
            import sherpa_onnx as sherpa_api
        spotter = create_keyword_spotter(
            model_path,
            keywords_file,
            sherpa_api=sherpa_api,
        )
        recognizer = SherpaKeywordRecognizer(
            spotter,
            sample_rate=INPUT_SAMPLE_RATE,
        )

    router = LocalAudioRouter(recognizer, delay_chunks=delay_chunks)
    audio_queue: queue.Queue[bytes] = queue.Queue(maxsize=32)
    callback_failures: list[str] = []

    def callback(indata, _frames, _time_info, status) -> None:
        if status:
            callback_failures.append(str(status))
            return
        try:
            audio_queue.put_nowait(bytes(indata))
        except queue.Full:
            callback_failures.append("audio queue overflow")

    started = time.monotonic()
    processed_chunks = 0
    emit(
        f"门控已启动：真实麦克风 [{input_device}] {source_name}；"
        f"虚拟输出 [{target.index}] {target.name} @ {target.sample_rate} Hz。"
    )
    emit("状态：未唤醒。说“小欧”开始，说“结束”关闭。按 Ctrl+C 停止。")
    try:
        with audio_api.RawOutputStream(
            samplerate=target.sample_rate,
            blocksize=0,
            device=target.index,
            dtype="int16",
            channels=1,
        ) as output_stream, audio_api.RawInputStream(
            samplerate=INPUT_SAMPLE_RATE,
            blocksize=INPUT_BLOCKSIZE,
            device=input_device,
            dtype="int16",
            channels=1,
            callback=callback,
        ):
            while chunk_limit is None or processed_chunks < chunk_limit:
                if (
                    duration_seconds is not None
                    and time.monotonic() - started >= duration_seconds
                ):
                    break
                if callback_failures:
                    raise RuntimeError(callback_failures[0])
                try:
                    chunk = audio_queue.get(timeout=0.25)
                except queue.Empty:
                    continue

                gated = router.process_chunk(chunk)
                output = resample_pcm16_mono(
                    gated,
                    INPUT_SAMPLE_RATE,
                    target.sample_rate,
                )
                if output_stream.write(output):
                    raise RuntimeError("virtual output underflow")
                processed_chunks += 1

                if router.last_event is GateEvent.OPENED:
                    emit("状态：已唤醒，正在放行。")
                elif router.last_event is GateEvent.CLOSED:
                    emit("状态：已结束，恢复静音。")
                elif router.last_event is GateEvent.FAILED_SAFE:
                    raise RuntimeError(router.failure_reason or "gate failed safe")
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        emit(f"状态：音频桥异常，已安全静音。{type(exc).__name__}: {exc}")
        return 1
    finally:
        emit("状态：门控已停止，虚拟输出恢复静音。")

    return 0
