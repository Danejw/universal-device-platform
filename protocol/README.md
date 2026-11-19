# UDP/1 device contract

UDP = **Universal Device Platform**.

`udp/1` is a **semantic protocol**, independent of BLE, localhost TCP, or future Wi-Fi media transports.

## Canonical messages

Each message is a UTF-8 JSON object. Required fields:

- **manifest**: `{"type":"manifest","protocol":"udp/1","device_id":"watch-v0","firmware_version":"sim-0.1.0","capabilities":["button.primary"]}`
- **command**: `{"type":"command","protocol":"udp/1","request_id":"r1","command":"device.ping"}`
- **event**: `{"type":"event","protocol":"udp/1","device_id":"watch-v0","event":"button.primary.pressed","seq":1}`
- **response**: `{"type":"response","protocol":"udp/1","request_id":"r1","ok":true,"result":{}}`

The transport is responsible for authorization, reliable framing, disconnect detection, and rate limits. Unknown major protocol versions must be rejected. A capability must be listed only if it can actually be used.

## Simulator-only commands

`sim.button.press` triggers `button.primary.pressed` in the local simulator. It is intentionally excluded from physical firmware. `device.ping` works for both simulator and firmware once the BLE adapter is connected.

## Localhost TCP framing

One newline-terminated JSON object per message, maximum 4096 bytes including newline, bound to 127.0.0.1 by default. A manifest is sent on connection. A command yields a response (and optionally events). The simulator is **never** a security boundary or a production transport.

## BLE GATT v0

Fixed UUIDs in [docs/ROADMAP.md](../docs/ROADMAP.md). The ESP32 publishes a short version/capability manifest and button notifications. The Android adapter translates the BLE wire representation into canonical messages. MTU negotiation and read/notification chunking must be verified on real devices before extending the wire protocol. Media must not be pushed through the initial BLE event characteristic.

## Capability namespaces

- `button.primary`: sends `button.primary.pressed`
- `motion.imu`: planned, not active
- `camera.capture`: planned, not active
- `microphone.record`: planned, not active
- `biometrics.heart_rate`: planned, not active

Protocol changes need fixtures plus compatibility tests. No assumption of medically accurate metrics.