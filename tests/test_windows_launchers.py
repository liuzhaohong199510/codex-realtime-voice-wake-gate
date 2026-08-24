from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WindowsLauncherTests(unittest.TestCase):
    def test_cmd_launchers_use_crlf_without_lone_lf(self):
        launchers = tuple(ROOT.glob("*.cmd"))
        self.assertTrue(launchers)

        for launcher in launchers:
            payload = launcher.read_bytes()
            self.assertIn(b"\r\n", payload, launcher.name)
            self.assertNotIn(b"\n", payload.replace(b"\r\n", b""), launcher.name)


if __name__ == "__main__":
    unittest.main()
