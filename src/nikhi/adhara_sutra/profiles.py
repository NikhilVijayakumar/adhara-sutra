"""Built-in architecture profile selection for generated and inspected projects."""

from __future__ import annotations

import json
import keyword
import tomllib
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from .verification import ArchitectureProfile, DEFAULT_MANDATORY_RULES

PROFILE_REGISTRY = {"minimal": ("1",), "cli": ("1",)}
PROFILES = tuple(PROFILE_REGISTRY)


def _relative_path(value: Any, root: Path) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("profile paths must be nonempty relative POSIX paths")
    path, windows = PurePosixPath(value), PureWindowsPath(value)
    if path.is_absolute() or windows.is_absolute() or windows.drive or any(part in ("..", ".") for part in value.split("/")):
        raise ValueError(f"profile path must be project-relative: {value!r}")
    if not (root / value).resolve().is_relative_to(root.resolve()):
        raise ValueError(f"profile path escapes the project: {value!r}")
    return path.as_posix()


def resolve_profile(root: str | Path, *, name: str | None = None,
                    version: str | None = None,
                    captured_files: dict[str, bytes] | None = None) -> ArchitectureProfile:
    """Resolve explicit overrides, project metadata, then minimal/1."""
    root = Path(root)
    project_file = root / "pyproject.toml"
    metadata: dict[str, Any] = {}
    if ("pyproject.toml" in captured_files if captured_files is not None else project_file.exists()):
        try:
            content = captured_files["pyproject.toml"].decode("utf-8") if captured_files is not None else project_file.read_text(encoding="utf-8")
            data = tomllib.loads(content)
        except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
            raise ValueError(f"invalid project metadata: {exc}") from exc
        tool = data.get("tool", {})
        if not isinstance(tool, dict) or not isinstance(tool.get("adhara", {}), dict):
            raise ValueError("tool.adhara must be a table")
        metadata = tool.get("adhara", {})
    for key in ("profile", "profile_version", "package"):
        if key in metadata and (not isinstance(metadata[key], str) or not metadata[key]):
            raise ValueError(f"tool.adhara.{key} must be a nonempty string")
    selected = name if name is not None else metadata.get("profile", "minimal")
    selected_version = version if version is not None else metadata.get("profile_version", "1")
    if selected not in PROFILE_REGISTRY or selected_version not in PROFILE_REGISTRY[selected]:
        raise ValueError(f"unsupported architecture profile: {selected}/{selected_version}")
    package = metadata.get("package")
    if package is not None and (not package.isidentifier() or keyword.iskeyword(package)):
        raise ValueError("tool.adhara.package must be a Python package name")
    required_files = ["pyproject.toml"]
    required_directories = ["src"]
    if selected == "cli":
        if not package:
            raise ValueError("cli profile requires tool.adhara.package in pyproject.toml")
        required_files += [f"src/{package}/__init__.py", f"src/{package}/app.py",
                           f"src/{package}/__main__.py", f"src/{package}/cli.py",
                           f"src/{package}/actions/__init__.py", f"src/{package}/actions/greeting.py"]
        required_directories += [f"src/{package}", f"src/{package}/actions"]
    config: dict[str, Any] = {}
    config_file = root / ".adhara-profile.json"
    if (".adhara-profile.json" in captured_files if captured_files is not None else config_file.exists()):
        try:
            content = captured_files[".adhara-profile.json"].decode("utf-8") if captured_files is not None else config_file.read_text(encoding="utf-8")
            config = json.loads(content)
        except (OSError, UnicodeError, ValueError) as exc:
            raise ValueError(f"invalid profile configuration: {exc}") from exc
        if not isinstance(config, dict) or set(config) - {"required_files", "required_directories", "forbidden_imports", "layer_boundaries"}:
            raise ValueError("invalid profile configuration fields")
    def paths(key: str) -> list[str]:
        values = config.get(key, [])
        if not isinstance(values, list):
            raise ValueError(f"{key} must be a list")
        return [_relative_path(value, root) for value in values]
    def tuples(key: str, length: int) -> tuple[tuple[str, ...], ...]:
        values = config.get(key, [])
        if not isinstance(values, list) or any(not isinstance(item, list) or len(item) != length or
                any(not isinstance(part, str) or not part for part in item) for item in values):
            raise ValueError(f"{key} must contain lists of {length} nonempty strings")
        return tuple(tuple(item) for item in values)
    forbidden = tuples("forbidden_imports", 2)
    layers = tuple((_relative_path(source, root), imported, remediation)
                   for source, imported, remediation in tuples("layer_boundaries", 3))
    return ArchitectureProfile(version=selected_version, name=selected,
        required_files=tuple(dict.fromkeys(required_files + paths("required_files"))),
        required_directories=tuple(dict.fromkeys(required_directories + paths("required_directories"))),
        forbidden_imports=forbidden, layer_boundaries=layers,
        mandatory_rules=DEFAULT_MANDATORY_RULES + ("ARCH-STRUCT-002",))
