import asyncio
import unittest

from udp.protocol import decode_frame, encode_frame, VERSION
from udp.simulator import VirtualWatch


class SimulatorTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.device = VirtualWatch()
        self.server = await asyncio.start_server(self.device.handle, "127.0.0.1", 0)
        self.port = self.server.sockets[0].getsockname()[1]

    async def asyncTearDown(self):
        self.server.close()
        await self.server.wait_closed()

    async def connect(self):
        reader, writer = await asyncio.open_connection("127.0.0.1", self.port)
        manifest = decode_frame(await reader.readline())
        self.assertEqual(manifest["capabilities"], ["button.primary"])
        return reader, writer

    async def test_ping(self):
        reader, writer = await self.connect()
        writer.write(encode_frame({"type": "command", "protocol": VERSION,
                                   "request_id": "1", "command": "device.ping"}))
        await writer.drain()
        result = decode_frame(await reader.readline())
        self.assertEqual(result["result"], {"alive": True})
        writer.close()
        await writer.wait_closed()

    async def test_button_press(self):
        reader, writer = await self.connect()
        writer.write(encode_frame({"type": "command", "protocol": VERSION,
                                   "request_id": "2", "command": "sim.button.press"}))
        await writer.drain()
        event = decode_frame(await reader.readline())
        result = decode_frame(await reader.readline())
        self.assertEqual(event["event"], "button.primary.pressed")
        self.assertEqual(event["seq"], 1)
        self.assertTrue(result["ok"])
        writer.close()
        await writer.wait_closed()

    async def test_unknown_command(self):
        reader, writer = await self.connect()
        writer.write(encode_frame({"type": "command", "protocol": VERSION,
                                   "request_id": "3", "command": "camera.capture"}))
        await writer.drain()
        response = decode_frame(await reader.readline())
        self.assertFalse(response["ok"])
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    unittest.main()
