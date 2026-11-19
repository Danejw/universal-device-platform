from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent


class AndroidContractTests(unittest.TestCase):
    def test_mock_and_ble_share_event_name(self):
        ble = (ROOT / "android/WatchBleClient.kt").read_text(encoding="utf-8")
        mock = (ROOT / "android/VirtualWatchClient.kt").read_text(encoding="utf-8")
        self.assertIn('listener.onEvent("button.primary.pressed")', ble)
        self.assertIn('listener.onEvent("button.primary.pressed")', mock)

    def test_firmware_and_android_share_wire_opcodes(self):
        c = (ROOT / "firmware/watch-v0/main/main.c").read_text(encoding="utf-8")
        kotlin = (ROOT / "android/WatchBleClient.kt").read_text(encoding="utf-8")
        self.assertIn("#define BLE_EVENT_BUTTON 'P'", c)
        self.assertIn("'P' ->", kotlin)
        self.assertIn("#define BLE_CMD_PING '?'", c)
        self.assertIn("'?'.code.toByte()", kotlin)


if __name__ == "__main__":
    unittest.main()
