"""Static inspection of an existing Python project for architecture reporting."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass, field
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

    source_fingerprint: str | None = None
    configuration_files: dict[str, bytes] = field(default_factory=dict, repr=False)

    def by_kind(self, kind: str) -> list[Finding]:
        return [finding for finding in self.findings if finding.kind == kind]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_fingerprint": self.source_fingerprint,
            "root": self.root,
            "revision": self.revision,
            "dirty": self.dirty,
            "files": self.files,
            "modules": self.modules,
            "dependencies": self.dependencies,
            "findings": [finding.to_dict() for finding in self.findings],
            "errors": [error.to_dict() for error in self.errors],
        }


@dataclass
class AnalysisCache:
    """Per-file inspection results reused while a file's content is unchanged (FR-DISC-011)."""

    files: dict[str, tuple[str, list[Finding], list[Finding],
                          dict[str, list[Evidence]], dict[str, list[Evidence]]]] = field(default_factory=dict)


class ProjectInspector:
    """Discover entry points, framework usage, integrations, and dependencies from source."""

    def __init__(self, root: str | Path, *, exclude: Iterable[str] = (), cache: AnalysisCache | None = None) -> None:
        self.root = Path(root).resolve()
        self.exclude = _EXCLUDED | set(exclude)
        self.cache = cache

    def inspect(self) -> ProjectProfile:
        if not self.root.is_dir():
            raise ValueError(f"Not a directory: {self.root}")
        files = [path for path in sorted(self.root.rglob("*"))
                 if path.is_file() and not self._excluded(path)]
        python_files = [path for path in files if path.suffix == ".py"]
        inputs = [path for path in files if path.suffix == ".py" or path.suffix in _JS_SUFFIXES
                  or self._relative(path) in {"pyproject.toml", "setup.cfg", "package.json", ".adhara-profile.json"}]
        contents = {self._relative(path): path.read_bytes() for path in inputs}
        manifest = [(name, hashlib.sha256(data).hexdigest()) for name, data in sorted(contents.items())]
        fingerprint = hashlib.sha256(json.dumps(manifest, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
        modules = [self._module_name(path) for path in python_files]
        findings: list[Finding] = []
        errors: list[Finding] = []
        imports: dict[str, list[Evidence]] = {}
        module_imports: dict[str, list[Evidence]] = {}
        for path in python_files:
            relative = self._relative(path)
            digest = hashlib.sha256(contents[relative]).hexdigest()
            cached = self.cache.files.get(relative) if self.cache is not None else None
            if cached is not None and cached[0] == digest:
                file_findings, file_errors, file_imports, file_module_imports = cached[1:]
            else:
                file_findings, file_errors = [], []
                file_imports, file_module_imports = {}, {}
                self._inspect_python(path, contents[relative], file_findings, file_errors, file_imports, file_module_imports)
                if self.cache is not None:
                    self.cache.files[relative] = (digest, file_findings, file_errors,
                                                  file_imports, file_module_imports)
            findings.extend(file_findings)
            errors.extend(file_errors)
            _merge_imports(imports, file_imports)
            _merge_imports(module_imports, file_module_imports)
        if self.cache is not None:
            current = {self._relative(path) for path in python_files}
            for stale in set(self.cache.files) - current:
                del self.cache.files[stale]
        for path in files:
            if path.suffix in _JS_SUFFIXES:
                self._inspect_javascript(path, contents[self._relative(path)], findings)
        self._inspect_scripts(findings, contents)
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
            source_fingerprint=fingerprint,
            configuration_files={name: contents[name] for name in ("pyproject.toml", ".adhara-profile.json") if name in contents},
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

    def _inspect_python(self, path: Path, content: bytes, findings: list[Finding], errors: list[Finding],
                        imports: dict[str, list[Evidence]],
                        module_imports: dict[str, list[Evidence]]) -> None:
        relative = self._relative(path)
        source = content.decode("utf-8", errors="replace")
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

        # Recognize only stable, direct module-level imports and instance assignments.
        constructors, namespaces = set(), set()
        for item in tree.body:
            if isinstance(item, ast.ImportFrom) and item.level == 0 and item.module == "nikhi.adhara_sutra":
                constructors.update(alias.asname or alias.name for alias in item.names if alias.name == "Application")
            elif isinstance(item, ast.Import):
                namespaces.update(alias.asname for alias in item.names
                                  if alias.name == "nikhi.adhara_sutra" and alias.asname)
        bound = constructors | namespaces
        had_framework_import = bool(bound)
        shadowed = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
                    and isinstance(node.ctx, (ast.Store, ast.Del)) and node.id in bound}
        shadowed.update(node.name for node in ast.walk(tree)
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name in bound)
        shadowed.update(node.arg for node in ast.walk(tree) if isinstance(node, ast.arg) and node.arg in bound)
        imports_per_name = {name: 0 for name in bound}
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    name = alias.asname or alias.name.split(".")[0]
                    if name in imports_per_name:
                        imports_per_name[name] += 1
        shadowed.update(name for name, count in imports_per_name.items() if count != 1)
        constructors -= shadowed
        namespaces -= shadowed

        def is_constructor(node: ast.AST) -> bool:
            return (isinstance(node, ast.Name) and node.id in constructors) or (
                isinstance(node, ast.Attribute) and node.attr == "Application"
                and isinstance(node.value, ast.Name) and node.value.id in namespaces)

        applications = set()
        for item in tree.body:
            if isinstance(item, (ast.Assign, ast.AnnAssign)) and isinstance(item.value, ast.Call) and is_constructor(item.value.func):
                targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                if len(targets) == 1 and isinstance(targets[0], ast.Name):
                    applications.add(targets[0].id)
        stores = {name: 0 for name in applications}
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in stores and isinstance(node.ctx, (ast.Store, ast.Del)):
                stores[node.id] += 1
            elif isinstance(node, ast.arg) and node.arg in stores:
                stores[node.arg] += 1
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name in stores:
                stores[node.name] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    bound_name = alias.asname or alias.name.split(".")[0]
                    if bound_name in stores:
                        stores[bound_name] += 1
            elif isinstance(node, ast.ExceptHandler) and node.name in stores:
                stores[node.name] += 1
        applications = {name for name in applications if stores[name] == 1}

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
                        owner = decorator.func.value
                        if isinstance(owner, ast.Name) and owner.id in applications:
                            findings.append(Finding(decorator.func.attr, decorator.args[0].value, "observed",
                                                    f"handler {node.name}", (evidence(decorator),)))
                        else:
                            findings.append(Finding("framework_unresolved", "decorator", "inferred",
                                                    "decorator owner is not a supported application binding",
                                                    (evidence(decorator),)))
            elif isinstance(node, ast.Call):
                self._inspect_call(node, evidence, findings, is_constructor, applications, tree)
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

        if had_framework_import and not any(item.kind == "application" for item in findings):
            findings.append(Finding("framework_unresolved", "application binding", "inferred",
                                    "framework import has no supported stable application assignment"))

    def _inspect_call(self, node: ast.Call, evidence: Any, findings: list[Finding],
                      is_constructor: Any, applications: set[str], tree: ast.AST) -> None:
        function = node.func
        if isinstance(function, ast.Name) and function.id == "print":
            findings.append(Finding("protocol_bypass", "print()", "inferred",
                                    "writes directly to stdout", (evidence(node),)))
        elif isinstance(function, ast.Name) and function.id == "open":
            findings.append(Finding("integration", "filesystem", "inferred", "open() call",
                                    (evidence(node),)))
        elif is_constructor(function):
            name = "<unnamed>"
            for keyword in node.keywords:
                if keyword.arg == "name" and isinstance(keyword.value, ast.Constant) \
                        and isinstance(keyword.value.value, str):
                    name = keyword.value.value
            # Only a constructor assigned to a stable module-level name is a supported binding.
            if any(isinstance(item, ast.Assign) and item.value is node and len(item.targets) == 1
                   and isinstance(item.targets[0], ast.Name) and item.targets[0].id in applications
                   for item in tree.body) or any(
                    isinstance(item, ast.AnnAssign) and item.value is node and isinstance(item.target, ast.Name)
                    and item.target.id in applications for item in tree.body):
                findings.append(Finding("application", name, "observed", "", (evidence(node),)))
            else:
                findings.append(Finding("framework_unresolved", "application", "inferred", "unsupported application binding", (evidence(node),)))
        elif isinstance(function, ast.Attribute):
            if function.attr == "service" and node.args and isinstance(node.args[0], ast.Constant) \
                    and isinstance(node.args[0].value, str):
                findings.append(Finding("service", node.args[0].value, "observed", "",
                                        (evidence(node),)))
            elif function.attr in ("run", "serve") and isinstance(function.value, ast.Name) \
                    and function.value.id in applications:
                findings.append(Finding("entry_point", f"{function.value.id}.{function.attr}()", "observed",
                                        "application runtime entry", (evidence(node),)))
            elif isinstance(function.value, ast.Name) \
                    and function.attr in _UNMANAGED.get(function.value.id, ()):
                findings.append(Finding("unmanaged_task", f"{function.value.id}.{function.attr}",
                                        "inferred", "unmanaged background work", (evidence(node),)))

    def _inspect_javascript(self, path: Path, content: bytes, findings: list[Finding]) -> None:
        relative = self._relative(path)
        lines = content.decode("utf-8", errors="replace").splitlines()
        for number, line in enumerate(lines, 1):
            for kind, pattern in _ELECTRON.items():
                if pattern.search(line):
                    findings.append(Finding(kind, relative, "observed", "", (Evidence(relative, number, line.strip()[:200]),)))

    def _inspect_scripts(self, findings: list[Finding], contents: dict[str, bytes]) -> None:
        pyproject = self.root / "pyproject.toml"
        if "pyproject.toml" in contents:
            try:
                data = tomllib.loads(contents["pyproject.toml"].decode("utf-8"))
            except (UnicodeDecodeError, tomllib.TOMLDecodeError):
                data = {}
            scripts = data.get("project", {}).get("scripts", {})
            if isinstance(scripts, dict):
                for name, target in scripts.items():
                    findings.append(Finding("entry_point", str(name), "observed",
                                            f"console script -> {target}",
                                            (Evidence("pyproject.toml", 0, f"[project.scripts] {name}"),)))
        setup_cfg = self.root / "setup.cfg"
        if "setup.cfg" in contents:
            lines = contents["setup.cfg"].decode("utf-8", errors="replace").splitlines()
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
                                        tuple(locations)))
            integration = _INTEGRATIONS.get(name)
            if integration:
                findings.append(Finding("integration", integration, "inferred", f"import {name}",
                                        tuple(locations)))


def _add_import(imports: dict[str, list[Evidence]], name: str, evidence: Evidence) -> None:
    top = name.split(".")[0]
    if top:
        imports.setdefault(top, []).append(evidence)


def _merge_imports(target: dict[str, list[Evidence]], source: dict[str, list[Evidence]]) -> None:
    for name, evidence in source.items():
        target.setdefault(name, []).extend(evidence)


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
                             "evidence": [asdict(evidence) for evidence in imports[name]]})
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
