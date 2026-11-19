# ESP32-S3 reference firmware (bench-only)

The reference target uses **ESP-IDF v5.5.6**, Espressif NimBLE, XIAO ESP32S3 Sense, USB-C, and a normally-open switch between **D0/GPIO1** and **GND**.

## Build and flash when hardware is available

Install [ESP-IDF v5.5.6](https://github.com/espressif/esp-idf/releases) first, then:

```sh
cd firmware/watch-v0
idf.py set-target esp32s3
idf.py build
idf.py -p YOUR_SERIAL_PORT flash monitor
```

Once flashed, scan for **UDP-W0** with a BLE scanner, discover service `8d39fbe0-3fa8-475f-9e08-f6ca3ff2de10`, request a sufficiently large MTU (185 or greater), read the manifest characteristic, subscribe to event notifications, and press the external button. A press sends byte `P`; write `?` to the command characteristic for a `!` pong notification. See [protocol spec](../protocol/README.md) and [wiring](../hardware/WIRING.md).

**Limitations:** Source files and CI workflow are committed, but board compilation, flashing, BLE pairing, and notification reliability must be independently verified. This starter has **no BLE bonding or application authorization**, no OTA, no battery logic, no camera/mic driver initialization, and no IMU driver. Use it only on a controlled bench. Do not deploy it with sensitive inputs or control functions until the security gate is completed.

Do not map BOOT/GPIO0 as the application button; it affects boot mode. D0/GPIO1 is documented as a normal GPIO by Seeed.
