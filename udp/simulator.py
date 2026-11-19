"""Local-only virtual watch with canonical JSON commands and events."""

import argparse
import asyncio
import json
import logging

from udp.builder import make_manifest
from udp.hardware import read_json, WATCH
from udp.protocol import MAX_FRAME_BYTES, ProtocolError, VERSION, decode_frame, encode_frame

WATCH_CONFIG = read_json(WATCH)
DEVICE_ID = WATCH_CONFIG["id"]
MANIFEST = make_manifest(WATCH_CONFIG, "sim-0.1.0")


class VirtualWatch:
    def __init__(self):
        self.next_sequence = 0

    async def handle(self, reader, writer):
        peer = writer.get_extra_info("peername")
        logging.info("Client connected: %s", peer)
        try:
            writer.write(encode_frame(MANIFEST))
            await writer.drain()
            while True:
                data = await reader.readline()
                if not data:
                    break
                request_id = None
                try:
                    if len(data) > MAX_FRAME_BYTES:
                        raise ProtocolError("Frame too large")
                    cmd = decode_frame(data)
                    if cmd["type"] != "command":
                        raise ProtocolError("Expected command")
                    request_id = cmd["request_id"]
                    action = cmd["command"]
                    if action == "device.ping":
                        result = {"alive": True}
                    elif action == "sim.button.press":
                        self.next_sequence += 1
                        writer.write(encode_frame({
                            "type": "event", "protocol": VERSION, "device_id": DEVICE_ID,
                            "event": "button.primary.pressed", "seq": self.next_sequence,
                        }))
                        result = {"event_emitted": True}
                    else:
                        raise ProtocolError("Unsupported command: " + action)
                    response = {"type": "response", "protocol": VERSION,
                                "request_id": request_id, "ok": True, "result": result}
                except ProtocolError as exc:
                    response = {"type": "response", "protocol": VERSION,
                                "request_id": request_id or "invalid", "ok": False,
                                "error": str(exc)}
                writer.write(encode_frame(response))
                await writer.drain()
        except (ConnectionError, asyncio.IncompleteReadError):
            pass
        finally:
            writer.close()
            await writer.wait_closed()
            logging.info("Client disconnected: %s", peer)


async def serve(host="127.0.0.1", port=8765):
    # Localhost-only by default. Never expose this simulator on a network.
    watch = VirtualWatch()
    server = await asyncio.start_server(watch.handle, host, port, limit=MAX_FRAME_BYTES + 1)
    sockets = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print("Virtual watch listening on " + sockets, flush=True)
    async with server:
        await server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Virtual UDP/1 wristband")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(serve(port=args.port))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
