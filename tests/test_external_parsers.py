import json
import sys
import unittest

from nikhi.adhara_sutra import ExternalCommand


class ExternalParserTests(unittest.IsolatedAsyncioTestCase):
    async def test_registered_parsers_receive_complete_results(self):
        with ExternalCommand(sys.executable) as command:
            command.register_parser("json", lambda result: json.loads(result.stdout_text))
            command.register_parser("diagnostic", lambda result: (result.exit_code, result.stderr_text.strip()))
            result = await command.run(["-c", "import json; print(json.dumps({'value': 42}))"])
            self.assertEqual(command.parse("json", result), {"value": 42})
            failed = await command.run(["-c", "import sys; print('problem', file=sys.stderr); sys.exit(3)"])
            self.assertEqual(command.parse("diagnostic", failed), (3, "problem"))

    async def test_registration_and_parser_errors(self):
        command = ExternalCommand(sys.executable)
        with self.assertRaises(ValueError):
            command.register_parser("", lambda result: result)
        with self.assertRaises(TypeError):
            command.register_parser("invalid", None)
        command.register_parser("broken", lambda result: 1 / 0)
        with self.assertRaises(ValueError):
            command.register_parser("broken", lambda result: result)
        with ExternalCommand(sys.executable) as other:
            result = await other.run(["-c", "pass"])
        with self.assertRaises(ValueError):
            command.parse("missing", result)
        with self.assertRaises(ZeroDivisionError):
            command.parse("broken", result)
