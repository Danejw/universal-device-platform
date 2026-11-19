import unittest

from udp.protocol import ProtocolError, decode_frame, encode_frame


class ProtocolTests(unittest.TestCase):
    def test_valid_command_roundtrip(self):
        obj = {"type": "command", "protocol": "udp/1", "request_id": "r1", "command": "device.ping"}
        self.assertEqual(decode_frame(encode_frame(obj)), obj)

    def test_version_rejected(self):
        with self.assertRaises(ProtocolError):
            encode_frame({"type": "command", "protocol": "udp/2", "request_id": "r1", "command": "device.ping"})

    def test_capability_duplicates_rejected(self):
        with self.assertRaises(ProtocolError):
            encode_frame({"type": "manifest", "protocol": "udp/1", "device_id": "watch",
                          "firmware_version": "sim", "capabilities": ["button.primary", "button.primary"]})

    def test_oversized_frame_rejected(self):
        with self.assertRaises(ProtocolError):
            decode_frame(b"x" * 4096 + b"\n")

    def test_malformed_frame_rejected(self):
        with self.assertRaises(ProtocolError):
            decode_frame(b"not-json\n")


if __name__ == "__main__":
    unittest.main()
