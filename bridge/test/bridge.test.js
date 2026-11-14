import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { mkdtemp, rm, rmdir, writeFile } from "node:fs/promises";
import os from "node:os";
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
    for (const invalid of ["", null, 42]) {
      await assert.rejects(bridge.jobStatus(invalid), TypeError);
    }
    assert.deepEqual(await bridge.jobStatus("missing"), { job_id: "missing", status: null });
    const { job_id } = await bridge.request("report.submit", { name: "Ada" });
    const deadline = Date.now() + 5000;
    let status;
    do {
      ({ status } = await bridge.jobStatus(job_id));
      if (status?.state === "succeeded") break;
      if (status?.state === "failed") throw new Error(`Job failed: ${JSON.stringify(status)}`);
      await new Promise((resolve) => setTimeout(resolve, 20));
    } while (Date.now() < deadline);
    assert.equal(status?.state, "succeeded", "Timed out waiting for the submitted job to succeed");
    assert.equal(status.job_id, job_id);
    assert.deepEqual(status.result, { message: "Report for Ada" });
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


test("timeout leaves the operation running and reports the late response", async () => {
  const directory = await mkdtemp(path.join(os.tmpdir(), "adhara-timeout-"));
  const release = path.join(directory, "release");
  const bridge = new Bridge({
    command: python,
    args: [fixture, "--persistent"],
    cwd: root,
    env: { ...env, ADHARA_TEST_RELEASE_FILE: release },
    defaultTimeoutMs: 10000,
  });
  const waitFor = (eventName, predicate, timeoutMs = 5000) => new Promise((resolve, reject) => {
    const listener = (value) => {
      if (!predicate(value)) return;
      clearTimeout(timer);
      bridge.off(eventName, listener);
      resolve(value);
    };
    const timer = setTimeout(() => {
      bridge.off(eventName, listener);
      reject(new Error(`Timed out waiting for ${eventName}`));
    }, timeoutMs);
    bridge.on(eventName, listener);
  });
  try {
    await bridge.start();
    const entered = waitFor("event", (event) => event.event === "fixture.entered");
    const finished = waitFor("event", (event) => event.event === "fixture.finished");
    const late = waitFor("protocolError", ({ error }) => error.message === "Uncorrelated response");
    const request = bridge.request("fixture.wait", {}, { timeoutMs: 1000 });
    let timeoutRequestId;
    const timedOut = assert.rejects(request, (error) => {
      assert.ok(error instanceof BridgeError);
      assert.equal(error.code, "BRIDGE_TIMEOUT");
      assert.equal(typeof error.details.request_id, "string");
      timeoutRequestId = error.details.request_id;
      assert.equal(error.details.action, "fixture.wait");
      assert.equal(error.details.outcome, "unknown");
      assert.equal(error.details.cancellation_requested, false);
      return true;
    });
    const enteredEvent = await entered;
    await timedOut;
    assert.equal(enteredEvent.request_id, timeoutRequestId);
    await writeFile(release, "release");
    await finished;
    const lateResponse = await late;
    const lateMessage = JSON.parse(lateResponse.line);
    assert.equal(lateMessage.request_id, timeoutRequestId);
    assert.equal(lateMessage.data.finished, true);
    assert.deepEqual(await bridge.request("greeting.create", { name: "Ada" }), { message: "Hello, Ada!" });
  } finally {
    await writeFile(release, "release").catch(() => {});
    await bridge.close();
    await rm(release, { force: true });
    await rmdir(directory);
  }
});
