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

from .application import ConnectorError


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
                                         retryable=True,
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
