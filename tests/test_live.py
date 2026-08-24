import json
import unittest

from wake_gate.live import keyword_grammar


class KeywordGrammarTests(unittest.TestCase):
    def test_contains_only_control_phrases_and_unknown_token(self):
        grammar = json.loads(keyword_grammar("小欧", "结束"))

        self.assertEqual(grammar, ["小欧", "结束", "[unk]"])


if __name__ == "__main__":
    unittest.main()
