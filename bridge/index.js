/**
 * AdharaSutra Electron/Node bridge.
 *
 * Spawns one Python application in persistent mode and speaks the versioned
 * newline-delimited JSON protocol over stdin/stdout. The command and arguments
 * are fixed when the bridge is created: callers can only send action names and
 * payloads, never commands, so renderer input cannot choose what is executed.
 */

import { spawn } from "node:child_process";
import { EventEmitter } from "node:events";
import { createInterface } from "node:readline";

export const PROTOCOL_VERSION = "1.0";

export class BridgeError extends Error {
  constructor(message, { code = "BRIDGE_ERROR", category = "bridge", retryable = null, details = undefined, response = undefined } = {}) {
    super(message);
    this.name = "BridgeError";
    this.code = code;
    this.category = category;
    this.retryable = retryable;
    this.details = details;
    this.response = response;
  }
}

export class Bridge extends EventEmitter {
  #command;
  #args;
  #cwd;
  #env;
  #child = null;
  #pending = new Map();
  #sequence = 0;
  #started = false;
  #ended = false;
  #expectedExit = false;

  constructor({ command, args = [], cwd, env = {}, defaultTimeoutMs = 0 } = {}) {
    super();
    if (typeof command !== "string" || !command) {
      throw new TypeError("command is required");
    }
    if (!Array.isArray(args) || args.some((arg) => typeof arg !== "string")) {
      throw new TypeError("args must be an array of strings");
    }
    if (!Number.isFinite(defaultTimeoutMs) || defaultTimeoutMs < 0) {
      throw new TypeError("defaultTimeoutMs must be a non-negative number");
    }
    this.#command = command;
    this.#args = [...args];
    this.#cwd = cwd;
    this.#env = { ...env };
    this.defaultTimeoutMs = defaultTimeoutMs;
  }

  get started() {
    return this.#started;
  }

