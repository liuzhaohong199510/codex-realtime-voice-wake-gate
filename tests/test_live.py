import json
import unittest

from wake_gate.live import build_full_vocabulary_recognizer, keyword_grammar


class FakeRecognizer:
    def __init__(self):
        self.words_calls = []

    def SetWords(self, enabled):
        self.words_calls.append(enabled)


class FakeSpeechApi:
    def __init__(self):
        self.args = None
        self.recognizer = FakeRecognizer()

    def KaldiRecognizer(self, *args):
        self.args = args
        return self.recognizer


class KeywordGrammarTests(unittest.TestCase):
    def test_contains_only_control_phrases_and_unknown_token(self):
        grammar = json.loads(keyword_grammar("小欧", "结束"))

        self.assertEqual(grammar, ["小欧", "结束", "[unk]"])

    def test_live_recognizer_uses_full_vocabulary_and_word_confidence(self):
        speech_api = FakeSpeechApi()
        model = object()

        recognizer = build_full_vocabulary_recognizer(speech_api, model)

        self.assertEqual(speech_api.args, (model, 16_000))
        self.assertEqual(recognizer.words_calls, [True])


if __name__ == "__main__":
    unittest.main()
