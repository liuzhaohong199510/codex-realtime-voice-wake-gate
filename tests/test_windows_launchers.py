from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WindowsLauncherTests(unittest.TestCase):
    def test_live_bridge_launcher_targets_the_virtual_cable_runner(self):
        launcher = ROOT / "启动Codex实时语音小欧门控.cmd"

        self.assertTrue(launcher.is_file())
        self.assertIn(b"run_live_bridge.py", launcher.read_bytes())

    def test_live_bridge_launcher_reminds_user_to_restore_codex_microphone(self):
        launcher = ROOT / "启动Codex实时语音小欧门控.cmd"

        payload = launcher.read_text(encoding="utf-8")
        self.assertIn("请把 Codex 麦克风恢复为系统默认", payload)

    def test_cmd_launchers_use_crlf_without_lone_lf(self):
        launchers = tuple(ROOT.glob("*.cmd"))
        self.assertTrue(launchers)

        for launcher in launchers:
            payload = launcher.read_bytes()
            self.assertIn(b"\r\n", payload, launcher.name)
            self.assertNotIn(b"\n", payload.replace(b"\r\n", b""), launcher.name)


if __name__ == "__main__":
    unittest.main()
