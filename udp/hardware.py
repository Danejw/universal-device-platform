"""Validate a proposed configuration against the sourced XIAO hardware profile."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOARD = ROOT / "hardware/boards/seeed-xiao-esp32s3-sense.json"
WATCH = ROOT / "hardware/configurations/watch-v0.json"
PARTS = ROOT / "hardware/parts.json"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_watch(board=None, watch=None, parts=None):
    board = board if board is not None else read_json(BOARD)
    watch = watch if watch is not None else read_json(WATCH)
    parts = parts if parts is not None else read_json(PARTS)
    errors = []
    known = {part["id"] for part in parts}
    if watch.get("controller") != board["id"]:
        errors.append("Watch controller must match board profile")
    if watch.get("power", {}).get("battery_connected") is not False:
        errors.append("V0 design must remain USB-powered until battery review")
    if set(watch.get("active_capabilities", [])) & set(watch.get("planned_capabilities", [])):
        errors.append("Active and planned capabilities must be disjoint")
    if watch.get("active_capabilities") != ["button.primary"]:
        errors.append("V0 firmware advertises only the tested-in-source button interface")
    occupied = set()
    i2c_addresses = set()
    for component in watch.get("components", []):
        if component["id"] not in known:
            errors.append("Unknown component: " + component["id"])
        wiring = component.get("wiring", {})
        if "signal_pin" in wiring:
            pin = wiring["signal_pin"]
            gpio = board["pins"].get(pin)
            if gpio is None:
                errors.append("Unknown signal pin: " + str(pin))
            elif gpio in occupied:
                errors.append("Duplicate GPIO assignment: " + str(gpio))
            elif gpio in board["reserved_gpio"]["camera"] + board["reserved_gpio"]["pdm_microphone"]:
                errors.append("GPIO reserved for Sense camera/mic: " + str(gpio))
            else:
                occupied.add(gpio)
        if wiring.get("bus") == "i2c":
            if wiring.get("sda") != board["i2c"]["sda"] or wiring.get("scl") != board["i2c"]["scl"]:
                errors.append("I2C pins do not match board profile")
            if wiring.get("logic_voltage_v") != 3.3:
                errors.append("I2C must use 3.3V logic")
            try:
                address = int(wiring["address_hex"], 16)
                if address in i2c_addresses:
                    errors.append("Duplicate I2C address: " + wiring["address_hex"])
                i2c_addresses.add(address)
            except (ValueError, TypeError, KeyError):
                errors.append("Invalid I2C address")
    return errors


def main():
    errors = validate_watch()
    if errors:
        for error in errors:
            print("FAIL:", error)
        raise SystemExit(1)
    print("PASS: watch-v0 matches documented pin, bus, and component constraints")
    print("Hardware has NOT been physically tested.")


if __name__ == "__main__":
    main()
