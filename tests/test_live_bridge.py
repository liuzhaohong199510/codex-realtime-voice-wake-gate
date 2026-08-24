from pathlib import Path
from types import SimpleNamespace
import json
import unittest

import numpy as np

from wake_gate.live_bridge import run_virtual_cable_bridge


class ScriptedRecognizer:
    def __init__(self, results):
        self._results = iter(results)
        self._current = '{"text": ""}'

    def AcceptWaveform(self, _data):
        self._current = json.dumps(
            {"text": next(self._results, "")}, ensure_ascii=False
        )
        return True

    def Result(self):
        return self._current

    def PartialResult(self):
        return '{"partial": ""}'

    def FinalResult(self):
        return '{"text": ""}'


class FakeInputStream:
    def __init__(self, callback, chunks):
        self._callback = callback
        self._chunks = chunks

    def __enter__(self):
        for chunk in self._chunks:
            self._callback(chunk, len(chunk) // 2, None, None)
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        return False


class FakeOutputStream:
    def __init__(self, writes):
        self._writes = writes

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        return False

    def write(self, data):
        self._writes.append(bytes(data))
        return False


class FakeAudioApi:
    def __init__(self, devices, chunks):
        self._devices = devices
        self._chunks = chunks
        self.default = SimpleNamespace(device=(0, 1))
        self.input_open_count = 0
        self.output_open_count = 0
        self.writes = []

    def query_devices(self):
        return self._devices

    def query_hostapis(self):
        return [{"name": "Windows WASAPI"}]

    def check_output_settings(self, **kwargs):
        if kwargs["samplerate"] != 48_000:
            raise ValueError("native rate required")

    def RawInputStream(self, **kwargs):
        self.input_open_count += 1
        return FakeInputStream(kwargs["callback"], self._chunks)

    def RawOutputStream(self, **_kwargs):
        self.output_open_count += 1
        return FakeOutputStream(self.writes)


class LiveVirtualCableBridgeTests(unittest.TestCase):
    def setUp(self):
        self.devices = [
            {
                "name": "Real Microphone",
                "hostapi": 0,
                "max_input_channels": 1,
                "max_output_channels": 0,
                "default_samplerate": 48_000,
            },
            {
                "name": "CABLE Input (VB-Audio Virtual Cable)",
                "hostapi": 0,
                "max_input_channels": 0,
                "max_output_channels": 2,
                "default_samplerate": 48_000,
            },
            {
                "name": "CABLE Output (VB-Audio Virtual Cable)",
                "hostapi": 0,
                "max_input_channels": 2,
                "max_output_channels": 0,
                "default_samplerate": 48_000,
            },
        ]

    def test_wake_chunk_is_silent_then_post_wake_audio_reaches_cable_at_48k(self):
        first = np.array([1, 2, 3, 4], dtype=np.int16).tobytes()
        second = np.array([10, 20, 30, 40], dtype=np.int16).tobytes()
        audio = FakeAudioApi(self.devices, [first, second])
        messages = []

        exit_code = run_virtual_cable_bridge(
            Path("unused"),
            keywords_file=Path("unused"),
            input_device=0,
            audio_api=audio,
            recognizer=ScriptedRecognizer(["小欧", ""]),
            delay_chunks=0,
            chunk_limit=2,
            emit=messages.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(audio.input_open_count, 1)
        self.assertEqual(audio.output_open_count, 1)
        self.assertEqual(len(audio.writes), 2)
        self.assertEqual(audio.writes[0], bytes(len(first) * 3))
        self.assertEqual(len(audio.writes[1]), len(second) * 3)
        self.assertNotEqual(audio.writes[1], bytes(len(second) * 3))
        self.assertTrue(any("已唤醒" in message for message in messages))

    def test_virtual_cable_cannot_be_used_as_the_source_microphone(self):
        audio = FakeAudioApi(self.devices, [])
        messages = []

        exit_code = run_virtual_cable_bridge(
            Path("unused"),
            keywords_file=Path("unused"),
            input_device=2,
            audio_api=audio,
            recognizer=ScriptedRecognizer([]),
            chunk_limit=0,
            emit=messages.append,
        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(audio.input_open_count, 0)
        self.assertEqual(audio.output_open_count, 0)
        self.assertTrue(any("真实麦克风" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
