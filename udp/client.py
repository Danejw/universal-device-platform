"""One-shot CLI consumer of the virtual watch contract."""

import argparse
import asyncio
import json
import uuid

from udp.protocol import VERSION, decode_frame, encode_frame


async def execute(action, host="127.0.0.1", port=8765):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        manifest = decode_frame(await asyncio.wait_for(reader.readline(), timeout=5))
        print(json.dumps(manifest, indent=2))
        if manifest["type"] != "manifest":
            raise RuntimeError("Server did not send manifest")
        request_id = str(uuid.uuid4())
        writer.write(encode_frame({
            "type": "command", "protocol": VERSION,
            "request_id": request_id, "command": action,
        }))
        await writer.drain()
        while True:
            msg = decode_frame(await asyncio.wait_for(reader.readline(), timeout=5))
            print(json.dumps(msg, indent=2))
            if msg["type"] == "response" and msg["request_id"] == request_id:
                if not msg["ok"]:
                    raise RuntimeError(msg.get("error", "Command failed"))
                return
    finally:
        writer.close()
        await writer.wait_closed()


def main():
    parser = argparse.ArgumentParser(description="Virtual wearable client")
    parser.add_argument("action", nargs="?", choices=("ping", "press"), default="press")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    asyncio.run(execute("device.ping" if args.action == "ping" else "sim.button.press", port=args.port))


if __name__ == "__main__":
    main()
