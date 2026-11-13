"""The shipped CLI contract suite runs against a minimal application (FR-TEST-002)."""

import unittest
from uuid import uuid4

from nikhi.adhara_sutra import Application, CLIContractTests


class ShippedContractTests(CLIContractTests):
    def create_application(self):
        app = Application(f"contract_{uuid4().hex}", "1.0")

        @app.action("ping")
        def ping(payload, context):
            return {"pong": True}
        return app


if __name__ == "__main__":
    unittest.main()
