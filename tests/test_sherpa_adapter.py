import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from wake_gate.sherpa_adapter import (
    SherpaKeywordRecognizer,
    create_keyword_spotter,
    resolve_model_files,
)


class FakeStream:
    def __init__(self):
        self.accepted = []

    def accept_waveform(self, sample_rate, samples):
        self.accepted.append((sample_rate, samples.copy()))


class FakeKeywordSpotter:
    def __init__(self, results):
        self._results = iter(results)
        self.current = ""
        self.stream = FakeStream()
        self.reset_count = 0
        self.ready = True

    def create_stream(self):
        return self.stream

    def is_ready(self, _stream):
        return self.ready

    def decode_stream(self, _stream):
        self.current = next(self._results, "")
        self.ready = False

    def get_result(self, _stream):
        return self.current

    def reset_stream(self, _stream):
        self.reset_count += 1
        self.current = ""


class SherpaKeywordRecognizerTests(unittest.TestCase):
    def test_pcm16_is_normalized_and_detected_keyword_is_returned_as_final_json(self):
        spotter = FakeKeywordSpotter(["小欧"])
        recognizer = SherpaKeywordRecognizer(spotter, sample_rate=16_000)

        detected = recognizer.AcceptWaveform(np.array([0, 32767, -32768], dtype=np.int16).tobytes())

        self.assertTrue(detected)
        self.assertEqual(json.loads(recognizer.Result()), {"text": "小欧"})
        sample_rate, samples = spotter.stream.accepted[0]
        self.assertEqual(sample_rate, 16_000)
        np.testing.assert_allclose(samples, [0.0, 32767 / 32768, -1.0])
        self.assertEqual(spotter.reset_count, 1)

    def test_unrelated_audio_returns_no_keyword_or_transcript(self):
        recognizer = SherpaKeywordRecognizer(FakeKeywordSpotter([""]))

        detected = recognizer.AcceptWaveform(b"\x00\x00" * 16)

        self.assertFalse(detected)
        self.assertEqual(json.loads(recognizer.PartialResult()), {"partial": ""})
        self.assertEqual(json.loads(recognizer.FinalResult()), {"text": ""})

    def test_odd_length_pcm_fails_instead_of_silently_corrupting_audio(self):
        recognizer = SherpaKeywordRecognizer(FakeKeywordSpotter([""]))

        with self.assertRaises(ValueError):
            recognizer.AcceptWaveform(b"\x00")


class FakeSherpaApi:
    def __init__(self):
        self.kwargs = None

    def KeywordSpotter(self, **kwargs):
        self.kwargs = kwargs
        return object()


class SherpaRuntimeConfigTests(unittest.TestCase):
    required_names = (
        "tokens.txt",
        "encoder-epoch-13-avg-2-chunk-16-left-64.int8.onnx",
        "decoder-epoch-13-avg-2-chunk-16-left-64.onnx",
        "joiner-epoch-13-avg-2-chunk-16-left-64.int8.onnx",
    )

    def test_resolves_low_cpu_chunk16_model_files(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = Path(directory)
            for name in self.required_names:
                (model_dir / name).touch()

            files = resolve_model_files(model_dir)

        self.assertTrue(files.encoder.name.endswith("int8.onnx"))
        self.assertEqual(files.decoder.name, self.required_names[2])
        self.assertTrue(files.joiner.name.endswith("int8.onnx"))

    def test_missing_model_file_is_reported_before_microphone_use(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(FileNotFoundError, "tokens.txt"):
                resolve_model_files(Path(directory))

    def test_factory_uses_official_kws_defaults_and_custom_keyword_file(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = Path(directory)
            for name in self.required_names:
                (model_dir / name).touch()
            keywords = model_dir / "keywords.txt"
            keywords.write_text("x iǎo ōu @小欧", encoding="utf-8")
            api = FakeSherpaApi()

            create_keyword_spotter(model_dir, keywords, sherpa_api=api)

        self.assertEqual(api.kwargs["keywords_file"], str(keywords))
        self.assertEqual(api.kwargs["provider"], "cpu")
        self.assertEqual(api.kwargs["keywords_threshold"], 0.25)
        self.assertEqual(api.kwargs["max_active_paths"], 4)


if __name__ == "__main__":
    unittest.main()
