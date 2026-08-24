"""Interactive ten-scenario stage-A check; audio stays in memory only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections.abc import Callable, Sequence
from typing import Any

import sounddevice as sd

from preflight_virtual_audio import configure_utf8_output
from wake_gate.acceptance import (
    DEFAULT_ACCEPTANCE_SCENARIOS,
    AcceptanceObservation,
    AcceptanceScenario,
    evaluate_acceptance,
    report_payload,
)
from wake_gate.core import GateEvent, VoiceGate
from wake_gate.live import SAMPLE_RATE
from wake_gate.sherpa_adapter import SherpaKeywordRecognizer, create_keyword_spotter
from wake_gate.trial_capture import capture_trial


BLOCKSIZE = 4_000


def run_acceptance(
    model_path: Path,
    *,
    keywords_file: Path,
    scenarios: Sequence[AcceptanceScenario] = DEFAULT_ACCEPTANCE_SCENARIOS,
    device: int | None = None,
    audio_api: Any = sd,
    sherpa_api: Any = None,
    read_line: Callable[[str], str] = input,
    emit: Callable[[str], object] = print,
    keywords_score: float = 1.0,
    keywords_threshold: float = 0.25,
) -> int:
    if sherpa_api is None:
        import sherpa_onnx as sherpa_api

    try:
        keyword_spotter = create_keyword_spotter(
            model_path,
            keywords_file,
            sherpa_api=sherpa_api,
            keywords_score=keywords_score,
            keywords_threshold=keywords_threshold,
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        emit(f"sherpa-onnx 关键词检测未就绪：{exc}。不会打开麦克风。")
        return 2

    gate = VoiceGate("小欧", "结束")
    observations: list[AcceptanceObservation] = []

    emit("阶段 A 十组真人验收：不保存音频，不保存全文转写。输入 q 可在开麦前退出。")
    emit("识别引擎：sherpa-onnx 关键词检测，仅检测“小欧”和“结束”。")
    for index, scenario in enumerate(scenarios, start=1):
        emit(f"[{index}/{len(scenarios)}] {scenario.instruction}")
        answer = read_line("准备好后按 Enter 开始；输入 q 退出：")
        if answer.strip().casefold() == "q":
            gate.fail_safe("user cancelled")
            emit("已退出，门控保持关闭，麦克风未为本场景打开。")
            return 3

        recognizer = SherpaKeywordRecognizer(keyword_spotter, sample_rate=SAMPLE_RATE)
        initial_state = gate.state
        try:
            with audio_api.RawInputStream(
                samplerate=SAMPLE_RATE,
                blocksize=BLOCKSIZE,
                device=device,
                dtype="int16",
                channels=1,
            ) as stream:
                observed = capture_trial(scenario, stream, recognizer, gate)
        except Exception as exc:
            failed = gate.fail_safe(f"{type(exc).__name__}: {exc}")
            observed = AcceptanceObservation(
                scenario.scenario_id,
                initial_state,
                (failed.event,),
                gate.state,
            )

        observations.append(observed)
        outcome = evaluate_acceptance((scenario,), (observed,)).outcomes[0]
        emit(
            f"本组：{'通过' if outcome.passed else '未通过'}；"
            f"事件={[event.value for event in observed.events]}；"
            f"状态={observed.final_state.value}。"
        )

    report = evaluate_acceptance(scenarios, observations)
    payload = report_payload(report)
    emit(f"验收结果：{report.passed_count}/{report.total_count}")
    emit(json.dumps(payload, ensure_ascii=False))
    gate.fail_safe("acceptance finished")
    return 0 if report.complete else 1


def main() -> int:
    configure_utf8_output()
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=int, default=None)
    parser.add_argument(
        "--model",
        type=Path,
        default=(
            Path(__file__).parent
            / "models"
            / "sherpa-onnx-kws-zipformer-zh-en-3M-2025-12-20"
        ),
    )
    parser.add_argument(
        "--keywords-file",
        type=Path,
        default=Path(__file__).parent / "config" / "keywords.txt",
    )
    args = parser.parse_args()
    return run_acceptance(
        args.model,
        keywords_file=args.keywords_file,
        device=args.device,
    )


if __name__ == "__main__":
    raise SystemExit(main())
