"""Static inspection of an existing Python project for architecture reporting."""

from __future__ import annotations

import ast
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

_EXCLUDED = {".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist",
             ".mypy_cache", ".pytest_cache", ".tox"}
_JS_SUFFIXES = {".js", ".mjs", ".cjs", ".ts", ".tsx"}
_INTEGRATIONS = {
    "httpx": "HTTP", "requests": "HTTP", "aiohttp": "HTTP", "urllib": "HTTP", "urllib3": "HTTP",
    "websockets": "WebSocket", "websocket": "WebSocket",
    "sqlite3": "SQLite",
    "subprocess": "external CLI",
    "shutil": "filesystem",
    "pathlib": "filesystem",
}
_CLI_TOOLS = {"argparse", "click", "typer", "fire"}
_ELECTRON = {
    "electron-process": re.compile(r"child_process|spawn\(|execFile\(|fork\("),
    "electron-ipc": re.compile(r"ipcMain|ipcRenderer|contextBridge"),
}
# shortcut: other executors (concurrent.futures, loop.create_task) are not detected yet; extend here when needed.
_UNMANAGED = {"asyncio": ("create_task", "ensure_future"), "threading": ("Thread", "Timer")}


@dataclass(frozen=True)
class Evidence:
    """One source location supporting a finding."""

    path: str
    line: int
    snippet: str


@dataclass(frozen=True)
class Finding:
    """A source-backed fact or inference about the project."""

    kind: str
    name: str
    confidence: str = "observed"
    detail: str = ""
    evidence: tuple[Evidence, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "name": self.name, "confidence": self.confidence,
                "detail": self.detail, "evidence": [asdict(item) for item in self.evidence]}


@dataclass
class ProjectProfile:
    """The result of inspecting one project directory."""

    root: str
    revision: str | None
    dirty: bool | None
    files: list[str]
    modules: list[str]
    dependencies: list[dict[str, Any]]
    findings: list[Finding]
    errors: list[Finding]
    imports: dict[str, list[Evidence]]  # full dotted names, analysed but not serialized in reports

    def by_kind(self, kind: str) -> list[Finding]:
        return [finding for finding in self.findings if finding.kind == kind]

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": self.root,
            "revision": self.revision,
            "dirty": self.dirty,
            "files": self.files,
            "modules": self.modules,
            "dependencies": self.dependencies,
            "findings": [finding.to_dict() for finding in self.findings],
            "errors": [error.to_dict() for error in self.errors],
        }


