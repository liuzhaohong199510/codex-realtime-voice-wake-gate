import unittest

import numpy as np

from wake_gate.pcm_resampler import resample_pcm16_mono


class Pcm16MonoResamplerTests(unittest.TestCase):
    def test_same_rate_preserves_pcm_bytes(self):
        pcm = np.array([-32768, -100, 0, 100, 32767], dtype=np.int16).tobytes()

        self.assertEqual(resample_pcm16_mono(pcm, 16_000, 16_000), pcm)

    def test_16k_to_48k_has_exact_three_times_as_many_frames(self):
        pcm = np.array([1000, 1000, 1000, 1000], dtype=np.int16).tobytes()

        output = resample_pcm16_mono(pcm, 16_000, 48_000)

        samples = np.frombuffer(output, dtype=np.int16)
        self.assertEqual(len(samples), 12)
        self.assertTrue(np.all(samples == 1000))

    def test_odd_length_pcm_fails_instead_of_corrupting_samples(self):
        with self.assertRaisesRegex(ValueError, "complete two-byte samples"):
            resample_pcm16_mono(b"\x01", 16_000, 48_000)

    def test_invalid_sample_rate_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "positive"):
            resample_pcm16_mono(b"\x00\x00", 0, 48_000)


if __name__ == "__main__":
    unittest.main()
