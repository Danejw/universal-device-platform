# Universal Device Platform

A reusable foundation for custom connected devices, starting with an **AI wristband built around the Seeed XIAO ESP32S3 Sense**.

**Current status: software reference implementation, not a verified hardware build.** The repo contains a manufacturer-backed board profile, an explicit watch configuration, a testable device protocol, and a virtual-device simulator. The initial firmware target is ESP-IDF/NimBLE.

## Start without parts

Requires Python 3.11+ and no third-party Python dependencies.

```sh
python -m unittest discover -s tests -v
python -m udp.builder --check
python -m udp.simulator
# Separate terminal:
python -m udp.client press
```

The simulator listens on **127.0.0.1:8765** and advertises only its implemented `button.primary` capability. The `sim.button.press` command is **simulator-only**; it is never a production hardware command.

## Architecture

```text
[Watch: ESP32-S3 hardware + firmware]  --->  [BLE GATT transport adapter]
               |                                  |
[Virtual watch on localhost TCP] ------> [Canonical UDP/1 device messages]
                                                  |
                                [Android / Personal Voice device adapter]
                                                  |
                                  [Existing agent + computer controls]
```

UDP in this repository means **Universal Device Platform**, not the UDP network protocol. The virtual transport is newline-delimited JSON over localhost TCP. BLE uses the same capability vocabulary with a small BLE-specific wire encoding. Hardware connections, security, and camera/audio streaming are separate implementation milestones.

## Hardware baseline

See [hardware/BOM.md](hardware/BOM.md), [hardware/WIRING.md](hardware/WIRING.md), and [hardware/configurations/watch-v0.json](hardware/configurations/watch-v0.json). V0 is **USB-powered** and uses XIAO D0/GPIO1 for a button. The camera and microphone physically included on the Sense expansion are **not enabled capabilities until corresponding drivers and tests exist**. A six-axis IMU and optical sensor are specified as optional follow-ons.

**Important:** Seeed has shipped OV2640, OV3660, and OV5640 variants. The current listing describes an OV5640, but verify the delivered sensor. Never hard-code the camera sensor before board inspection. No battery selection, enclosure, medical accuracy, or all-day runtime has been validated.

## Project layout

- `udp/`: zero-dependency Python simulator, client, protocol validation, hardware checks, and configuration generator
- `protocol/`: canonical messages and device contract
- `hardware/`: documented profiles, bill of materials, wiring and validation inputs
- `firmware/`: initial ESP-IDF BLE firmware target (not hardware-tested)
- `android/`: integration guidance for Personal Voice (does not modify that other repo)
- `tests/`: repeatable host-side tests
- `.github/workflows/`: automated software checks

See [AGENTS.md](AGENTS.md) for implementation rules and [docs/ROADMAP.md](docs/ROADMAP.md) for acceptance gates.