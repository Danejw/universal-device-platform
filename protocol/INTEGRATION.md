# Watch V0 integration contract

The canonical version is **udp/1**. Use `protocol/fixtures/watch-v0.json` as the machine-readable transport parity fixture. The ESP32 and Android integration must match its UUIDs, advertisement name, capability IDs and wire opcodes.

**Hardware:** XIAO ESP32S3 Sense. **Active:** `button.primary`. **Planned, NOT active:** camera, microphone, IMU, optical biometric sensor. No fabricated battery reading.

The **physical BLE v0** emits a single byte `P` for a button press; it does not emit a release event. Personal Voice must implement a **tap-to-toggle** action in the normal Assistant flow. Never route that to Companion's hold-to-talk gate, which needs both press and release to forward audio.

The **simulator** emits canonical `button.primary.pressed` events via its `sim.button.press` development command or the in-process virtual adapter. A BLE adapter converts `P` into exactly that event. Because BLE v0 has no event sequence number, receivers allocate a per-connection local sequence for logging and duplicate handling. Repeated legitimate taps must remain possible. Do not treat sequence numbers as cryptographic authentication, or rely on cooldown alone for BLE replay protection.

The source (`simulated` vs `physical`) is **host-verified transport metadata**. A device cannot self-promote to trusted or physical status by sending that text. Protocol/manifest parsing and capability validation are distinct from pairing and authorization.

Security and validation gates for the physical adapter: real discoverable service UUID, bounded recent native scan ID, BLE permissions, readable manifest, capabilities `["button.primary"]`, event CCCD subscription before connected status, explicit owner authorization, reconnect cancellation, and no image/audio or side-effect commands until a secured transport exists.

No new Gemini tool declaration or DeviceLink session is necessary for button input.
