import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import { Bridge, BridgeError } from "../index.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..", "..");
const candidate = [
  process.env.ADHARA_TEST_PYTHON,
  path.join(root, ".venv", "Scripts", "python.exe"),
  path.join(root, ".venv", "bin", "python"),
].filter(Boolean).find((value) => existsSync(value));
const python = candidate || (process.platform === "win32" ? "python" : "python3");
const fixture = path.join(here, "fixture_app.py");
const env = {
  ...process.env,
  PYTHONPATH: [path.join(root, "src"), here].join(path.delimiter),
};

test("bridge fixes the backend command at construction", () => {
  assert.throws(() => new Bridge({ command: "" }), TypeError);
  assert.throws(() => new Bridge({ command: "python", args: ["-c", 1] }), TypeError);
});

test("bridge drives a representative Python runtime fixture", async () => {
  const bridge = new Bridge({
    command: python,
    args: [fixture, "--persistent"],
    cwd: root,
    env,
    defaultTimeoutMs: 20000,
  });
  try {
    await bridge.start();
    const result = await bridge.request("greeting.create", { name: "Ada" });
    assert.equal(result.message, "Hello, Ada!");
    const help = await bridge.help();
    assert.ok(help.actions.some((action) => action.name === "greeting.create"));
    await assert.rejects(
      bridge.request("broken.action", {}),
      (error) => error instanceof BridgeError && error.code === "RUNTIME_EXECUTION_FAILED",
    );
  } finally {
    await bridge.close();
  }
});
