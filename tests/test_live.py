from pathlib import Path
import tempfile
import unittest

from wake_gate.live import run_live_detector


class FakeSherpaApi:
    def KeywordSpotter(self, **_kwargs):
        return FakeSpotter()


class FakeSpotter:
    def create_stream(self):
        return object()

    def is_ready(self, _stream):
        return False

    def decode_stream(self, _stream):
        raise AssertionError("not ready")

    def get_result(self, _stream):
        return ""

    def reset_stream(self, _stream):
        pass


class FakeInputStream:
    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        return False


class FakeAudioApi:
    def __init__(self):
        self.open_count = 0

    def RawInputStream(self, **_kwargs):
        self.open_count += 1
        return FakeInputStream()


class LiveSherpaWiringTests(unittest.TestCase):
    required_names = (
        "tokens.txt",
        "encoder-epoch-13-avg-2-chunk-16-left-64.int8.onnx",
        "decoder-epoch-13-avg-2-chunk-16-left-64.onnx",
        "joiner-epoch-13-avg-2-chunk-16-left-64.int8.onnx",
    )

    def test_valid_sherpa_configuration_opens_microphone_only_after_preflight(self):
        with tempfile.TemporaryDirectory() as directory:
            model_dir = Path(directory)
            for name in self.required_names:
                (model_dir / name).touch()
            keywords = model_dir / "keywords.txt"
            keywords.write_text("x iǎo ōu @小欧", encoding="utf-8")
            audio_api = FakeAudioApi()

            exit_code = run_live_detector(
                model_dir,
                keywords_file=keywords,
                duration_seconds=0,
                audio_api=audio_api,
                sherpa_api=FakeSherpaApi(),
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(audio_api.open_count, 1)

    def test_missing_model_fails_before_microphone_is_opened(self):
        audio_api = FakeAudioApi()
        missing = Path("Z:/definitely-missing-sherpa-model")

        with self.assertRaises(FileNotFoundError):
            run_live_detector(
                missing,
                keywords_file=missing / "keywords.txt",
                audio_api=audio_api,
                sherpa_api=FakeSherpaApi(),
            )

        self.assertEqual(audio_api.open_count, 0)


if __name__ == "__main__":
    unittest.main()
