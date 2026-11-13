"""Managed outbound WebSocket connector (FR-WS-001..005)."""

import asyncio
import importlib.util
import json
import unittest

from nikhi.adhara_sutra.websocket import ConnectorError, WebSocketClient

HAS_WEBSOCKETS = importlib.util.find_spec("websockets") is not None


@unittest.skipUnless(HAS_WEBSOCKETS, "websockets is not installed")
class WebSocketConnectorTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import websockets

        async def handler(websocket):
            async for message in websocket:
                await websocket.send(message)

        self.server = await websockets.serve(handler, "127.0.0.1", 0)
        port = self.server.sockets[0].getsockname()[1]
        self.url = f"ws://127.0.0.1:{port}"

    async def asyncTearDown(self):
        self.server.close()
        await self.server.wait_closed()

    async def test_connect_send_receive_and_close(self):
        async with WebSocketClient(self.url) as client:
            self.assertTrue(client.health())
            await client.send("hello")
            self.assertEqual(await client.receive(), "hello")
        self.assertFalse(client.connected)

    async def test_message_validation(self):
        async with WebSocketClient(self.url) as client:
            await client.send(json.dumps({"ok": True}))
            data = await client.receive(validate=json.loads)
            self.assertEqual(data, {"ok": True})
            await client.send("not-json")
            with self.assertRaises(ConnectorError) as caught:
                await client.receive(validate=json.loads)
        self.assertFalse(caught.exception.retryable)
        self.assertEqual(caught.exception.details.get("connector"), "websocket")

    async def test_receive_timeout_and_disconnected_errors(self):
        async with WebSocketClient(self.url) as client:
            with self.assertRaises(ConnectorError) as timeout:
                await client.receive(timeout=0.01)
            self.assertTrue(timeout.exception.retryable)
            await client.close()
            with self.assertRaises(ConnectorError) as closed:
                await client.send("x")
            self.assertFalse(closed.exception.retryable)

    async def test_controlled_reconnection(self):
        import websockets

        connections = {"count": 0}

        async def flaky(websocket):
            connections["count"] += 1
            await websocket.send(f"hello-{connections['count']}")
            if connections["count"] == 1:
                await websocket.close()
                return
            async for message in websocket:
                await websocket.send(message)

        server = await websockets.serve(flaky, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            async with WebSocketClient(f"ws://127.0.0.1:{port}", max_reconnects=1, reconnect_delay=0) as client:
                self.assertEqual(await client.receive(), "hello-1")
                # connection closed by server; next receive reconnects and reads welcome from new connection
                self.assertEqual(await client.receive(), "hello-2")
                await client.send("ping")
                self.assertEqual(await client.receive(), "ping")
            self.assertEqual(connections["count"], 2)
        finally:
            server.close()
            await server.wait_closed()


class WebSocketUnavailableTests(unittest.TestCase):
    def test_sync_context_is_rejected(self):
        client = WebSocketClient("ws://example.test")
        with self.assertRaises(ConnectorError):
            with client:
                pass


if __name__ == "__main__":
    unittest.main()
