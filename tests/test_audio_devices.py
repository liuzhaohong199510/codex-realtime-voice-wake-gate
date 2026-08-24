import unittest

from wake_gate.audio_devices import console_safe, input_devices


class InputDevicesTests(unittest.TestCase):
    def test_returns_only_devices_with_input_channels(self):
        devices = [
            {"name": "Speakers", "max_input_channels": 0},
            {"name": "Microphone", "max_input_channels": 2},
            {"name": "Virtual output", "max_input_channels": 1},
        ]

        result = input_devices(devices)

        self.assertEqual([item["name"] for item in result], ["Microphone", "Virtual output"])

    def test_does_not_mutate_source_device_list(self):
        devices = [{"name": "Microphone", "max_input_channels": 1}]

        result = input_devices(devices)
        result[0]["name"] = "changed"

        self.assertEqual(devices[0]["name"], "Microphone")

    def test_console_safe_replaces_characters_unsupported_by_terminal(self):
        result = console_safe("Microphone ®", encoding="gbk")

        self.assertEqual(result, "Microphone ?")


if __name__ == "__main__":
    unittest.main()
