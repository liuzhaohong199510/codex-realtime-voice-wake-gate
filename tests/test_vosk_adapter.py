import unittest

from wake_gate.vosk_adapter import RecognitionKind, parse_vosk_result


class ParseVoskResultTests(unittest.TestCase):
    def test_extracts_final_text(self):
        result = parse_vosk_result('{"text": "小 欧"}')

        self.assertEqual(result.kind, RecognitionKind.FINAL)
        self.assertEqual(result.text, "小 欧")
        self.assertIsNone(result.confidence)

    def test_extracts_lowest_word_confidence_from_final_result(self):
        result = parse_vosk_result(
            '{"text":"小 欧","result":['
            '{"word":"小","conf":0.91},{"word":"欧","conf":0.73}]}'
        )

        self.assertEqual(result.kind, RecognitionKind.FINAL)
        self.assertEqual(result.confidence, 0.73)

    def test_extracts_partial_text(self):
        result = parse_vosk_result('{"partial": "结束"}')

        self.assertEqual(result.kind, RecognitionKind.PARTIAL)
        self.assertEqual(result.text, "结束")

    def test_empty_result_is_ignored(self):
        result = parse_vosk_result('{"partial": ""}')

        self.assertEqual(result.kind, RecognitionKind.EMPTY)
        self.assertEqual(result.text, "")

    def test_invalid_json_fails_closed(self):
        result = parse_vosk_result('not-json')

        self.assertEqual(result.kind, RecognitionKind.ERROR)
        self.assertEqual(result.text, "")

    def test_unknown_tokens_are_removed_before_keyword_matching(self):
        result = parse_vosk_result('{"text": "[unk] 结束"}')

        self.assertEqual(result.kind, RecognitionKind.FINAL)
        self.assertEqual(result.text, "结束")

    def test_result_containing_only_unknown_token_is_empty(self):
        result = parse_vosk_result('{"partial": "[unk]"}')

        self.assertEqual(result.kind, RecognitionKind.EMPTY)
        self.assertEqual(result.text, "")


if __name__ == "__main__":
    unittest.main()
