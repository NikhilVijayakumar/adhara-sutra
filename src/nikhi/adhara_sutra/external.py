"""Managed execution of external CLI programs without a shell."""

from __future__ import annotations

import asyncio
import os
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping

from .application import ConnectorError as _ConnectorError


class ConnectorError(_ConnectorError):
    """External-command connector failure that reports its connector identity."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, connector="external", **kwargs)


@dataclass(frozen=True)
class CommandResult:
    """The captured outcome of one external command."""

    exit_code: int
    stdout: bytes
    stderr: bytes
    duration: float

    @property
    def ok(self) -> bool:
        return self.exit_code == 0

    @property
    def stdout_text(self) -> str:
        return self.stdout.decode("utf-8", errors="replace")

    @property
    def stderr_text(self) -> str:
        return self.stderr.decode("utf-8", errors="replace")

    def raise_for_status(self) -> "CommandResult":
        """Raise a connector error when the command exited non-zero."""
        if self.exit_code != 0:
            raise ConnectorError(f"External command exited with {self.exit_code}",
                                 retryable=False, details={"exit_code": self.exit_code})
        return self


class ExternalSession:
    """A managed interactive external process with streamed output and stdin."""

    def __init__(self, process: asyncio.subprocess.Process, command: "ExternalCommand",
                 started: float) -> None:
        self._process = process
        self._command = command
        self.started = started
        self._output: asyncio.Queue[tuple[str, bytes] | None] = asyncio.Queue()
        self._stdout = asyncio.create_task(self._pump(process.stdout, "stdout"))
        self._stderr = asyncio.create_task(self._pump(process.stderr, "stderr"))
        self._closed = False

    async def _pump(self, stream: asyncio.StreamReader | None, name: str) -> None:
        if stream is None:
            return
        while True:
            line = await stream.readline()
            if not line:
                return
            await self._output.put((name, line))

    @property
    def exit_code(self) -> int | None:
        return self._process.returncode

    async def write(self, data: bytes | str) -> None:
        """Write data to the process stdin."""
        if self._process.stdin is None:
            raise ConnectorError("Interactive session stdin is not available", retryable=False)
        payload = data if isinstance(data, bytes) else data.encode()
        try:
            self._process.stdin.write(payload)
            await self._process.stdin.drain()
        except (BrokenPipeError, ConnectionResetError, OSError) as exc:
            raise ConnectorError(f"Interactive session stdin failed: {exc}", retryable=False) from exc

    async def close_stdin(self) -> None:
        if self._process.stdin is None:
            return
        try:
            self._process.stdin.close()
            await self._process.stdin.wait_closed()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    async def receive(self, timeout: float | None = None) -> tuple[str, bytes] | None:
        """Receive the next (stream, line) output item, or None at EOF."""
        if self._stdout.done() and self._stderr.done() and self._output.empty():
            return None
        try:
            if timeout is None:
                item = await self._output.get()
            else:
                item = await asyncio.wait_for(self._output.get(), timeout)
        except asyncio.TimeoutError as exc:
            raise ConnectorError("Interactive session output timed out",
                                 retryable=True, code="CONNECTOR_TIMEOUT") from exc
        return item

    async def __aiter__(self):
        while True:
            if self._stdout.done() and self._stderr.done() and self._output.empty():
                return
            item = await self._output.get()
            if item is None:
                return
            yield item

    async def wait(self, timeout: float | None = None) -> CommandResult:
        """Wait for the process to exit and return its captured streams/duration."""
        if timeout is not None:
            try:
                await asyncio.wait_for(self._process.wait(), timeout)
            except asyncio.TimeoutError:
                await self._command._terminate(self._process)
                raise ConnectorError("Interactive session timed out", retryable=True,
                                     code="CONNECTOR_TIMEOUT", details={"outcome": "unknown"})
        else:
            await self._process.wait()
        for task in (self._stdout, self._stderr):
            try:
                await asyncio.wait_for(task, 2)
            except Exception:
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
        # drain remaining queued output is not needed for result; result built from queue consumers not kept
        return CommandResult(exit_code=self._process.returncode if self._process.returncode is not None else -1,
                             stdout=b"", stderr=b"", duration=time.monotonic() - self.started)

    async def close(self) -> None:
        """Terminate the session and release process resources."""
        if self._closed:
            return
        self._closed = True
        try:
            if self._process.returncode is None:
                await self._command._terminate(self._process)
        finally:
            self._stdout.cancel()
            self._stderr.cancel()
            await asyncio.gather(self._stdout, self._stderr, return_exceptions=True)
            self._command._processes.discard(self._process)


class ExternalCommand:
    """Runs one configured executable with structured arguments and managed cleanup."""

    def __init__(self, executable: str, *, search_path: str | None = None,
                 env: Mapping[str, str] | None = None, cwd: str | None = None,
                 max_concurrent: int = 0, kill_timeout: float = 5.0) -> None:
        if not isinstance(max_concurrent, int) or max_concurrent < 0:
            raise ValueError("max_concurrent must be a non-negative integer")
        if not isinstance(kill_timeout, (int, float)) or isinstance(kill_timeout, bool) or kill_timeout <= 0:
            raise ValueError("kill_timeout must be a positive number")
        self.executable = executable
        self.search_path = search_path
        self.env = dict(env or {})
        self.cwd = cwd
        self.max_concurrent = max_concurrent
        self.kill_timeout = kill_timeout
        self.path: str | None = None
        self._processes: set[asyncio.subprocess.Process] = set()
        self._semaphore = asyncio.Semaphore(max_concurrent) if max_concurrent else None
        self._parsers: dict[str, Callable[[CommandResult], Any]] = {}

    def register_parser(self, name: str, parser: Callable[[CommandResult], Any]) -> None:
        """Register an application-supplied parser for a captured command result."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("parser name must be a non-empty string")
        if not callable(parser):
            raise TypeError("parser must be callable")
        if name in self._parsers:
            raise ValueError(f"parser already registered: {name}")
        self._parsers[name] = parser

    def parse(self, name: str, result: CommandResult) -> Any:
        """Apply a registered parser to a result, including non-zero exit results."""
        try:
            parser = self._parsers[name]
        except KeyError:
            raise ValueError(f"unknown parser: {name}") from None
        return parser(result)

    def __enter__(self) -> "ExternalCommand":
        path = shutil.which(self.executable, path=self.search_path) \
            if not os.path.dirname(self.executable) else self.executable
        if not path or not os.path.isfile(path):
            raise ConnectorError(f"Executable not found: {self.executable}", retryable=False)
        self.path = os.path.abspath(path)
        return self

    def __exit__(self, *exc: Any) -> bool:
        for process in list(self._processes):
            if process.returncode is None:
                self._kill_sync(process)
        self._processes.clear()
        self.path = None
        return False

    def health(self) -> bool:
        return bool(self.path) and os.path.isfile(self.path)

    async def run(self, args: Iterable[str] = (), *, timeout: float | None = None,
                  input: bytes | str | None = None, cwd: str | None = None,
                  env: Mapping[str, str] | None = None,
                  on_output: Callable[[str, bytes], None] | None = None) -> CommandResult:
        """Run the executable and capture or stream its output."""
        if self._semaphore is None:
            return await self._run(args, timeout=timeout, input=input, cwd=cwd, env=env, on_output=on_output)
        async with self._semaphore:
            return await self._run(args, timeout=timeout, input=input, cwd=cwd, env=env, on_output=on_output)

    async def open_session(self, args: Iterable[str] = (), *, cwd: str | None = None,
                           env: Mapping[str, str] | None = None) -> ExternalSession:
        """Start a managed interactive session for the configured executable."""
        if self.path is None:
            raise ConnectorError("The external command connector is not started", retryable=False)
        if isinstance(args, (str, bytes)):
            raise ConnectorError("External command arguments must be a sequence, not a command string",
                                 retryable=False)
        args = tuple(args)
        if not all(isinstance(argument, str) for argument in args):
            raise ConnectorError("External command arguments must be strings", retryable=False)
        command_env = {**os.environ, **self.env, **(env or {})}
        options: dict[str, Any] = {}
        if sys.platform != "win32":
            options["start_new_session"] = True
        try:
            process = await asyncio.create_subprocess_exec(
                self.path, *args,
                stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE, cwd=cwd or self.cwd, env=command_env, **options)
        except (OSError, ValueError) as exc:
            raise ConnectorError(f"Failed to start {self.path}: {exc}", retryable=False,
                                 details={"outcome": "not_sent"}) from exc
        self._processes.add(process)
        return ExternalSession(process, self, time.monotonic())

    async def _run(self, args: Iterable[str] = (), *, timeout: float | None = None,
                   input: bytes | str | None = None, cwd: str | None = None,
                   env: Mapping[str, str] | None = None,
                   on_output: Callable[[str, bytes], None] | None = None) -> CommandResult:
        """Run the executable without applying the concurrency limit."""
        if self.path is None:
            raise ConnectorError("The external command connector is not started", retryable=False)
        if isinstance(args, (str, bytes)):
            raise ConnectorError("External command arguments must be a sequence, not a command string",
                                 retryable=False)
        args = tuple(args)
        if not all(isinstance(argument, str) for argument in args):
            raise ConnectorError("External command arguments must be strings", retryable=False)
        command_env = {**os.environ, **self.env, **(env or {})}
        options: dict[str, Any] = {}
        if sys.platform != "win32":
            options["start_new_session"] = True
        try:
            process = await asyncio.create_subprocess_exec(
                self.path, *args,
                stdin=asyncio.subprocess.PIPE if input is not None else asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                cwd=cwd or self.cwd, env=command_env, **options)
        except (OSError, ValueError) as exc:
            raise ConnectorError(f"Failed to start {self.path}: {exc}", retryable=False,
                                 details={"outcome": "not_sent"}) from exc
        self._processes.add(process)
        stdout: list[bytes] = []
        stderr: list[bytes] = []
        readers = [asyncio.create_task(self._read(process.stdout, "stdout", stdout, on_output)),
                   asyncio.create_task(self._read(process.stderr, "stderr", stderr, on_output))]
        started = time.monotonic()

        async def feed_and_wait() -> None:
            if input is not None:
                payload = input if isinstance(input, bytes) else input.encode()
                try:
                    process.stdin.write(payload)
                    await process.stdin.drain()
                    process.stdin.close()
                    await process.stdin.wait_closed()
                except (BrokenPipeError, ConnectionResetError):
                    pass
            await process.wait()

        try:
            if timeout is not None:
                try:
                    await asyncio.wait_for(feed_and_wait(), timeout)
                except asyncio.TimeoutError:
                    await self._terminate(process)
                    raise ConnectorError(f"{os.path.basename(self.path)} timed out after {timeout} seconds",
                                         retryable=True, code="CONNECTOR_TIMEOUT",
                                         details={"timeout": timeout, "outcome": "unknown"}) from None
            else:
                await feed_and_wait()
            try:
                await asyncio.wait_for(asyncio.gather(*readers), 5)
            except asyncio.TimeoutError:
                pass
        finally:
            if process.returncode is None:
                await self._terminate(process)
            for reader in readers:
                if not reader.done():
                    reader.cancel()
            await asyncio.gather(*readers, return_exceptions=True)
            self._processes.discard(process)
        return CommandResult(exit_code=process.returncode if process.returncode is not None else -1,
                             stdout=b"".join(stdout), stderr=b"".join(stderr),
                             duration=time.monotonic() - started)

    async def _read(self, stream: asyncio.StreamReader | None, name: str,
                    sink: list[bytes], callback: Callable[[str, bytes], None] | None) -> None:
        if stream is None:
            return
        while True:
            line = await stream.readline()
            if not line:
                return
            sink.append(line)
            if callback is not None:
                callback(name, line)

    async def _terminate(self, process: asyncio.subprocess.Process) -> None:
        if process.returncode is not None:
            return
        if sys.platform == "win32":
            try:
                killer = await asyncio.create_subprocess_exec(
                    "taskkill", "/PID", str(process.pid), "/T", "/F",
                    stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
                await killer.wait()
            except OSError:
                pass
        else:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                try:
                    process.terminate()
                except ProcessLookupError:
                    pass
        try:
            await asyncio.wait_for(process.wait(), self.kill_timeout)
        except asyncio.TimeoutError:
            if sys.platform == "win32":
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
            else:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
            await process.wait()

    def _kill_sync(self, process: asyncio.subprocess.Process) -> None:
        if sys.platform == "win32":
            try:
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                               capture_output=True, check=False,
                               creationflags=subprocess.CREATE_NO_WINDOW)
                return
            except OSError:
                pass
        else:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                return
            except (ProcessLookupError, PermissionError):
                pass
        try:
            process.kill()
        except ProcessLookupError:
            pass
