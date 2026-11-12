import base64
import unittest
from unittest.mock import patch

try:
    import httpx
except ImportError:
    httpx = None

from nikhi.adhara_sutra import HttpClient


@unittest.skipIf(httpx is None, "HTTP extra is not installed")
class HttpAuthenticationTests(unittest.TestCase):
    def test_basic_and_bearer_credentials_are_sent(self):
        seen = []
        def respond(request):
            seen.append(request.headers.get("Authorization"))
            return httpx.Response(200, text="ok")

        real_client = httpx.Client
        def client_with_transport(**kwargs):
            return real_client(transport=httpx.MockTransport(respond), **kwargs)

        with patch.object(httpx, "Client", side_effect=client_with_transport):
            with HttpClient(auth=("user", "password")) as client:
                self.assertTrue(client.get("https://example.test/").ok)
            with HttpClient(headers={"Authorization": "Bearer example-token"}) as client:
                self.assertTrue(client.get("https://example.test/").ok)
        expected = base64.b64encode(b"user:password").decode("ascii")
        self.assertEqual(seen, [f"Basic {expected}", "Bearer example-token"])


if __name__ == "__main__":
    unittest.main()
