import json
import unittest

from wake_gate.acceptance import AcceptanceScenario
from wake_gate.core import GateEvent, GateState, VoiceGate
from wake_gate.trial_capture import capture_trial


class ScriptedRecognizer:
    def __init__(self, results):
        self._results = iter(results)
        self._current = '{"text": ""}'

    def AcceptWaveform(self, _data):
        value = next(self._results, "")
        if isinstance(value, Exception):
            raise value
        self._current = json.dumps({"text": value}, ensure_ascii=False)
        return True

    def Result(self):
        return self._current

    def PartialResult(self):
        return '{"partial": ""}'

    def FinalResult(self):
        return '{"text": ""}'


class FakeInputStream:
    def __init__(self, chunks):
        self._chunks = iter(chunks)
        self.read_count = 0

    def read(self, _blocksize):
        self.read_count += 1
        return next(self._chunks)


def wake_scenario(duration_seconds=0.5):
    return AcceptanceScenario(
        "wake",
        "说小欧",
        duration_seconds,
        GateState.CLOSED,
        (GateEvent.OPENED,),
        GateState.OPEN,
    )


class TrialCaptureTests(unittest.TestCase):
    def test_reads_only_the_fixed_trial_window_and_records_gate_events(self):
        gate = VoiceGate("小欧", "结束")
        stream = FakeInputStream([(b"a" * 8_000, False), (b"b" * 8_000, False)])

        observed = capture_trial(
            wake_scenario(),
            stream,
            ScriptedRecognizer(["小欧", ""]),
            gate,
            sample_rate=16_000,
            blocksize=4_000,
        )

        self.assertEqual(stream.read_count, 2)
        self.assertEqual(observed.events, (GateEvent.OPENED,))
        self.assertEqual(observed.final_state, GateState.OPEN)

    def test_input_overflow_fails_closed(self):
        gate = VoiceGate("小欧", "结束")
        gate.handle_recognition("小欧")
        stream = FakeInputStream([(b"x" * 8_000, True)])

        observed = capture_trial(
            wake_scenario(0.25),
            stream,
            ScriptedRecognizer([""]),
            gate,
            sample_rate=16_000,
            blocksize=4_000,
        )

        self.assertEqual(observed.events, (GateEvent.FAILED_SAFE,))
        self.assertEqual(observed.final_state, GateState.CLOSED)

    def test_recognizer_exception_fails_closed_without_returning_audio(self):
        gate = VoiceGate("小欧", "结束")
        gate.handle_recognition("小欧")
        stream = FakeInputStream([(b"private speech", False)])

        observed = capture_trial(
            wake_scenario(0.25),
            stream,
            ScriptedRecognizer([RuntimeError("recognizer failed")]),
            gate,
            sample_rate=16_000,
            blocksize=4_000,
        )

        self.assertEqual(observed.events, (GateEvent.FAILED_SAFE,))
        self.assertEqual(observed.final_state, GateState.CLOSED)
        self.assertFalse(hasattr(observed, "audio"))
        self.assertFalse(hasattr(observed, "transcript"))


if __name__ == "__main__":
    unittest.main()
