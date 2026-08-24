import json
from pathlib import Path
import tempfile
import unittest

from run_stage_a_acceptance import run_acceptance
from wake_gate.acceptance import AcceptanceScenario
from wake_gate.core import GateEvent, GateState


class FakeRecognizer:
    def __init__(self, text):
        self._text = text

    def AcceptWaveform(self, _data):
        return True

    def Result(self):
        text, self._text = self._text, ""
        return json.dumps({"text": text}, ensure_ascii=False)

    def PartialResult(self):
        return '{"partial": ""}'

    def FinalResult(self):
        return '{"text": ""}'


class FakeSpeechApi:
    def __init__(self, recognized_text):
        self.recognized_text = recognized_text
        self.model_paths = []

    def SetLogLevel(self, _level):
        pass

    def Model(self, path):
        self.model_paths.append(path)
        return object()

    def KaldiRecognizer(self, _model, _sample_rate, _grammar):
        return FakeRecognizer(self.recognized_text)


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
    def test_user_started_trial_runs_in_memory_and_reports_pass(self):
        with tempfile.TemporaryDirectory() as model_dir:
            audio_api = FakeAudioApi()
            speech_api = FakeSpeechApi("小欧")
            messages = []

            exit_code = run_acceptance(
                Path(model_dir),
                scenarios=(one_wake_scenario(),),
                audio_api=audio_api,
                speech_api=speech_api,
                read_line=lambda _prompt: "",
                emit=messages.append,
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(audio_api.open_count, 1)
        self.assertTrue(any("1/1" in message for message in messages))

    def test_user_can_cancel_before_microphone_is_opened(self):
        with tempfile.TemporaryDirectory() as model_dir:
            audio_api = FakeAudioApi()

            exit_code = run_acceptance(
                Path(model_dir),
                scenarios=(one_wake_scenario(),),
                audio_api=audio_api,
                speech_api=FakeSpeechApi("小欧"),
                read_line=lambda _prompt: "q",
                emit=lambda _message: None,
            )

        self.assertEqual(exit_code, 3)
        self.assertEqual(audio_api.open_count, 0)

    def test_missing_model_fails_before_microphone_is_opened(self):
        audio_api = FakeAudioApi()
        missing = Path("Z:/definitely-missing-vosk-model")

        exit_code = run_acceptance(
            missing,
            scenarios=(one_wake_scenario(),),
            audio_api=audio_api,
            speech_api=FakeSpeechApi("小欧"),
            read_line=lambda _prompt: "",
            emit=lambda _message: None,
        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(audio_api.open_count, 0)


if __name__ == "__main__":
    unittest.main()
