# Roadmap and verified state

## Implemented in repository

- Host-side protocol and manifest validation
- Deterministic virtual watch with button simulation and command/response
- Machine-readable verified-source board/pin catalog with conflicting-pin and I2C-address checks
- Tests and GitHub Actions Python CI
- ESP-IDF BLE button/manifest reference firmware source (compile/flash needs validation)
- Android BLE integration guide and planned adapter contract (Personal Voice repo remains unchanged)

## Hardware gates (not yet passed)

1. **USB bench:** ESP-IDF firmware builds, flashes and logs cleanly on the actual purchased XIAO. Button LOW -> debounced press observed.
2. **Android BLE:** user-authorized pairing, MTU, manifest read, notifications, disconnect/reconnect verified on actual phone and board.
3. **Sensor:** add Adafruit IMU driver, read ID register then real accelerometer values, compare against motion.
4. **Camera:** detect OV2640/OV3660/OV5640 variant and capture photos with appropriate manufacturer driver and sensor thermal limits.
5. **Microphone:** initialize PDM interface and verify sample rate, recording and latency.
6. **Media:** Wi-Fi provisioning and authenticated image/audio transfers, size limits and privacy controls.
7. **Battery:** electrically vetted protected LiPo, charger current, thermal and capacity tests; separate enclosure fit.
8. **Device Builder:** validated manifests generate a config and component checklist; auto-detection only for modules with safe electrical connections and reliable identity probes.

## BLE GATT UUID contract

Service: `8d39fbe0-3fa8-475f-9e08-f6ca3ff2de10`

- Manifest read: `8d39fbe0-3fa8-475f-9e08-f6ca3ff2de11`
- Event notify: `8d39fbe0-3fa8-475f-9e08-f6ca3ff2de12`
- Command write: `8d39fbe0-3fa8-475f-9e08-f6ca3ff2de13`

V0 short BLE manifest: `{"v":1,"id":"watch-v0","caps":["button.primary"]}` (request sufficient MTU). V0 event byte `P` = `button.primary.pressed`; command byte `?` = ping, reply event byte `!`. These fixed short opcodes are a BLE transport codec, not the canonical JSON message contract. Future capability expansion requires version negotiation and fragmentation tests.

**Security gate:** initial BLE peripheral reference is for local bench testing only. Before action/media functionality, require BLE bonding, application-level authorization, replay protection as appropriate, and secure OTA. Do not ship the debug protocol directly.