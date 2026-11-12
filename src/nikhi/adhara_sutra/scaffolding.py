"""Deterministic project scaffolding for ``adhara new``."""

from __future__ import annotations

import keyword
import re
from pathlib import Path

PROFILES = ("minimal", "cli")
CONNECTORS = ("http", "sqlite", "external")

_GITIGNORE = """__pycache__/
*.py[cod]
*.egg-info/
.venv/
dist/
build/
.pytest_cache/
"""


def _package_name(name: str) -> str:
    candidate = re.sub(r"[^0-9a-zA-Z_]+", "_", name).strip("_").lower()
    if not candidate:
        return "app"
    return f"app_{candidate}" if candidate[0].isdigit() else candidate


def _pyproject(name: str, package: str, profile: str, connectors: tuple[str, ...]) -> str:
    dependency = "nikhi-adhara-sutra[http]" if "http" in connectors else "nikhi-adhara-sutra"
    scripts = ""
    if profile == "cli":
        scripts = f'\n[project.scripts]\n"{name}" = "{package}.cli:main"\n'
    return f"""[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
description = "{name} application"
requires-python = ">=3.12"
dependencies = ["{dependency}"]

[project.optional-dependencies]
test = ["pytest>=8"]
{scripts}
[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
pythonpath = ["src"]
"""


def _service_imports(connectors: tuple[str, ...]) -> tuple[list[str], list[str]]:
    imports, services = [], []
    if "http" in connectors:
        imports.append("HttpClient")
        services.append('app.service("http", lambda context: HttpClient(base_url="https://api.example.com"))')
    if "sqlite" in connectors:
        imports.append("SQLiteDatabase")
        services.append('app.service("database", lambda context: SQLiteDatabase("app.db"))')
    if "external" in connectors:
        imports.append("ExternalCommand")
        services.append('app.service("commands", lambda context: ExternalCommand("git"))')
    return imports, services


def _app_py(name: str, profile: str, connectors: tuple[str, ...]) -> str:
    extra_imports, services = _service_imports(connectors)
    names = ["Application", *extra_imports]
    lines = [
        f'"""{name} application."""',
        "",
        f"from nikhi.adhara_sutra import {', '.join(names)}",
        "",
    ]
    if profile == "cli":
        lines += ["from .actions import register", ""]
    lines += [f"app = Application(name={name!r}, version=\"0.1.0\")", ""]
    if profile == "cli":
        lines += ["register(app)"]
    else:
        lines += [
            '@app.action("greeting.create")',
            "def greeting_create(payload, context):",
            '    """Return a greeting for the supplied name."""',
            '    return {"message": f"Hello, {payload.get(\'name\', \'world\')}!"}',
        ]
    lines += services
    return "\n".join(lines) + "\n"


def _readme(name: str, package: str, profile: str, connectors: tuple[str, ...]) -> str:
    run = f"python -m {package}"
    if profile == "cli":
        run = f"{name}  # or: python -m {package}"
    selected = ", ".join(connectors) or "none"
    return f"""# {name}

Generated with AdharaSutra using the `{profile}` profile.

Connectors: {selected}

## Run

```bash
pip install -e ".[test]"
{run}
```

Use `--persistent` for the JSON-line session protocol. `adhara run src/{package}/app.py`
serves the same application without installing it.

## Test

```bash
pytest
```
"""


def _test_py(package: str) -> str:
    return f'''"""Smoke test for the generated application."""

import asyncio

from nikhi.adhara_sutra import ApplicationTestClient

from {package}.app import app


def test_greeting():
    async def run():
        async with ApplicationTestClient(app) as client:
            assert await client.call("greeting.create", {{"name": "Ada"}}) == {{"message": "Hello, Ada!"}}

    asyncio.run(run())
'''


def _entry_point(package: str, profile: str) -> str:
    if profile == "cli":
        return f'''"""Module entry point for {package}."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
'''
    return f'''"""Module entry point for {package}."""

import sys

from .app import app


def main() -> int:
    return app.run(persistent="--persistent" in sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _files(name: str, package: str, profile: str, connectors: tuple[str, ...]) -> dict[str, str]:
    files = {
        "pyproject.toml": _pyproject(name, package, profile, connectors),
        "README.md": _readme(name, package, profile, connectors),
        ".gitignore": _GITIGNORE,
        f"src/{package}/__init__.py": f'"""{name} package."""\n',
        f"src/{package}/app.py": _app_py(name, profile, connectors),
        f"src/{package}/__main__.py": _entry_point(package, profile),
        "tests/test_app.py": _test_py(package),
    }
    if profile == "cli":
        files[f"src/{package}/actions/__init__.py"] = (
            '"""Application actions."""\n\nfrom .greeting import register\n\n__all__ = ["register"]\n'
        )
        files[f"src/{package}/actions/greeting.py"] = (
            '"""Greeting actions."""\n\n\n'
            "def register(app):\n"
            '    @app.action("greeting.create")\n'
            "    def greeting_create(payload, context):\n"
            '        """Return a greeting for the supplied name."""\n'
            '        return {"message": f"Hello, {payload.get(\'name\', \'world\')}!"}\n'
        )
        files[f"src/{package}/cli.py"] = f'''"""Console entry point for {name}."""

import sys

from .app import app


def main() -> int:
    return app.run(persistent="--persistent" in sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
'''
    return files


def generate(target: str | Path, *, name: str | None = None, package: str | None = None,
             profile: str = "minimal", connectors: tuple[str, ...] | list[str] = (),
             force: bool = False) -> list[str]:
    """Write a new project and return its created relative paths."""
    root = Path(target)
    if root.exists() and not root.is_dir():
        raise ValueError(f"not a directory: {root}")
    name = (name or root.resolve().name).strip()
    if not name or any(character in name for character in ('"', "\\", "\n")):
        raise ValueError("an application name without quotes, backslashes, or newlines is required")
    package = (package or _package_name(name)).strip()
    if not package.isidentifier() or keyword.iskeyword(package):
        raise ValueError(f"invalid Python package name: {package}")
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}")
    connectors = tuple(dict.fromkeys(connectors))
    unknown = [connector for connector in connectors if connector not in CONNECTORS]
    if unknown:
        raise ValueError(f"unsupported connector(s): {', '.join(unknown)}")
    files = _files(name, package, profile, connectors)
    conflicts = [str(root / relative) for relative in files if (root / relative).exists()]
    if conflicts and not force:
        raise ValueError("refusing to overwrite existing files (use --force): " + ", ".join(conflicts))
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return list(files)
