import unittest

from wake_gate.route_preflight import RouteStatus, preflight_virtual_cable


class RoutePreflightTests(unittest.TestCase):
    def setUp(self):
        self.devices = [
            {"name": "Real Microphone", "max_input_channels": 1, "max_output_channels": 0},
            {"name": "Speakers", "max_input_channels": 0, "max_output_channels": 2},
            {"name": "CABLE Input (VB-Audio Virtual Cable)", "max_input_channels": 0, "max_output_channels": 2},
            {"name": "CABLE Output (VB-Audio Virtual Cable)", "max_input_channels": 2, "max_output_channels": 0},
        ]

    def test_missing_cable_fails_without_falling_back_to_default_output(self):
        result = preflight_virtual_cable(self.devices[:2], lambda **_kwargs: None)

        self.assertEqual(result.status, RouteStatus.MISSING)
        self.assertIsNone(result.target)

    def test_selects_only_cable_input_playback_endpoint(self):
        calls = []

        result = preflight_virtual_cable(
            self.devices,
            lambda **kwargs: calls.append(kwargs),
            sample_rate=16_000,
        )

        self.assertEqual(result.status, RouteStatus.READY)
        self.assertEqual(result.target.index, 2)
        self.assertEqual(result.target.name, "CABLE Input (VB-Audio Virtual Cable)")
        self.assertEqual(
            calls,
            [{"device": 2, "samplerate": 16_000, "channels": 1, "dtype": "int16"}],
        )

    def test_ambiguous_cable_outputs_fail_closed(self):
        devices = self.devices + [
            {"name": "CABLE Input 2", "max_input_channels": 0, "max_output_channels": 2}
        ]

        result = preflight_virtual_cable(devices, lambda **_kwargs: None)

        self.assertEqual(result.status, RouteStatus.AMBIGUOUS)
        self.assertIsNone(result.target)

    def test_incompatible_sample_format_fails_closed(self):
        def reject_format(**_kwargs):
            raise ValueError("unsupported sample rate")

        result = preflight_virtual_cable(self.devices, reject_format)

        self.assertEqual(result.status, RouteStatus.INCOMPATIBLE)
        self.assertIsNone(result.target)
        self.assertIn("ValueError", result.reason)

    def test_preflight_does_not_mutate_device_inventory(self):
        snapshot = [dict(device) for device in self.devices]

        preflight_virtual_cable(self.devices, lambda **_kwargs: None)

        self.assertEqual(self.devices, snapshot)


if __name__ == "__main__":
    unittest.main()
