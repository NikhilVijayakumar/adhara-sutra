import json
import unittest
from uuid import uuid4

from nikhi.adhara_sutra import Application, ApplicationTestClient


class DomainError(Exception):
    pass


class SpecificError(DomainError):
    pass


class ErrorMappingTests(unittest.IsolatedAsyncioTestCase):
    async def test_most_specific_mapping_wins_and_hides_internal_detail(self):
        app = Application("mapping_" + uuid4().hex, "1.0")
        app.map_error(DomainError, code="ACTION_VALIDATION_FAILED", message="Invalid domain input")
        app.map_error(SpecificError, code="CONNECTOR_FAILURE", message="Upstream unavailable",
                      retryable=True)

        @app.action("fail")
        def fail(payload, context):
            raise DomainError("secret detail")

        @app.action("specific")
        def specific(payload, context):
            raise SpecificError("secret detail")
        async with ApplicationTestClient(app) as client:
            with self.assertLogs("nikhi.adhara_sutra.application", level="ERROR") as logs:
                response = await client.dispatch("fail")
                self.assertFalse(response["success"])
                error = response["error"]
                self.assertEqual(error["code"], "ACTION_VALIDATION_FAILED")
                self.assertEqual(error["category"], "validation")
                self.assertEqual(error["message"], "Invalid domain input")
                self.assertFalse(error["retryable"])
                self.assertNotIn("secret detail", json.dumps(response))
                specific_error = (await client.dispatch("specific"))["error"]
            self.assertEqual(specific_error["code"], "CONNECTOR_FAILURE")
            self.assertEqual(specific_error["category"], "connector")
            self.assertTrue(specific_error["retryable"])
            self.assertIn("secret detail", "\n".join(logs.output))

    async def test_registration_is_validated_and_closed_after_startup(self):
        app = Application("mapping_" + uuid4().hex, "1.0")
        for exception_type, code, message in ((str, "CONNECTOR_FAILURE", "message"),
                                             (DomainError, "UNKNOWN_CODE", "message"),
                                             (DomainError, "CONNECTOR_FAILURE", " ")):
            with self.subTest(code=code), self.assertRaises((TypeError, ValueError)):
                app.map_error(exception_type, code=code, message=message)
        app.map_error(DomainError, code="CONNECTOR_FAILURE", message="message")
        with self.assertRaises(ValueError):
            app.map_error(DomainError, code="CONNECTOR_FAILURE", message="message")
        await app.start()
        try:
            with self.assertRaises(ValueError):
                app.map_error(KeyError, code="CONNECTOR_FAILURE", message="message")
        finally:
            await app.stop()


if __name__ == "__main__":
    unittest.main()
