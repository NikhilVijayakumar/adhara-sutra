"""Standard application directories and path-confined file access."""

from __future__ import annotations

import os
import json
import shutil
import sys
import tempfile
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Iterator, Mapping


class PathViolation(ValueError):
    """A requested path escapes the configured access boundary."""


@dataclass(frozen=True)
class AppDirectories:
    """Resolved data, configuration, cache, log, and temporary directories."""

    data: Path
    config: Path
    cache: Path
    logs: Path
    temp: Path

    @classmethod
    def for_app(cls, name: str, *, base: str | os.PathLike | None = None,
                env: Mapping[str, str] | None = None,
                platform: str | None = None) -> "AppDirectories":
        """Resolve the directories for an application, using platform conventions."""
        if not isinstance(name, str) or not name or name in (".", "..") \
                or "/" in name or "\\" in name:
            raise ValueError("Application name must be a non-empty path segment")
        environment = os.environ if env is None else env
        platform = platform or sys.platform
        if base is not None:
            root = Path(base).expanduser().resolve()
            return cls(root / "data", root / "config", root / "cache", root / "logs", root / "temp")
        if platform == "win32":
            local = Path(environment.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
            roaming = Path(environment.get("APPDATA") or Path.home() / "AppData" / "Roaming")
            data, config, cache, logs = local / name, roaming / name, local / name / "Cache", local / name / "Logs"
        else:
            home = Path.home()
            data = Path(environment.get("XDG_DATA_HOME") or home / ".local" / "share") / name
            config = Path(environment.get("XDG_CONFIG_HOME") or home / ".config") / name
            cache = Path(environment.get("XDG_CACHE_HOME") or home / ".cache") / name
            logs = Path(environment.get("XDG_STATE_HOME") or home / ".local" / "state") / name / "logs"
        temp = Path(tempfile.gettempdir()) / name
        return cls(data.expanduser(), config.expanduser(), cache.expanduser(), logs.expanduser(), temp)

    def ensure(self) -> "AppDirectories":
        """Create every directory that does not exist yet."""
        for directory in (self.data, self.config, self.cache, self.logs, self.temp):
            directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        return self

    @contextmanager
    def temporary(self, prefix: str = "tmp") -> Iterator[Path]:
        """Create a temporary directory inside the application temp directory."""
        self.temp.mkdir(parents=True, exist_ok=True, mode=0o700)
        path = Path(tempfile.mkdtemp(prefix=prefix, dir=self.temp))
        try:
            yield path
        finally:
            shutil.rmtree(path, ignore_errors=True)


class PathBoundary:
    """Resolves paths inside configured roots, rejecting traversal and escaping links."""

    def __init__(self, *roots: str | os.PathLike) -> None:
        if not roots:
            raise ValueError("At least one boundary root is required")
        self.roots = tuple(Path(root).expanduser().resolve() for root in roots)

    def resolve(self, path: str | os.PathLike, *, must_exist: bool = False) -> Path:
        """Resolve a path against the first root and confirm it stays inside a root."""
        candidate = Path(path).expanduser()
        if not candidate.is_absolute():
            candidate = self.roots[0] / candidate
        resolved = candidate.resolve(strict=must_exist)
        if any(resolved == root or root in resolved.parents for root in self.roots):
            return resolved
        raise PathViolation(f"Path escapes the configured boundary: {path}")

    def open(self, path: str | os.PathLike, mode: str = "r", **kwargs) -> Any:
        """Open a file inside the boundary; read modes require the file to exist."""
        return self.resolve(path, must_exist=mode.startswith("r")).open(mode, **kwargs)

    def read_text(self, path: str | os.PathLike, *, encoding: str = "utf-8") -> str:
        """Read a text file within the boundary."""
        return self.resolve(path, must_exist=True).read_text(encoding=encoding)

    def write_text(self, path: str | os.PathLike, content: str, *, encoding: str = "utf-8") -> int:
        """Write text within the boundary; the parent directory must already exist."""
        return self.resolve(path).write_text(content, encoding=encoding)

    def read_json(self, path: str | os.PathLike, *, encoding: str = "utf-8") -> Any:
        """Read and decode JSON within the boundary."""
        return json.loads(self.read_text(path, encoding=encoding))

    def write_json(self, path: str | os.PathLike, value: Any, *, encoding: str = "utf-8") -> int:
        """Encode and write JSON within the boundary."""
        return self.write_text(path, json.dumps(value, ensure_ascii=False, allow_nan=False), encoding=encoding)


class ArtifactStore:
    """Store large binary artifacts under opaque identifiers in a managed directory."""

    def __init__(self, directory: str | os.PathLike) -> None:
        self.directory = Path(directory).expanduser().resolve()
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)

    @staticmethod
    def _validate_id(artifact_id: str) -> str:
        if not isinstance(artifact_id, str) or len(artifact_id) != 32:
            raise ValueError("Invalid artifact identifier")
        try:
            parsed = uuid.UUID(hex=artifact_id)
        except ValueError:
            raise ValueError("Invalid artifact identifier") from None
        if parsed.hex != artifact_id:
            raise ValueError("Invalid artifact identifier")
        return artifact_id

    def put(self, source: BinaryIO, *, media_type: str = "application/octet-stream") -> dict[str, Any]:
        """Copy a binary stream incrementally and return a JSON-compatible reference."""
        if not isinstance(media_type, str) or not media_type.strip():
            raise ValueError("media_type must be a non-empty string")
        artifact_id = uuid.uuid4().hex
        path = self.directory / artifact_id
        size = 0
        with path.open("xb") as output:
            try:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not isinstance(chunk, bytes):
                        raise TypeError("artifact source must be a binary stream")
                    if not chunk:
                        break
                    output.write(chunk)
                    size += len(chunk)
            except BaseException:
                output.close()
                path.unlink(missing_ok=True)
                raise
        return {"artifact_id": artifact_id, "size_bytes": size, "media_type": media_type}

    def open(self, artifact_id: str) -> BinaryIO:
        """Open an artifact for binary reading; the caller must close the file."""
        path = self.directory / self._validate_id(artifact_id)
        if path.is_symlink():
            raise PathViolation("Artifact must not be a symbolic link")
        return path.open("rb")

    def delete(self, artifact_id: str) -> None:
        """Delete an artifact when the application no longer needs it."""
        (self.directory / self._validate_id(artifact_id)).unlink()
