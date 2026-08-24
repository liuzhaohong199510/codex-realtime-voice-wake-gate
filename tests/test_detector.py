import unittest

from wake_gate.core import GateEvent, GateState, VoiceGate
from wake_gate.detector import KeywordDetectionSession


class FakeRecognizer:
    def __init__(self, *, final_payload=None, partial_payload=None, finish_payload=None):
        self.final_payload = final_payload
        self.partial_payload = partial_payload or '{"partial": ""}'
        self.finish_payload = finish_payload or '{"text": ""}'

    def AcceptWaveform(self, _data):
        return self.final_payload is not None

    def Result(self):
        return self.final_payload

    def PartialResult(self):
        return self.partial_payload

    def FinalResult(self):
        return self.finish_payload


class KeywordDetectionSessionTests(unittest.TestCase):
    def test_final_wake_phrase_opens_gate(self):
        gate = VoiceGate("小欧", "结束")
        session = KeywordDetectionSession(
            FakeRecognizer(final_payload='{"text": "小 欧"}'), gate
        )

        result = session.process_pcm(b"audio")

        self.assertEqual(result.event, GateEvent.OPENED)
        self.assertEqual(gate.state, GateState.OPEN)

    def test_partial_stop_phrase_does_not_close_gate_before_final_result(self):
        gate = VoiceGate("小欧", "结束")
        gate.handle_recognition("小欧")
        session = KeywordDetectionSession(
            FakeRecognizer(partial_payload='{"partial": "结束"}'), gate
        )

        result = session.process_pcm(b"audio")

        self.assertIsNone(result)
        self.assertEqual(gate.state, GateState.OPEN)

    def test_repeated_partial_is_not_emitted_twice(self):
        gate = VoiceGate("小欧", "结束")
        session = KeywordDetectionSession(
            FakeRecognizer(partial_payload='{"partial": "小欧"}'), gate
        )

        first = session.process_pcm(b"audio")
        second = session.process_pcm(b"audio")

        self.assertIsNone(first)
        self.assertIsNone(second)
        self.assertEqual(gate.state, GateState.CLOSED)

    def test_low_confidence_final_control_phrase_is_ignored(self):
        gate = VoiceGate("小欧", "结束")
        session = KeywordDetectionSession(
            FakeRecognizer(
                final_payload=(
                    '{"text":"小欧","result":'
                    '[{"word":"小欧","conf":0.42}]}'
                )
            ),
            gate,
            min_confidence=0.65,
        )

        result = session.process_pcm(b"audio")

        self.assertIsNone(result)
        self.assertEqual(gate.state, GateState.CLOSED)

    def test_high_confidence_final_control_phrase_opens_gate(self):
        gate = VoiceGate("小欧", "结束")
        session = KeywordDetectionSession(
            FakeRecognizer(
                final_payload=(
                    '{"text":"小欧","result":'
                    '[{"word":"小欧","conf":0.91}]}'
                )
            ),
            gate,
            min_confidence=0.65,
        )

        result = session.process_pcm(b"audio")

        self.assertEqual(result.event, GateEvent.OPENED)
        self.assertEqual(gate.state, GateState.OPEN)

    def test_invalid_recognizer_payload_fails_closed(self):
        gate = VoiceGate("小欧", "结束")
        gate.handle_recognition("小欧")
        session = KeywordDetectionSession(
            FakeRecognizer(final_payload="not-json"), gate
        )

        result = session.process_pcm(b"audio")

        self.assertEqual(result.event, GateEvent.FAILED_SAFE)
        self.assertEqual(gate.state, GateState.CLOSED)

    def test_finish_processes_keyword_at_end_of_stream(self):
        gate = VoiceGate("小欧", "结束")
        gate.handle_recognition("小欧")
        session = KeywordDetectionSession(
            FakeRecognizer(finish_payload='{"text": "结束"}'), gate
        )

        result = session.finish()

        self.assertEqual(result.event, GateEvent.CLOSED)
        self.assertEqual(gate.state, GateState.CLOSED)


if __name__ == "__main__":
    unittest.main()
