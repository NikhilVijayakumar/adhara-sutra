"""Configuration source merging and diagnostics (FR-CFG-002/004/006/007/008)."""

import json
import os
import tempfile
import unittest
from uuid import uuid4

from nikhi.adhara_sutra import Application, BootstrapError


def application(label, **options):
    return Application(f"config_{label}_{uuid4().hex}", "1.0", **options)


class ConfigurationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._config_env = {key: value for key, value in os.environ.items()
                            if key.startswith("ADHARA_CONFIG_")}
        self._clear_env()
        self.addCleanup(self._restore_env)

    def _clear_env(self):
        for key in [key for key in os.environ if key.startswith("ADHARA_CONFIG_")]:
            del os.environ[key]

    def _restore_env(self):
        self._clear_env()
        os.environ.update(self._config_env)

    def file_with(self, content):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = os.path.join(directory.name, "config.json")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return path

    def missing_path(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        return os.path.join(directory.name, "missing.json")

    async def test_unreadable_config_file_names_path_and_source(self):
        path = self.missing_path()
        app = application("missing", config_file=path)
        with self.assertRaises(BootstrapError) as raised:
            await app.start()
        message = str(raised.exception)
        self.assertEqual(raised.exception.code, "INVALID_CONFIGURATION")
        self.assertIn(path, message)
        self.assertIn("config_file", message)
        self.assertIsInstance(raised.exception.__cause__, OSError)
        self.assertEqual(app.state, "failed")

    async def test_environment_selected_config_file_names_the_variable(self):
        os.environ["ADHARA_CONFIG_FILE"] = self.missing_path()
        app = application("environment")
        with self.assertRaises(BootstrapError) as raised:
            await app.start()
        self.assertIn("ADHARA_CONFIG_FILE", str(raised.exception))

    async def test_malformed_or_non_object_config_file_is_actionable(self):
        for content, expected in (("{", "not valid JSON"), ("[]", "must contain an object")):
            with self.subTest(expected=expected):
                path = self.file_with(content)
                with self.assertRaises(BootstrapError) as raised:
                    await application("file", config_file=path).start()
                self.assertIn(path, str(raised.exception))
                self.assertIn(expected, str(raised.exception))

    async def test_sources_merge_in_documented_precedence(self):
        path = self.file_with(json.dumps({"value": "file", "file_only": 1, "count": 1}))
        os.environ["ADHARA_CONFIG_VALUE"] = json.dumps("environment")
        os.environ["ADHARA_CONFIG_COUNT"] = "3"
        app = application("merge", config={"value": "default", "base_only": True}, config_file=path)
        app.override_config({"value": "override"})
        await app.start()
        self.addAsyncCleanup(app.stop)
        config = app.context.config
        self.assertEqual(config["value"], "override")
        self.assertEqual(config["count"], 3)
        self.assertEqual(config["file_only"], 1)
        self.assertIs(config["base_only"], True)

    async def test_non_json_environment_values_fall_back_to_strings(self):
        os.environ["ADHARA_CONFIG_LABEL"] = "plain text"
        app = application("label", config={"label": "default"})
        await app.start()
        self.addAsyncCleanup(app.stop)
        self.assertEqual(app.context.config["label"], "plain text")

    async def test_invalid_configuration_blocks_services_and_keeps_the_cause(self):
        started = []

        def validate_config(config):
            if not isinstance(config.get("name"), str):
                raise ValueError("name must be a string")
            return config

        app = application("invalid", config={"name": 0}, validate_config=validate_config)
        app.service("service", lambda context: started.append(True))
        with self.assertRaises(BootstrapError) as raised:
            await app.start()
        self.assertIn("name must be a string", str(raised.exception))
        self.assertEqual(started, [])
        self.assertIsInstance(raised.exception.__cause__, ValueError)
        self.assertEqual(app.state, "failed")


if __name__ == "__main__":
    unittest.main()
