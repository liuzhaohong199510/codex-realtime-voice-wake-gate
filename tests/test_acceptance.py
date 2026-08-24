import unittest

from wake_gate.acceptance import (
    DEFAULT_ACCEPTANCE_SCENARIOS,
    AcceptanceObservation,
    evaluate_acceptance,
    report_payload,
)
from wake_gate.core import GateEvent, GateState


def observation(scenario_id, initial_state, events, final_state):
    return AcceptanceObservation(
        scenario_id=scenario_id,
        initial_state=initial_state,
        events=tuple(events),
        final_state=final_state,
    )


class AcceptanceEvaluationTests(unittest.TestCase):
    def test_required_ten_scenario_sequence_can_prove_stage_a_state_transitions(self):
        observations = [
            observation("closed_silence", GateState.CLOSED, [], GateState.CLOSED),
            observation("closed_unrelated", GateState.CLOSED, [], GateState.CLOSED),
            observation("closed_wrong_wake", GateState.CLOSED, [], GateState.CLOSED),
            observation("wake_once", GateState.CLOSED, [GateEvent.OPENED], GateState.OPEN),
            observation("open_command", GateState.OPEN, [], GateState.OPEN),
            observation("open_continuous", GateState.OPEN, [], GateState.OPEN),
            observation("open_repeat_wake", GateState.OPEN, [], GateState.OPEN),
            observation("stop_once", GateState.OPEN, [GateEvent.CLOSED], GateState.CLOSED),
            observation("closed_after_stop", GateState.CLOSED, [], GateState.CLOSED),
            observation(
                "full_cycle",
                GateState.CLOSED,
                [GateEvent.OPENED, GateEvent.CLOSED],
                GateState.CLOSED,
            ),
        ]

        report = evaluate_acceptance(DEFAULT_ACCEPTANCE_SCENARIOS, observations)

        self.assertEqual(report.passed_count, 10)
        self.assertEqual(report.total_count, 10)
        self.assertTrue(report.complete)

    def test_unexpected_wake_during_unrelated_speech_fails_the_scenario(self):
        observations = [
            observation(
                "closed_unrelated",
                GateState.CLOSED,
                [GateEvent.OPENED],
                GateState.OPEN,
            )
        ]

        report = evaluate_acceptance(
            [DEFAULT_ACCEPTANCE_SCENARIOS[1]], observations
        )

        self.assertFalse(report.complete)
        self.assertEqual(report.passed_count, 0)
        self.assertIn("events", report.outcomes[0].reason)

    def test_missing_observation_is_reported_as_failure(self):
        report = evaluate_acceptance(DEFAULT_ACCEPTANCE_SCENARIOS[:1], [])

        self.assertFalse(report.complete)
        self.assertEqual(report.total_count, 1)
        self.assertIn("not run", report.outcomes[0].reason)

    def test_report_payload_contains_only_events_and_states_not_audio_or_transcript(self):
        report = evaluate_acceptance(
            DEFAULT_ACCEPTANCE_SCENARIOS[:1],
            [observation("closed_silence", GateState.CLOSED, [], GateState.CLOSED)],
        )

        payload = report_payload(report)

        self.assertEqual(
            payload,
            {
                "complete": True,
                "passed": 1,
                "total": 1,
                "outcomes": [
                    {
                        "scenario_id": "closed_silence",
                        "passed": True,
                        "events": [],
                        "final_state": "closed",
                        "reason": None,
                    }
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
