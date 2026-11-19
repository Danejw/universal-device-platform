"""Small, strict canonical JSON message contract for UDP/1 (Universal Device Platform)."""

import json

VERSION = "udp/1"
MAX_FRAME_BYTES = 4096
TYPES = frozenset(("manifest", "event", "command", "response"))


class ProtocolError(ValueError):
    """A malformed or unsupported device message."""


def validate_message(message):
    if not isinstance(message, dict):
        raise ProtocolError("Message must be an object")
    if message.get("protocol") != VERSION:
        raise ProtocolError("Unsupported protocol version")
    kind = message.get("type")
    if kind not in TYPES:
        raise ProtocolError("Unknown message type")
    if kind == "manifest":
        if not isinstance(message.get("device_id"), str) or not message["device_id"]:
            raise ProtocolError("Manifest requires device_id")
        if not isinstance(message.get("firmware_version"), str):
            raise ProtocolError("Manifest requires firmware_version")
        capabilities = message.get("capabilities")
        if not isinstance(capabilities, list) or not all(
            isinstance(item, str) and item for item in capabilities
        ) or len(capabilities) != len(set(capabilities)):
            raise ProtocolError("Capabilities must be unique nonempty strings")
    elif kind == "event":
        if not isinstance(message.get("device_id"), str) or not message["device_id"]:
            raise ProtocolError("Event requires device_id")
        if not isinstance(message.get("event"), str) or not message["event"]:
            raise ProtocolError("Event requires event")
        if type(message.get("seq")) is not int or message["seq"] < 0:
            raise ProtocolError("Event requires nonnegative sequence")
    elif kind == "command":
        if not isinstance(message.get("command"), str) or not message["command"]:
            raise ProtocolError("Command name required")
        if not isinstance(message.get("request_id"), str) or not message["request_id"]:
            raise ProtocolError("Command request_id required")
    else:
        if not isinstance(message.get("request_id"), str) or not message["request_id"]:
            raise ProtocolError("Response request_id required")
        if type(message.get("ok")) is not bool:
            raise ProtocolError("Response requires boolean ok")
    return message


def encode_frame(message):
    validate_message(message)
    line = json.dumps(message, separators=(",", ":"), ensure_ascii=True) + "\n"
    data = line.encode("utf-8")
    if len(data) > MAX_FRAME_BYTES:
        raise ProtocolError("Frame exceeds maximum size")
    return data


def decode_frame(data):
    if not isinstance(data, bytes):
        raise ProtocolError("Frame must be bytes")
    if not data.endswith(b"\n") or len(data) > MAX_FRAME_BYTES:
        raise ProtocolError("Missing newline or oversized frame")
    try:
        message = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolError("Malformed JSON frame") from exc
    return validate_message(message)
