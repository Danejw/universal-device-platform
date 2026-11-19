import copy
import unittest

from udp.hardware import read_json, validate_watch, BOARD, WATCH, PARTS


class HardwareTests(unittest.TestCase):
    def setUp(self):
        self.board = read_json(BOARD)
        self.watch = read_json(WATCH)
        self.parts = read_json(PARTS)

    def test_reference_profile(self):
        self.assertEqual(validate_watch(self.board, self.watch, self.parts), [])

    def test_reserved_camera_gpio_rejected(self):
        watch = copy.deepcopy(self.watch)
        watch["components"][1]["wiring"]["signal_pin"] = "D11"
        self.assertIn("GPIO reserved for Sense camera/mic: 42", validate_watch(self.board, watch, self.parts))

    def test_duplicate_i2c_rejected(self):
        watch = copy.deepcopy(self.watch)
        watch["components"][3]["wiring"]["address_hex"] = "0x6A"
        self.assertTrue(any("Duplicate I2C address" in error for error in validate_watch(self.board, watch, self.parts)))

    def test_wrong_i2c_voltage_rejected(self):
        watch = copy.deepcopy(self.watch)
        watch["components"][2]["wiring"]["logic_voltage_v"] = 5.0
        self.assertIn("I2C must use 3.3V logic", validate_watch(self.board, watch, self.parts))

    def test_battery_unreviewed_rejected(self):
        watch = copy.deepcopy(self.watch)
        watch["power"]["battery_connected"] = True
        self.assertTrue(validate_watch(self.board, watch, self.parts))


if __name__ == "__main__":
    unittest.main()
