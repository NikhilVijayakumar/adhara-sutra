"""Packaged desktop runtime discovery for supported platforms (FR-PKG-005, FR-PKG-006)."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Iterable, Mapping

ENV_VARIABLE = "ADHARA_PYTHON"
_NAMES = {"win32": ("python.exe",), "darwin": ("python3", "python")}
_DEFAULT_NAMES = ("python3", "python")
_SUPPORTED = ("win32", "darwin", "linux")


class RuntimeDiscoveryError(RuntimeError):
    """No usable Python backend could be located for a packaged application."""


def supported_platforms() -> tuple[str, ...]:
    """Return the desktop platforms with a defined backend-discovery mechanism."""
    return _SUPPORTED


def locate_backend(*, app_root: str | Path | None = None,
                   bundled: Iterable[str | Path] = (),
                   env: Mapping[str, str] | None = None) -> str:
    """Resolve the Python backend executable for a packaged application.

    Resolution order: the ``ADHARA_PYTHON`` override, bundled interpreter paths
    (relative to ``app_root`` when given), platform interpreter names on
    ``PATH``, then the running interpreter.
    """
    environment = os.environ if env is None else env
    override = environment.get(ENV_VARIABLE)
    if override:
        path = Path(override)
        if not path.is_file():
            raise RuntimeDiscoveryError(f"{ENV_VARIABLE} does not point to a file: {override}")
        return str(path.resolve())
    root = Path(app_root) if app_root is not None else None
    for candidate in bundled:
        path = Path(candidate)
        if root is not None:
            path = root / path
        if path.is_file():
            return str(path.resolve())
    for name in _NAMES.get(sys.platform, _DEFAULT_NAMES):
        found = shutil.which(name)
        if found:
            return found
    if Path(sys.executable).is_file():
        return sys.executable
    raise RuntimeDiscoveryError(f"No Python backend found; set {ENV_VARIABLE} or bundle an interpreter")