  /** Spawn the backend and complete the persistent-mode handshake. */
  async start({ timeoutMs = 10000 } = {}) {
    if (this.#started) {
      return this;
    }
    if (this.#child) {
      throw new BridgeError("The bridge is already running or closing", { code: "BRIDGE_NOT_STARTABLE" });
    }
    const child = spawn(this.#command, this.#args, {
      cwd: this.#cwd,
      env: { ...process.env, ...this.#env },
      stdio: ["pipe", "pipe", "pipe"],
      windowsHide: true,
      shell: false,
    });
    this.#child = child;
    this.#started = false;
    this.#ended = false;
    this.#expectedExit = false;
    createInterface({ input: child.stdout }).on("line", (line) => this.#handleLine(line));
    createInterface({ input: child.stderr }).on("line", (line) => this.emit("stderr", line));
    child.on("exit", (code, signal) => this.#handleExit(code, signal));
    child.on("error", (error) => this.#handleProcessError(error));
    try {
      await new Promise((resolve, reject) => {
        child.once("spawn", resolve);
        child.once("error", reject);
      });
      const response = await this.#send("system.hello", {}, timeoutMs);
      const versions = response.data?.supported_protocol_versions;
      if (!Array.isArray(versions) || !versions.includes(PROTOCOL_VERSION)) {
        throw new BridgeError(`The backend does not support protocol ${PROTOCOL_VERSION}`, {
          code: "BRIDGE_PROTOCOL_UNSUPPORTED",
          response,
        });
      }
      if (this.#ended) {
        throw new BridgeError("The backend exited during startup", { code: "BRIDGE_PROCESS_EXITED" });
      }
      this.#started = true;
      return this;
    } catch (error) {
      this.#started = false;
      await this.close({ timeoutMs: 1000 }).catch(() => {});
      throw error instanceof BridgeError
        ? error
        : new BridgeError(`The backend failed to start: ${error.message}`, { code: "BRIDGE_START_FAILED", details: error });
    }
  }

  /** Send one action and resolve with its result data; reject on failure. */
  request(action, payload = {}, { timeoutMs = this.defaultTimeoutMs } = {}) {
    if (!this.#started) {
      return Promise.reject(new BridgeError("The bridge is not started", { code: "BRIDGE_NOT_STARTED" }));
    }
    if (typeof action !== "string" || !action) {
      return Promise.reject(new TypeError("action is required"));
    }
    return this.#send(action, payload, timeoutMs).then((response) => response.data);
  }

  /** Ask the runtime to cancel a managed job and report the outcome. */
  async cancel(jobId) {
    if (typeof jobId !== "string" || !jobId) {
      throw new TypeError("jobId is required");
    }
    return this.request("system.cancel", { job_id: jobId });
  }

  /** Read the status of a managed job, or null when it is unknown. */
  async jobStatus(jobId) {
    if (typeof jobId !== "string" || !jobId) {
      throw new TypeError("jobId is required");
    }
    return this.request("system.jobs.get", { job_id: jobId });
  }

  /** Report application readiness and connector health. */
  health() {
    return this.request("system.health");
  }

  /** List registered actions and jobs. */
  help() {
    return this.request("system.help");
  }

  /** Close stdin and wait for the backend to exit, killing it after a grace period. */
  async close({ timeoutMs = 2000 } = {}) {
    const child = this.#child;
    this.#started = false;
    this.#expectedExit = true;
    this.#rejectPending(new BridgeError("The bridge closed", { code: "BRIDGE_CLOSED" }));
    if (!child) {
      return;
    }
    if (this.#ended) {
      this.#child = null;
      return;
    }
    const exited = new Promise((resolve) => {
      child.once("exit", resolve);
      child.once("close", resolve);
    });
    child.stdin?.end();
    const timer = setTimeout(() => {
      if (child.exitCode === null) {
        child.kill();
      }
    }, timeoutMs);
    await Promise.race([exited, new Promise((resolve) => setTimeout(resolve, timeoutMs + 1000))]);
    clearTimeout(timer);
    this.#child = null;
  }

  #send(action, payload, timeoutMs) {
    const child = this.#child;
    if (!child || this.#ended) {
      return Promise.reject(new BridgeError("The backend is not running", { code: "BRIDGE_PROCESS_EXITED" }));
    }
    const requestId = `r${++this.#sequence}`;
    const envelope = { kind: "request", protocol_version: PROTOCOL_VERSION, request_id: requestId, action, payload };
    return new Promise((resolve, reject) => {
      const pending = { resolve, reject, timer: null };
      if (timeoutMs > 0) {
        pending.timer = setTimeout(() => {
          this.#pending.delete(requestId);
          reject(new BridgeError(`Request timed out after ${timeoutMs} ms`, {
            code: "BRIDGE_TIMEOUT",
            details: { request_id: requestId, action, outcome: "unknown", cancellation_requested: false },
          }));
        }, timeoutMs);
      }
      this.#pending.set(requestId, pending);
      try {
        child.stdin.write(`${JSON.stringify(envelope)}\n`, (error) => {
          if (!error) {
            return;
          }
          clearTimeout(pending.timer);
          this.#pending.delete(requestId);
          reject(new BridgeError(`Failed to write to the backend: ${error.message}`, {
            code: "BRIDGE_WRITE_FAILED",
            details: error,
          }));
        });
      } catch (error) {
        clearTimeout(pending.timer);
        this.#pending.delete(requestId);
        reject(new BridgeError(`Failed to write to the backend: ${error.message}`, {
          code: "BRIDGE_WRITE_FAILED",
          details: error,
        }));
      }
    });
  }

  #handleLine(line) {
    if (!line.trim()) {
      return;
    }
    let message;
    try {
      message = JSON.parse(line);
    } catch (error) {
      this.emit("protocolError", { line, error });
      return;
    }
    if (message?.kind === "event") {
      this.emit("event", message);
      return;
    }
    if (message?.kind !== "response" || typeof message.request_id !== "string") {
      this.emit("protocolError", { line, error: new Error("Unexpected protocol message") });
      return;
    }
    const pending = this.#pending.get(message.request_id);
    if (!pending) {
      this.emit("protocolError", { line, error: new Error("Uncorrelated response") });
      return;
    }
    this.#pending.delete(message.request_id);
    clearTimeout(pending.timer);
    if (message.success) {
      pending.resolve(message);
      return;
    }
    const info = message.error ?? {};
    pending.reject(new BridgeError(info.message ?? "The backend rejected the request", {
      code: info.code ?? "BRIDGE_REQUEST_FAILED",
      category: info.category ?? "internal",
      retryable: info.retryable ?? null,
      details: info.details,
      response: message,
    }));
  }

  #handleExit(code, signal) {
    this.#ended = true;
    this.#started = false;
    this.#rejectPending(new BridgeError(
      `The backend exited (code ${code ?? "null"}${signal ? `, signal ${signal}` : ""})`,
      { code: "BRIDGE_PROCESS_EXITED", details: { code, signal } },
    ));
    this.emit("exit", { code, signal, expected: this.#expectedExit });
  }

  #handleProcessError(error) {
    this.#ended = true;
    this.#started = false;
    this.emit("processError", error);
    this.#rejectPending(new BridgeError(`The backend process failed: ${error.message}`, {
      code: "BRIDGE_PROCESS_FAILED",
      details: error,
    }));
  }

  #rejectPending(error) {
    for (const pending of this.#pending.values()) {
      clearTimeout(pending.timer);
      pending.reject(error);
    }
    this.#pending.clear();
  }
}
