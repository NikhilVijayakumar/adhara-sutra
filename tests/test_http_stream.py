import unittest
from unittest.mock import patch

try:
    import httpx
except ImportError:
    httpx = None

from nikhi.adhara_sutra import ConnectorError, HttpClient


@unittest.skipIf(httpx is None, "HTTP extra is not installed")
class HttpStreamTests(unittest.TestCase):
    def test_incremental_consumption_and_early_close(self):
        class Body(httpx.SyncByteStream):
            closed = False
            def __iter__(self):
                yield b"first"
                yield b"second"
            def close(self):
                self.closed = True
        body = Body()
        real = httpx.Client
        with patch.object(httpx, "Client", side_effect=lambda **kw: real(
                transport=httpx.MockTransport(lambda req: httpx.Response(200, stream=body)), **kw)):
            with HttpClient() as client:
                with client.stream("GET", "https://example.test") as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(next(response.iter_bytes()), b"first")
                    self.assertFalse(body.closed)
                self.assertTrue(body.closed)

    def test_read_failure_is_translated_and_closed(self):
        class Body(httpx.SyncByteStream):
            closed = False
            def __iter__(self):
                yield b"part"
                raise httpx.ReadError("disconnected")
            def close(self):
                self.closed = True
        body = Body()
        real = httpx.Client
        with patch.object(httpx, "Client", side_effect=lambda **kw: real(
                transport=httpx.MockTransport(lambda req: httpx.Response(200, stream=body)), **kw)):
            with HttpClient() as client:
                with self.assertRaises(ConnectorError) as caught:
                    with client.stream("GET", "https://example.test") as response:
                        list(response.iter_bytes())
        self.assertTrue(body.closed)
        self.assertEqual(caught.exception.details["outcome"], "unknown")

    def test_open_failure_and_unstarted_client(self):
        with self.assertRaises(ConnectorError):
            with HttpClient().stream("GET", "https://example.test"):
                pass
        def fail(request):
            raise httpx.ConnectError("offline", request=request)
        real = httpx.Client
        with patch.object(httpx, "Client", side_effect=lambda **kw: real(
                transport=httpx.MockTransport(fail), **kw)):
            with HttpClient(max_retries=2) as client:
                with self.assertRaises(ConnectorError) as caught:
                    with client.stream("GET", "https://example.test"):
                        pass
        self.assertEqual(caught.exception.details["outcome"], "not_sent")
