import unittest
from unittest.mock import patch

try:
    import httpx
except ImportError:
    httpx = None

from nikhi.adhara_sutra import ConnectorError, HttpClient


@unittest.skipIf(httpx is None, "HTTP extra is not installed")
class HttpRetryTests(unittest.TestCase):
    def client(self, handler, **policy):
        real_client = httpx.Client
        factory = lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs)
        return patch.object(httpx, "Client", side_effect=factory), HttpClient(**policy)

    def test_safe_request_retries_status_and_transport_failure(self):
        calls = []
        def handler(request):
            calls.append(request.method)
            if len(calls) == 1:
                raise httpx.ConnectError("offline", request=request)
            return httpx.Response(503 if len(calls) == 2 else 200)
        mock, client = self.client(handler, max_retries=2, retry_delay=0.01)
        with mock, patch("nikhi.adhara_sutra.http.time.sleep") as sleep, client:
            self.assertEqual(client.get("https://example.test").status, 200)
        self.assertEqual(calls, ["GET"] * 3)
        self.assertEqual(sleep.call_count, 2)

    def test_unsafe_methods_and_default_policy_do_not_retry(self):
        calls = []
        def handler(request):
            calls.append(request.method)
            return httpx.Response(503)
        mock, client = self.client(handler, max_retries=2)
        with mock, client:
            self.assertEqual(client.post("https://example.test").status, 503)
            self.assertEqual(client.put("https://example.test").status, 503)
        mock, client = self.client(handler)
        with mock, client:
            self.assertEqual(client.get("https://example.test").status, 503)
        self.assertEqual(calls, ["POST", "PUT", "GET"])

    def test_exhaustion_preserves_failure_and_nontransient_does_not_retry(self):
        calls = []
        def handler(request):
            calls.append(1)
            raise httpx.ReadTimeout("timeout", request=request)
        mock, client = self.client(handler, max_retries=1)
        with mock, client, self.assertRaises(ConnectorError) as caught:
            client.get("https://example.test")
        self.assertEqual(len(calls), 2)
        self.assertEqual(caught.exception.details["outcome"], "unknown")
        calls.clear()
        def permanent(request):
            calls.append(1)
            raise httpx.UnsupportedProtocol("bad scheme", request=request)
        mock, client = self.client(permanent, max_retries=2)
        with mock, client, self.assertRaises(ConnectorError) as caught:
            client.get("https://example.test")
        self.assertEqual(len(calls), 1)
        self.assertFalse(caught.exception.retryable)

    def test_exhausted_status_is_returned(self):
        calls = []
        def handler(request):
            calls.append(1)
            return httpx.Response(503)
        mock, client = self.client(handler, max_retries=1)
        with mock, client:
            self.assertEqual(client.get("https://example.test").status, 503)
        self.assertEqual(len(calls), 2)

    def test_policy_validation(self):
        for policy in ({"max_retries": -1}, {"max_retries": True},
                       {"retry_delay": float("nan")}, {"retry_delay": -1}):
            with self.subTest(policy=policy), self.assertRaises(ValueError):
                HttpClient(**policy)
