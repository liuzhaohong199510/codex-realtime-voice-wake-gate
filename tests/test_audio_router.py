import json
import unittest

from wake_gate.audio_router import LocalAudioRouter
from wake_gate.core import GateEvent, GateState


class ScriptedRecognizer:
    def __init__(self, results):
        self._results = iter(results)
        self._current = '{"text": ""}'

    def AcceptWaveform(self, _data):
        result = next(self._results, "")
        if isinstance(result, Exception):
            raise result
        self._current = json.dumps({"text": result}, ensure_ascii=False)
        return True

    def Result(self):
        return self._current

    def PartialResult(self):
        return '{"partial": ""}'

    def FinalResult(self):
        return '{"text": ""}'


class LocalAudioRouterTests(unittest.TestCase):
    def test_closed_router_outputs_same_length_silence(self):
        router = LocalAudioRouter(ScriptedRecognizer([""]), delay_chunks=2)

        output = router.process_chunk(b"abcd")

        self.assertEqual(output, b"\x00" * 4)
        self.assertEqual(router.state, GateState.CLOSED)
        self.assertEqual(router.last_event, GateEvent.NONE)

    def test_wake_phrase_is_suppressed_before_post_wake_audio_is_released(self):
        router = LocalAudioRouter(
            ScriptedRecognizer(["小欧", "", "", ""]), delay_chunks=2
        )

        wake = router.process_chunk(b"wake")
        first = router.process_chunk(b"1111")
        second = router.process_chunk(b"2222")
        released = router.process_chunk(b"3333")

        self.assertEqual(wake, b"\x00" * 4)
        self.assertEqual(first, b"\x00" * 4)
        self.assertEqual(second, b"\x00" * 4)
        self.assertEqual(released, b"1111")
        self.assertEqual(router.state, GateState.OPEN)

    def test_stop_phrase_discards_buffered_audio_and_closes_router(self):
        router = LocalAudioRouter(
            ScriptedRecognizer(["小欧", "", "结束", ""]), delay_chunks=2
        )
        router.process_chunk(b"wake")
        router.process_chunk(b"1111")

        stop = router.process_chunk(b"stop")
        after_stop = router.process_chunk(b"2222")

        self.assertEqual(stop, b"\x00" * 4)
        self.assertEqual(after_stop, b"\x00" * 4)
        self.assertEqual(router.state, GateState.CLOSED)
        self.assertEqual(router.last_event, GateEvent.NONE)

    def test_recognizer_exception_fails_closed_and_never_forwards_audio(self):
        router = LocalAudioRouter(
            ScriptedRecognizer(["小欧", "", RuntimeError("recognizer failed")]),
            delay_chunks=1,
        )
        router.process_chunk(b"wake")
        router.process_chunk(b"1111")

        failed = router.process_chunk(b"boom")

        self.assertEqual(failed, b"\x00" * 4)
        self.assertEqual(router.state, GateState.CLOSED)
        self.assertEqual(router.last_event, GateEvent.FAILED_SAFE)
        self.assertIn("RuntimeError", router.failure_reason)


if __name__ == "__main__":
    unittest.main()
