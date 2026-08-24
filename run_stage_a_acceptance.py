"""Interactive ten-scenario stage-A check; audio stays in memory only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections.abc import Callable, Sequence
from typing import Any

import sounddevice as sd
import vosk

from preflight_virtual_audio import configure_utf8_output
from wake_gate.acceptance import (
    DEFAULT_ACCEPTANCE_SCENARIOS,
    AcceptanceObservation,
    AcceptanceScenario,
    evaluate_acceptance,
    report_payload,
)
from wake_gate.core import GateEvent, VoiceGate
from wake_gate.live import SAMPLE_RATE, keyword_grammar
from wake_gate.trial_capture import capture_trial


BLOCKSIZE = 4_000


def run_acceptance(
    model_path: Path,
    *,
    scenarios: Sequence[AcceptanceScenario] = DEFAULT_ACCEPTANCE_SCENARIOS,
    device: int | None = None,
    audio_api: Any = sd,
    speech_api: Any = vosk,
    read_line: Callable[[str], str] = input,
    emit: Callable[[str], object] = print,
) -> int:
    if not model_path.is_dir():
        emit(f"未找到本地 Vosk 模型：{model_path}。不会打开麦克风。")
        return 2

    speech_api.SetLogLevel(-1)
    model = speech_api.Model(str(model_path))
    gate = VoiceGate("小欧", "结束")
    observations: list[AcceptanceObservation] = []

    emit("阶段 A 十组真人验收：不保存音频，不保存全文转写。输入 q 可在开麦前退出。")
    for index, scenario in enumerate(scenarios, start=1):
        emit(f"[{index}/{len(scenarios)}] {scenario.instruction}")
        answer = read_line("准备好后按 Enter 开始；输入 q 退出：")
        if answer.strip().casefold() == "q":
            gate.fail_safe("user cancelled")
            emit("已退出，门控保持关闭，麦克风未为本场景打开。")
            return 3

        recognizer = speech_api.KaldiRecognizer(
            model,
            SAMPLE_RATE,
            keyword_grammar("小欧", "结束"),
        )
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
        default=Path(__file__).parent / "models" / "vosk-model-small-cn-0.22",
    )
    args = parser.parse_args()
    return run_acceptance(args.model, device=args.device)


if __name__ == "__main__":
    raise SystemExit(main())
