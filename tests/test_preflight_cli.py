import unittest

from preflight_virtual_audio import configure_utf8_output, run_preflight


class FakeAudioApi:
    def __init__(self, devices):
        self._devices = devices
        self.checked = []

    def query_devices(self):
        return self._devices

    def check_output_settings(self, **kwargs):
        self.checked.append(kwargs)


class ReconfigurableOutput:
    def __init__(self):
        self.calls = []

    def reconfigure(self, **kwargs):
        self.calls.append(kwargs)


class PreflightCliTests(unittest.TestCase):
    def test_cli_forces_utf8_output_for_windows_pipe_compatibility(self):
        output = ReconfigurableOutput()

        configure_utf8_output(output)

        self.assertEqual(
            output.calls,
            [{"encoding": "utf-8", "errors": "replace"}],
        )

    def test_missing_driver_reports_safe_stop(self):
        api = FakeAudioApi(
            [{"name": "Speakers", "max_input_channels": 0, "max_output_channels": 2}]
        )
        messages = []

        exit_code = run_preflight(api, messages.append)

        self.assertEqual(exit_code, 2)
        self.assertTrue(any("不会启动音频路由" in message for message in messages))
        self.assertEqual(api.checked, [])

    def test_ready_driver_reports_explicit_cable_endpoint(self):
        api = FakeAudioApi(
            [
                {"name": "Speakers", "max_input_channels": 0, "max_output_channels": 2},
                {
                    "name": "CABLE Input (VB-Audio Virtual Cable)",
                    "max_input_channels": 0,
                    "max_output_channels": 2,
                },
            ]
        )
        messages = []

        exit_code = run_preflight(api, messages.append)

        self.assertEqual(exit_code, 0)
        self.assertTrue(any("[1] CABLE Input" in message for message in messages))
        self.assertEqual(api.checked[0]["device"], 1)


if __name__ == "__main__":
    unittest.main()
