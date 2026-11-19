import json
import unittest
from pathlib import Path

from udp.blecodec import encode_ble_command, normalize_notification
from udp.builder import make_manifest
from udp.hardware import read_json, WATCH
from udp.protocol import ProtocolError, decode_frame, encode_frame

FIXTURE = Path(__file__).resolve().parent.parent / "protocol/fixtures/watch-v0.json"


class ContractFixtures(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_manifest_matches_watch_config(self):
        self.assertEqual(make_manifest(read_json(WATCH)), self.fixture["simulated_manifest"])

    def test_button_matches_canonical_event(self):
        self.assertEqual(normalize_notification(b"P", "watch-v0", 1),
                         self.fixture["normalized_press"])

    def test_ping_and_pong(self):
        self.assertEqual(encode_ble_command("device.ping"), b"?")
        event = normalize_notification(b"!", "watch-v0", 2)
        self.assertEqual(event["event"], "device.pong")

    def test_message_roundtrip(self):
        self.assertEqual(decode_frame(encode_frame(self.fixture["normalized_press"])),
                         self.fixture["normalized_press"])

    def test_unknown_ble_bytes_rejected(self):
        for b in (b"", b"p", b"PP", b"\x00"):
            with self.subTest(b=b):
                with self.assertRaises(ProtocolError):
                    normalize_notification(b, "watch-v0", 1)

    def test_future_hardware_command_is_not_advertised(self):
        with self.assertRaises(ProtocolError):
            encode_ble_command("camera.capture")

    def test_invalid_sequence_rejected(self):
        with self.assertRaises(ProtocolError):
            normalize_notification(b"P", "watch-v0", -1)


if __name__ == "__main__":
    unittest.main()
