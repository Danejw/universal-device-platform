import unittest

from udp.builder import generate_header, make_manifest, GENERATED_HEADER
from udp.hardware import read_json, BOARD, WATCH


class BuilderTests(unittest.TestCase):
    def test_generated_header_matches_sourced_hardware(self):
        expected = generate_header(read_json(BOARD), read_json(WATCH))
        self.assertEqual(GENERATED_HEADER.read_text(encoding="utf-8"), expected)

    def test_simulator_uses_configured_device_id_and_capabilities(self):
        watch = read_json(WATCH)
        manifest = make_manifest(watch)
        self.assertEqual(manifest["device_id"], watch["id"])
        self.assertEqual(manifest["capabilities"], watch["active_capabilities"])

    def test_button_gpio_matches_xiao_d0(self):
        header = generate_header(read_json(BOARD), read_json(WATCH))
        self.assertIn("#define UDP_BUTTON_GPIO 1", header)


if __name__ == "__main__":
    unittest.main()
