"""The ``adhara`` developer command."""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Sequence

from ._version import __version__
from .application import Application
from .discovery import ProjectInspector
from .doctor import application_report, environment_report, render_text
from .migration import STRATEGIES, analyze_migration, load_statuses, load_test_evidence
from .report import (implementation_report, load_report, migration_report, render_json, render_markdown, verification_report)
from .profiles import resolve_profile
from .scaffolding import PROFILES, generate
from .verification import Baseline, apply_baseline, verify


def _load(target: str) -> Application:
    """Load an Application from a module name or a Python file defining app/application/create_app."""
    path = Path(target)
    if path.is_file():
        spec = importlib.util.spec_from_file_location(f"_adhara_app_{path.stem}", path)
        if spec is None or spec.loader is None:
            raise ValueError("the file cannot be loaded as a Python module")
        module = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(path.resolve().parent))
        try:
            try:
                spec.loader.exec_module(module)
            except ImportError as exc:
                if "attempted relative import with no known parent package" in str(exc):
                    raise ValueError(
                        "This file uses package-relative imports; install the project and use "
                        "its dotted module target, for example: adhara run package.app") from exc
                raise
        finally:
            sys.path.pop(0)
    else:
        module = importlib.import_module(target)
    app = getattr(module, "app", None) or getattr(module, "application", None)
    if app is None and callable(getattr(module, "create_app", None)):
        app = module.create_app()
    if not isinstance(app, Application):
        raise ValueError("define an Application as 'app', 'application', or create_app()")
    return app


