"""Reference UDP/1 BLE notification codec, separate from canonical JSON.

Watch V0 emits one-byte notifications: P (button), ! (ping acknowledgement).
BLE has no on-wire event sequence, so a receiver supplies a monotonically
increasing connection-local sequence number when normalizing.
"""

from udp.protocol import VERSION, validate_message, ProtocolError

BUTTON = b"P"
PONG = b"!"
PING = b"?"


def normalize_notification(data: bytes, device_id: str, sequence: int) -> dict:
    if data == BUTTON:
        event = "button.primary.pressed"
    elif data == PONG:
        event = "device.pong"
    else:
        raise ProtocolError("Unsupported UDP/1 watch notification")
    return validate_message({
        "type": "event",
        "protocol": VERSION,
        "device_id": device_id,
        "event": event,
        "seq": sequence,
    })


def encode_ble_command(command: str) -> bytes:
    if command == "device.ping":
        return PING
    raise ProtocolError("Command is unavailable on watch V0")