class ProjectInspector:
    """Discover entry points, framework usage, integrations, and dependencies from source."""

    def __init__(self, root: str | Path, *, exclude: Iterable[str] = ()) -> None:
        self.root = Path(root).resolve()
        self.exclude = _EXCLUDED | set(exclude)

    def inspect(self) -> ProjectProfile:
        if not self.root.is_dir():
            raise ValueError(f"Not a directory: {self.root}")
        files = [path for path in sorted(self.root.rglob("*"))
                 if path.is_file() and not self._excluded(path)]
        python_files = [path for path in files if path.suffix == ".py"]
        modules = [self._module_name(path) for path in python_files]
        findings: list[Finding] = []
        errors: list[Finding] = []
        imports: dict[str, list[Evidence]] = {}
        module_imports: dict[str, list[Evidence]] = {}
        for path in python_files:
            self._inspect_python(path, findings, errors, imports, module_imports)
        for path in files:
            if path.suffix in _JS_SUFFIXES:
                self._inspect_javascript(path, findings)
        self._inspect_scripts(findings)
        self._inspect_imports(imports, findings)
        revision, dirty = _revision(self.root)
        return ProjectProfile(
            root=str(self.root),
            revision=revision,
            dirty=dirty,
            files=[self._relative(path) for path in files],
            modules=modules,
            dependencies=_classify(imports, modules),
            findings=_dedupe(findings),
            errors=errors,
            imports=module_imports,
        )

    def _excluded(self, path: Path) -> bool:
        return any(part in self.exclude for part in path.relative_to(self.root).parts)

    def _relative(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def _module_name(self, path: Path) -> str:
        parts = list(path.relative_to(self.root).with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        return ".".join(parts) or "__root__"

    def _inspect_python(self, path: Path, findings: list[Finding], errors: list[Finding],
                        imports: dict[str, list[Evidence]],
                        module_imports: dict[str, list[Evidence]]) -> None:
        relative = self._relative(path)
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            errors.append(Finding("read_error", relative, "observed", str(exc)))
            return
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            errors.append(Finding("parse_error", relative, "observed", str(exc),
                                  (Evidence(relative, exc.lineno or 0, (exc.text or "").strip()[:200]),)))
            return
        lines = source.splitlines()

        def evidence(node: ast.AST) -> Evidence:
            line = getattr(node, "lineno", 0)
            snippet = lines[line - 1].strip()[:200] if 0 < line <= len(lines) else ""
            return Evidence(relative, line, snippet)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    _add_import(imports, alias.name, evidence(node))
                    module_imports.setdefault(alias.name, []).append(evidence(node))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    _add_import(imports, node.module, evidence(node))
                resolved = _resolve_import(node, relative)
                if resolved:
                    module_imports.setdefault(resolved, []).append(evidence(node))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    if (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute)
                            and decorator.func.attr in ("action", "job")
                            and decorator.args and isinstance(decorator.args[0], ast.Constant)
                            and isinstance(decorator.args[0].value, str)):
                        findings.append(Finding(decorator.func.attr, decorator.args[0].value, "observed",
                                                f"handler {node.name}", (evidence(decorator),)))
            elif isinstance(node, ast.Call):
                self._inspect_call(node, evidence, findings)
            elif isinstance(node, ast.Attribute):
                if node.attr in ("state", "session_state", "request_state") \
                        and isinstance(node.value, ast.Name) and node.value.id == "context":
                    findings.append(Finding("state", f"context.{node.attr}", "observed", "",
                                            (evidence(node),)))
                elif node.attr == "jobs" and isinstance(node.value, ast.Name) and node.value.id == "context":
                    findings.append(Finding("job_access", "context.jobs", "observed", "",
                                            (evidence(node),)))
                elif node.attr == "argv" and isinstance(node.value, ast.Name) and node.value.id == "sys":
                    findings.append(Finding("cli", "sys.argv", "inferred", "manual argument parsing",
                                            (evidence(node),)))
                elif node.attr in ("stdin", "stdout") and isinstance(node.value, ast.Name) \
                        and node.value.id == "sys":
                    findings.append(Finding("protocol_bypass", f"sys.{node.attr}", "observed",
                                            "direct standard stream access", (evidence(node),)))
            elif isinstance(node, ast.If) and _is_main_guard(node.test):
                findings.append(Finding("entry_point", "__main__", "observed", "module script entry",
                                        (evidence(node),)))

    def _inspect_call(self, node: ast.Call, evidence: Any, findings: list[Finding]) -> None:
        function = node.func
        if isinstance(function, ast.Name) and function.id == "print":
            findings.append(Finding("protocol_bypass", "print()", "inferred",
                                    "writes directly to stdout", (evidence(node),)))
        elif isinstance(function, ast.Name) and function.id == "open":
            findings.append(Finding("integration", "filesystem", "inferred", "open() call",
                                    (evidence(node),)))
        elif isinstance(function, ast.Name) and function.id == "Application":
            name = "<unnamed>"
            for keyword in node.keywords:
                if keyword.arg == "name" and isinstance(keyword.value, ast.Constant) \
                        and isinstance(keyword.value.value, str):
                    name = keyword.value.value
            findings.append(Finding("application", name, "observed", "", (evidence(node),)))
        elif isinstance(function, ast.Attribute):
            if function.attr == "service" and node.args and isinstance(node.args[0], ast.Constant) \
                    and isinstance(node.args[0].value, str):
                findings.append(Finding("service", node.args[0].value, "observed", "",
                                        (evidence(node),)))
            elif function.attr == "run" and isinstance(function.value, ast.Name) \
                    and function.value.id in ("app", "application"):
                findings.append(Finding("entry_point", f"{function.value.id}.run()", "observed",
                                        "application runtime entry", (evidence(node),)))
            elif isinstance(function.value, ast.Name) \
                    and function.attr in _UNMANAGED.get(function.value.id, ()):
                findings.append(Finding("unmanaged_task", f"{function.value.id}.{function.attr}",
                                        "inferred", "unmanaged background work", (evidence(node),)))

    def _inspect_javascript(self, path: Path, findings: list[Finding]) -> None:
        relative = self._relative(path)
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return
        for number, line in enumerate(lines, 1):
            for kind, pattern in _ELECTRON.items():
                if pattern.search(line):
                    findings.append(Finding(kind, relative, "observed", "", (Evidence(relative, number, line.strip()[:200]),)))

    def _inspect_scripts(self, findings: list[Finding]) -> None:
        pyproject = self.root / "pyproject.toml"
        if pyproject.is_file():
            try:
                data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            except (OSError, tomllib.TOMLDecodeError):
                data = {}
            scripts = data.get("project", {}).get("scripts", {})
            if isinstance(scripts, dict):
                for name, target in scripts.items():
                    findings.append(Finding("entry_point", str(name), "observed",
                                            f"console script -> {target}",
                                            (Evidence("pyproject.toml", 0, f"[project.scripts] {name}"),)))
        setup_cfg = self.root / "setup.cfg"
        if setup_cfg.is_file():
            try:
                lines = setup_cfg.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                lines = []
            in_console_scripts = False
            for number, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("[") and stripped.endswith("]"):
                    in_console_scripts = stripped == "[options.entry_points]"
                elif in_console_scripts and "=" in stripped:
                    name, target = stripped.split("=", 1)
                    findings.append(Finding("entry_point", name.strip(), "observed",
                                            f"console script -> {target.strip()}",
                                            (Evidence("setup.cfg", number, stripped[:200]),)))

    def _inspect_imports(self, imports: dict[str, list[Evidence]], findings: list[Finding]) -> None:
        for name, locations in sorted(imports.items()):
            if name in _CLI_TOOLS:
                findings.append(Finding("cli", name, "inferred", f"import {name}",
                                        tuple(locations[:3])))
            integration = _INTEGRATIONS.get(name)
            if integration:
                findings.append(Finding("integration", integration, "inferred", f"import {name}",
                                        tuple(locations[:3])))


def _add_import(imports: dict[str, list[Evidence]], name: str, evidence: Evidence) -> None:
    top = name.split(".")[0]
    if top:
        imports.setdefault(top, []).append(evidence)


def _resolve_import(node: ast.ImportFrom, relative: str) -> str | None:
    """Resolve an absolute or relative import to a dotted module prefix."""
    if node.level == 0:
        return node.module
    parts = relative.split("/")[:-1]
    keep = len(parts) - node.level + 1
    base = parts[:keep] if keep > 0 else []
    if node.module:
        base.append(node.module)
    return ".".join(base) or None


def _is_main_guard(test: ast.AST) -> bool:
    if not isinstance(test, ast.Compare):
        return False
    return any(isinstance(node, ast.Name) and node.id == "__name__"
               for node in [test.left, *test.comparators])


def _classify(imports: dict[str, list[Evidence]], modules: list[str]) -> list[dict[str, Any]]:
    local = {module.split(".")[0] for module in modules}
    dependencies = []
    for name in sorted(imports):
        if name in sys.stdlib_module_names:
            kind = "stdlib"
        elif name in local:
            kind = "local"
        else:
            kind = "third-party"
        dependencies.append({"name": name, "kind": kind,
                             "evidence": [asdict(evidence) for evidence in imports[name][:3]]})
    return dependencies


def _dedupe(findings: list[Finding]) -> list[Finding]:
    seen: set[tuple[str, str, str, int]] = set()
    unique = []
    for finding in findings:
        key = (finding.kind, finding.name,
               finding.evidence[0].path if finding.evidence else "",
               finding.evidence[0].line if finding.evidence else 0)
        if key not in seen:
            seen.add(key)
            unique.append(finding)
    return unique


def _revision(root: Path) -> tuple[str | None, bool | None]:
    try:
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=False, timeout=10)
        if head.returncode != 0:
            return None, None
        status = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                                capture_output=True, text=True, check=False, timeout=10)
        return head.stdout.strip(), bool(status.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        return None, None
