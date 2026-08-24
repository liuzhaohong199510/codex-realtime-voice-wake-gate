import unittest

import numpy as np

from wake_gate.core import GateEvent, GateState, VoiceGate


class VoiceGateStateTests(unittest.TestCase):
    def setUp(self):
        self.gate = VoiceGate(wake_phrase="小欧", stop_phrase="结束")

    def test_starts_closed(self):
        self.assertEqual(self.gate.state, GateState.CLOSED)

    def test_wake_phrase_opens_gate_without_forwarding_phrase(self):
        result = self.gate.handle_recognition("小欧")

        self.assertEqual(result.event, GateEvent.OPENED)
        self.assertFalse(result.forward_text)
        self.assertEqual(self.gate.state, GateState.OPEN)

    def test_speech_is_forwarded_only_while_open(self):
        closed = self.gate.handle_recognition("这句话不应该发送")
        self.gate.handle_recognition("小欧")
        opened = self.gate.handle_recognition("帮我检查当前任务")

        self.assertFalse(closed.forward_text)
        self.assertTrue(opened.forward_text)

    def test_stop_phrase_closes_gate_without_forwarding_phrase(self):
        self.gate.handle_recognition("小欧")

        result = self.gate.handle_recognition("结束")

        self.assertEqual(result.event, GateEvent.CLOSED)
        self.assertFalse(result.forward_text)
        self.assertEqual(self.gate.state, GateState.CLOSED)

    def test_stop_phrase_is_ignored_when_gate_is_already_closed(self):
        result = self.gate.handle_recognition("结束")

        self.assertEqual(result.event, GateEvent.NONE)
        self.assertEqual(self.gate.state, GateState.CLOSED)

    def test_wake_phrase_is_ignored_when_gate_is_already_open(self):
        self.gate.handle_recognition("小欧")

        result = self.gate.handle_recognition("小欧")

        self.assertEqual(result.event, GateEvent.NONE)
        self.assertEqual(self.gate.state, GateState.OPEN)

    def test_keyword_matching_ignores_spaces_and_common_punctuation(self):
        opened = self.gate.handle_recognition("小，欧！")
        closed = self.gate.handle_recognition("结 束。")

        self.assertEqual(opened.event, GateEvent.OPENED)
        self.assertEqual(closed.event, GateEvent.CLOSED)

    def test_failure_always_returns_to_closed(self):
        self.gate.handle_recognition("小欧")

        result = self.gate.fail_safe("microphone disconnected")

        self.assertEqual(result.event, GateEvent.FAILED_SAFE)
        self.assertEqual(self.gate.state, GateState.CLOSED)


class VoiceGateAudioTests(unittest.TestCase):
    def setUp(self):
        self.gate = VoiceGate(wake_phrase="小欧", stop_phrase="结束")
        self.samples = np.array([0.25, -0.5, 0.75], dtype=np.float32)

    def test_closed_gate_outputs_silence(self):
        output = self.gate.apply_audio(self.samples)

        np.testing.assert_array_equal(output, np.zeros_like(self.samples))

    def test_open_gate_preserves_audio(self):
        self.gate.handle_recognition("小欧")

        output = self.gate.apply_audio(self.samples)

        np.testing.assert_array_equal(output, self.samples)
        self.assertIsNot(output, self.samples)


if __name__ == "__main__":
    unittest.main()
