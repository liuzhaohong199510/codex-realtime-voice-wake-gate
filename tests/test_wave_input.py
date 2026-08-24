import tempfile
import unittest
import wave
from pathlib import Path

from wake_gate.wave_input import iter_pcm16_mono


class WaveInputTests(unittest.TestCase):
    def _write_wave(self, path: Path, *, channels: int, rate: int, payload: bytes):
        with wave.open(str(path), "wb") as output:
            output.setnchannels(channels)
            output.setsampwidth(2)
            output.setframerate(rate)
            output.writeframes(payload)

    def test_yields_pcm_chunks_for_16k_mono_wave(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.wav"
            self._write_wave(path, channels=1, rate=16000, payload=b"\x01\x00" * 6)

            chunks = list(iter_pcm16_mono(path, frames_per_chunk=4))

        self.assertEqual(chunks, [b"\x01\x00" * 4, b"\x01\x00" * 2])

    def test_rejects_non_mono_wave(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "stereo.wav"
            self._write_wave(path, channels=2, rate=16000, payload=b"\x00\x00" * 4)

            with self.assertRaisesRegex(ValueError, "mono"):
                list(iter_pcm16_mono(path))

    def test_rejects_wrong_sample_rate(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "wrong-rate.wav"
            self._write_wave(path, channels=1, rate=44100, payload=b"\x00\x00" * 4)

            with self.assertRaisesRegex(ValueError, "16000"):
                list(iter_pcm16_mono(path))


if __name__ == "__main__":
    unittest.main()
