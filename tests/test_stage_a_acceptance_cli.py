from pathlib import Path
import tempfile
import unittest

from run_stage_a_acceptance import run_acceptance
from wake_gate.acceptance import AcceptanceScenario
from wake_gate.core import GateEvent, GateState


class FakeSpeechApi:
    def __init__(self, recognized_text):
        self.recognized_text = recognized_text
        self.kwargs = None

    def KeywordSpotter(self, **kwargs):
        self.kwargs = kwargs
        return FakeKeywordSpotter(self.recognized_text)


class FakeSherpaStream:
    def __init__(self):
        self.ready = False

    def accept_waveform(self, _sample_rate, _samples):
        self.ready = True


class FakeKeywordSpotter:
    def __init__(self, recognized_text):
        self.recognized_text = recognized_text
        self.emitted = False

    def create_stream(self):
        return FakeSherpaStream()

    def is_ready(self, stream):
        return stream.ready

    def decode_stream(self, stream):
        stream.ready = False

    def get_result(self, _stream):
        if self.emitted:
            return ""
        self.emitted = True
        return self.recognized_text

    def reset_stream(self, _stream):
        pass


class FakeInputStream:
    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        return False

    def read(self, _frames):
        return b"\x00" * 8_000, False


class FakeAudioApi:
    def __init__(self):
        self.open_count = 0

    def RawInputStream(self, **_kwargs):
        self.open_count += 1
        return FakeInputStream()


def one_wake_scenario():
    return AcceptanceScenario(
        "wake",
        "说小欧",
        0.25,
        GateState.CLOSED,
        (GateEvent.OPENED,),
        GateState.OPEN,
    )


class StageAAcceptanceCliTests(unittest.TestCase):
    required_names = (
        "tokens.txt",
        "encoder-epoch-13-avg-2-chunk-16-left-64.int8.onnx",
        "decoder-epoch-13-avg-2-chunk-16-left-64.onnx",
        "joiner-epoch-13-avg-2-chunk-16-left-64.int8.onnx",
    )

    def prepare_model(self, model_dir):
        for name in self.required_names:
            (model_dir / name).touch()
        keywords = model_dir / "keywords.txt"
        keywords.write_text("x iǎo ōu @小欧", encoding="utf-8")
        return keywords

    def test_user_started_trial_runs_in_memory_and_reports_pass(self):
        with tempfile.TemporaryDirectory() as model_dir:
            model_dir = Path(model_dir)
            keywords = self.prepare_model(model_dir)
            audio_api = FakeAudioApi()
            speech_api = FakeSpeechApi("小欧")
            messages = []

            exit_code = run_acceptance(
                model_dir,
                keywords_file=keywords,
                scenarios=(one_wake_scenario(),),
                audio_api=audio_api,
                sherpa_api=speech_api,
                read_line=lambda _prompt: "",
                emit=messages.append,
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(audio_api.open_count, 1)
        self.assertTrue(any("1/1" in message for message in messages))

    def test_user_can_cancel_before_microphone_is_opened(self):
        with tempfile.TemporaryDirectory() as model_dir:
            model_dir = Path(model_dir)
            keywords = self.prepare_model(model_dir)
            audio_api = FakeAudioApi()

            exit_code = run_acceptance(
                model_dir,
                keywords_file=keywords,
                scenarios=(one_wake_scenario(),),
                audio_api=audio_api,
                sherpa_api=FakeSpeechApi("小欧"),
                read_line=lambda _prompt: "q",
                emit=lambda _message: None,
            )

        self.assertEqual(exit_code, 3)
        self.assertEqual(audio_api.open_count, 0)

    def test_missing_model_fails_before_microphone_is_opened(self):
        audio_api = FakeAudioApi()
        missing = Path("Z:/definitely-missing-sherpa-model")

        exit_code = run_acceptance(
            missing,
            keywords_file=missing / "keywords.txt",
            scenarios=(one_wake_scenario(),),
            audio_api=audio_api,
            sherpa_api=FakeSpeechApi("小欧"),
            read_line=lambda _prompt: "",
            emit=lambda _message: None,
        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(audio_api.open_count, 0)


if __name__ == "__main__":
    unittest.main()
