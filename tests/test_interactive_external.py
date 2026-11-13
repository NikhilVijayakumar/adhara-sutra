"""Managed interactive external sessions (FR-EXT-010)."""

import sys
import unittest

from nikhi.adhara_sutra import ExternalCommand


class InteractiveExternalTests(unittest.IsolatedAsyncioTestCase):
    async def test_interactive_session_streams_io(self):
        # Python process that echoes lines from stdin
        code = "import sys\nfor line in sys.stdin:\n    print(line.strip().upper(), flush=True)\n"
        with ExternalCommand(sys.executable) as command:
            session = await command.open_session(["-u", "-c", code])
            try:
                await session.write("hello\n")
                stream, line = await session.receive(timeout=5)
                self.assertEqual(stream, "stdout")
                self.assertEqual(line.strip(), b"HELLO")
                await session.close_stdin()
                result = await session.wait(timeout=5)
                self.assertEqual(result.exit_code, 0)
            finally:
                await session.close()

    async def test_session_cleanup_on_close(self):
        with ExternalCommand(sys.executable) as command:
            session = await command.open_session(["-c", "import time; time.sleep(30)"])
            await session.close()
            self.assertIsNotNone(session.exit_code)


if __name__ == "__main__":
    unittest.main()
