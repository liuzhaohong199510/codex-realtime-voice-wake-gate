"""Privacy-minimal evaluation for the ten stage-A voice scenarios."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from .core import GateEvent, GateState


@dataclass(frozen=True)
class AcceptanceScenario:
    scenario_id: str
    instruction: str
    duration_seconds: float
    initial_state: GateState
    expected_events: tuple[GateEvent, ...]
    expected_final_state: GateState


@dataclass(frozen=True)
class AcceptanceObservation:
    scenario_id: str
    initial_state: GateState
    events: tuple[GateEvent, ...]
    final_state: GateState


@dataclass(frozen=True)
class AcceptanceOutcome:
    scenario_id: str
    passed: bool
    events: tuple[GateEvent, ...]
    final_state: GateState | None
    reason: str | None


@dataclass(frozen=True)
class AcceptanceReport:
    outcomes: tuple[AcceptanceOutcome, ...]

    @property
    def passed_count(self) -> int:
        return sum(outcome.passed for outcome in self.outcomes)

    @property
    def total_count(self) -> int:
        return len(self.outcomes)

    @property
    def complete(self) -> bool:
        return bool(self.outcomes) and self.passed_count == self.total_count


DEFAULT_ACCEPTANCE_SCENARIOS = (
    AcceptanceScenario(
        "closed_silence",
        "保持安静，不说控制词。",
        3.0,
        GateState.CLOSED,
        (),
        GateState.CLOSED,
    ),
    AcceptanceScenario(
        "closed_unrelated",
        "正常说一句与 Codex 无关的话，不说“小欧”或“结束”。",
        4.0,
        GateState.CLOSED,
        (),
        GateState.CLOSED,
    ),
    AcceptanceScenario(
        "closed_wrong_wake",
        "说“小陈”，不要说“小欧”。",
        4.0,
        GateState.CLOSED,
        (),
        GateState.CLOSED,
    ),
    AcceptanceScenario(
        "wake_once",
        "只说一次“小欧”。",
        4.0,
        GateState.CLOSED,
        (GateEvent.OPENED,),
        GateState.OPEN,
    ),
    AcceptanceScenario(
        "open_command",
        "说一句普通指令，不说控制词。",
        4.0,
        GateState.OPEN,
        (),
        GateState.OPEN,
    ),
    AcceptanceScenario(
        "open_continuous",
        "连续说两句话，不说控制词。",
        6.0,
        GateState.OPEN,
        (),
        GateState.OPEN,
    ),
    AcceptanceScenario(
        "open_repeat_wake",
        "门控已开启时再说一次“小欧”。",
        4.0,
        GateState.OPEN,
        (),
        GateState.OPEN,
    ),
    AcceptanceScenario(
        "stop_once",
        "只说一次“结束”。",
        4.0,
        GateState.OPEN,
        (GateEvent.CLOSED,),
        GateState.CLOSED,
    ),
    AcceptanceScenario(
        "closed_after_stop",
        "结束后再说一句普通话，不说控制词。",
        4.0,
        GateState.CLOSED,
        (),
        GateState.CLOSED,
    ),
    AcceptanceScenario(
        "full_cycle",
        "依次说“小欧”、一段普通话、再说“结束”。",
        8.0,
        GateState.CLOSED,
        (GateEvent.OPENED, GateEvent.CLOSED),
        GateState.CLOSED,
    ),
)


def evaluate_acceptance(
    scenarios: Sequence[AcceptanceScenario],
    observations: Iterable[AcceptanceObservation],
) -> AcceptanceReport:
    observed_by_id = {item.scenario_id: item for item in observations}
    outcomes: list[AcceptanceOutcome] = []

    for scenario in scenarios:
        observed = observed_by_id.get(scenario.scenario_id)
        if observed is None:
            outcomes.append(
                AcceptanceOutcome(
                    scenario.scenario_id,
                    False,
                    (),
                    None,
                    "scenario was not run",
                )
            )
            continue

        mismatches = []
        if observed.initial_state is not scenario.initial_state:
            mismatches.append("initial_state")
        if observed.events != scenario.expected_events:
            mismatches.append("events")
        if observed.final_state is not scenario.expected_final_state:
            mismatches.append("final_state")

        outcomes.append(
            AcceptanceOutcome(
                scenario.scenario_id,
                not mismatches,
                observed.events,
                observed.final_state,
                None if not mismatches else "mismatch: " + ", ".join(mismatches),
            )
        )

    return AcceptanceReport(tuple(outcomes))


def report_payload(report: AcceptanceReport) -> dict[str, object]:
    return {
        "complete": report.complete,
        "passed": report.passed_count,
        "total": report.total_count,
        "outcomes": [
            {
                "scenario_id": outcome.scenario_id,
                "passed": outcome.passed,
                "events": [event.value for event in outcome.events],
                "final_state": (
                    None if outcome.final_state is None else outcome.final_state.value
                ),
                "reason": outcome.reason,
            }
            for outcome in report.outcomes
        ],
    }
