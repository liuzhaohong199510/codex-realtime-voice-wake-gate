import unittest

from wake_gate.audio_delay_gate import DelayedAudioGate
from wake_gate.core import GateEvent


class DelayedAudioGateTests(unittest.TestCase):
    def setUp(self):
        self.router = DelayedAudioGate(delay_chunks=2)

    def test_closed_gate_outputs_same_length_silence_without_buffering(self):
        output = self.router.process_chunk(b"abcd")

        self.assertEqual(output, b"\x00" * 4)
        self.assertEqual(self.router.buffered_chunks, 0)

    def test_wake_chunk_is_suppressed_and_post_wake_audio_is_delayed(self):
        wake_output = self.router.process_chunk(b"wake", GateEvent.OPENED)
        first = self.router.process_chunk(b"1111")
        second = self.router.process_chunk(b"2222")
        released = self.router.process_chunk(b"3333")

        self.assertEqual(wake_output, b"\x00" * 4)
        self.assertEqual(first, b"\x00" * 4)
        self.assertEqual(second, b"\x00" * 4)
        self.assertEqual(released, b"1111")

    def test_stop_discards_delayed_audio_and_returns_to_silence(self):
        self.router.process_chunk(b"wake", GateEvent.OPENED)
        self.router.process_chunk(b"1111")
        self.router.process_chunk(b"stop", GateEvent.CLOSED)

        after_stop = self.router.process_chunk(b"2222")

        self.assertEqual(after_stop, b"\x00" * 4)
        self.assertEqual(self.router.buffered_chunks, 0)

    def test_failure_discards_audio_and_fails_closed(self):
        self.router.process_chunk(b"wake", GateEvent.OPENED)
        self.router.process_chunk(b"1111")

        failed = self.router.process_chunk(b"boom", GateEvent.FAILED_SAFE)
        after_failure = self.router.process_chunk(b"2222")

        self.assertEqual(failed, b"\x00" * 4)
        self.assertEqual(after_failure, b"\x00" * 4)
        self.assertEqual(self.router.buffered_chunks, 0)

    def test_repeated_open_event_does_not_release_buffered_audio(self):
        self.router.process_chunk(b"wake", GateEvent.OPENED)
        self.router.process_chunk(b"1111")

        repeated = self.router.process_chunk(b"wake", GateEvent.OPENED)

        self.assertEqual(repeated, b"\x00" * 4)
        self.assertEqual(self.router.buffered_chunks, 0)


if __name__ == "__main__":
    unittest.main()