def _write(text: str, output: str | None) -> None:
    if output:
        Path(output).write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
        print(f"wrote {output}")
    else:
        print(text)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="adhara", description="AdharaSutra developer command")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command")
    run = commands.add_parser("run", help="run an application")
    run.add_argument("target", help="module name or path to a Python file defining 'app'")
    run.add_argument("--persistent", action="store_true",
                     help="serve sequential JSON-line requests until EOF")
    commands.add_parser("version", help="print the framework version")
    new = commands.add_parser("new", help="generate a new application project")
    new.add_argument("path", help="directory to create the project in")
    new.add_argument("--name", help="application name (default: directory name)")
    new.add_argument("--package", help="Python package name (default: derived from the name)")
    new.add_argument("--profile", choices=PROFILES, default="minimal", help="architecture profile (default: minimal)")
    new.add_argument("--connectors", default="",
                     help="comma-separated connectors: http, sqlite, external")
    new.add_argument("--force", action="store_true", help="overwrite existing files")
    doctor = commands.add_parser("doctor", help="diagnose the environment and an optional application")
    doctor.add_argument("target", nargs="?", help="optional module name or path to a Python file defining 'app'")
    doctor.add_argument("--json", action="store_true", help="emit JSON instead of text")
    doctor.add_argument("--output", help="write the report to a file instead of stdout")
    inspect = commands.add_parser("inspect", help="inspect a project and report its implementation")
    inspect.add_argument("target", nargs="?", default=".", help="project root (default: current directory)")
    inspect.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    inspect.add_argument("--output", help="write the report to a file instead of stdout")
    verify_command = commands.add_parser("verify", help="verify a project against the architecture profile")
    verify_command.add_argument("target", nargs="?", default=".", help="project root (default: current directory)")
    verify_command.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    verify_command.add_argument("--output", help="write the report to a file instead of stdout")
    verify_command.add_argument("--profile", help="override selected architecture profile")
    verify_command.add_argument("--profile-version", help="override selected architecture profile version")
    verify_command.add_argument("--strict", action="store_true",
                                help="treat checks needing review as failures")
    verify_command.add_argument("--baseline",
                                help="JSON file of acknowledged violations that do not block verification")
    verify_command.add_argument("--write-baseline",
                                help="write the current violations to this baseline file and exit")
    migrate = commands.add_parser("migrate", help="analyze a project and produce a migration plan")
    migrate.add_argument("target", nargs="?", default=".", help="project root (default: current directory)")
    migrate.add_argument("--profile", help="override selected architecture profile")
    migrate.add_argument("--profile-version", help="override selected architecture profile version")
    migrate.add_argument("--strategy", choices=STRATEGIES, default="incremental",
                         help="migration strategy (default: incremental)")
    migrate.add_argument("--status", help="JSON file mapping task/finding ids to recorded statuses")
    migrate.add_argument("--evidence", help="JSON file with behavioral/regression test evidence for completion")
    migrate.add_argument("--plan", help="saved migration report to compare")
    migrate.add_argument("--check-source", action="store_true",
                         help="fail if the analyzed source does not match the current working tree")
    migrate.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    migrate.add_argument("--output", help="write the report to a file instead of stdout")
    args = parser.parse_args(argv)
    if args.command == "version":
        print(__version__)
        return 0
    if args.command == "new":
        connectors = [item.strip() for item in args.connectors.split(",") if item.strip()]
        try:
            written = generate(args.path, name=args.name, package=args.package,
                               profile=args.profile, connectors=connectors, force=args.force)
        except ValueError as exc:
            print(f"adhara: {exc}", file=sys.stderr)
            return 2
        for path in written:
            print(f"created {path}")
        return 0
    if args.command == "doctor":
        report = environment_report()
        if args.target:
            try:
                report = application_report(report, _load(args.target))
            except Exception as exc:
                print(f"adhara: cannot load {args.target}: {exc}", file=sys.stderr)
                return 2
        _write(render_json(report) if args.json else render_text(report), args.output)
        return 1 if report["status"] == "fail" else 0
    if args.command == "inspect":
        if not Path(args.target).is_dir():
            print(f"adhara: not a directory: {args.target}", file=sys.stderr)
            return 2
        try:
            report = implementation_report(ProjectInspector(args.target).inspect())
        except Exception as exc:
            print(f"adhara: cannot inspect {args.target}: {exc}", file=sys.stderr)
            return 2
        text = render_json(report) if args.json else render_markdown(report)
        _write(text, args.output)
        return 0
    if args.command == "verify":
        if not Path(args.target).is_dir():
            print(f"adhara: not a directory: {args.target}", file=sys.stderr)
            return 2
        try:
            project = ProjectInspector(args.target).inspect()
            profile = resolve_profile(args.target, name=args.profile, version=args.profile_version,
                                      captured_files=project.configuration_files)
            result = verify(project, profile)
            if args.write_baseline:
                baseline = Baseline.capture(result)
                baseline.save(args.write_baseline)
                print(f"wrote {len(baseline.entries)} acknowledged violation(s) to {args.write_baseline}")
                return 0
            if args.baseline:
                result = apply_baseline(result, Baseline.load(args.baseline))
        except Exception as exc:
            print(f"adhara: cannot verify {args.target}: {exc}", file=sys.stderr)
            return 2
        report = verification_report(result, source={"root": project.root, "revision": project.revision,
                                                     "dirty": project.dirty})
        text = render_json(report) if args.json else render_markdown(report)
        _write(text, args.output)
        failed = result.status == "fail" or (args.strict and result.status == "needs_review")
        return 1 if failed else 0
    if args.command == "migrate":
        if not Path(args.target).is_dir():
            print(f"adhara: not a directory: {args.target}", file=sys.stderr)
            return 2
        if args.check_source and not args.plan:
            print("adhara: --check-source requires --plan", file=sys.stderr)
            return 2
        try:
            saved = load_report(args.plan) if args.check_source else None
            if saved is not None:
                source = saved.get("source")
                if saved.get("kind") != "migration" or not isinstance(source, dict) or any(
                        not isinstance(value, str) or not value.strip() for value in
                        (source.get("source_fingerprint"), saved.get("analyzer_version"), saved.get("profile_digest"))):
                    raise ValueError("saved migration report is missing required identity fields")
            project = ProjectInspector(args.target).inspect()
            profile = resolve_profile(args.target, name=args.profile, version=args.profile_version,
                                      captured_files=project.configuration_files)
            result = verify(project, profile)
            plan = analyze_migration(project, result, strategy=args.strategy)
            if saved is not None and (saved["source"]["source_fingerprint"] != project.source_fingerprint
                    or saved["analyzer_version"] != result.analyzer_version
                    or saved["profile_digest"] != result.profile_digest):
                print("adhara: saved migration identity does not match current analysis", file=sys.stderr)
                return 1
            statuses = load_statuses(args.status) if args.status else None
            evidence = load_test_evidence(args.evidence) if args.evidence else None
            report = migration_report(plan, statuses=statuses, verification=result if evidence is not None else None,
                                      test_evidence=evidence)
        except Exception as exc:
            print(f"adhara: cannot plan migration for {args.target}: {exc}", file=sys.stderr)
            return 2
        _write(render_json(report) if args.json else render_markdown(report), args.output)
        if report.get("completion_evaluation", {}).get("complete"):
            return 0
        return 0 if evidence is None else 1
    if args.command != "run":
        parser.print_help()
        return 0
    try:
        app = _load(args.target)
    except Exception as exc:
        print(f"adhara: cannot load {args.target}: {exc}", file=sys.stderr)
        return 2
    return app.run(persistent=args.persistent)


if __name__ == "__main__":
    raise SystemExit(main())
