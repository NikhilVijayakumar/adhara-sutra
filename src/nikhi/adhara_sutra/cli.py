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
from .migration import STRATEGIES, analyze_migration, load_statuses
from .report import (implementation_report, migration_report, render_json, render_markdown, verification_report)
from .verification import default_profile, verify


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
            spec.loader.exec_module(module)
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
    verify_command.add_argument("--strict", action="store_true",
                                help="treat checks needing review as failures")
    migrate = commands.add_parser("migrate", help="analyze a project and produce a migration plan")
    migrate.add_argument("target", nargs="?", default=".", help="project root (default: current directory)")
    migrate.add_argument("--strategy", choices=STRATEGIES, default="incremental",
                         help="migration strategy (default: incremental)")
    migrate.add_argument("--status", help="JSON file mapping task ids to recorded statuses")
    migrate.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    migrate.add_argument("--output", help="write the report to a file instead of stdout")
    args = parser.parse_args(argv)
    if args.command == "version":
        print(__version__)
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
            result = verify(ProjectInspector(args.target).inspect(), default_profile())
        except Exception as exc:
            print(f"adhara: cannot verify {args.target}: {exc}", file=sys.stderr)
            return 2
        report = verification_report(result)
        text = render_json(report) if args.json else render_markdown(report)
        _write(text, args.output)
        failed = result.status == "fail" or (args.strict and result.status == "needs_review")
        return 1 if failed else 0
    if args.command == "migrate":
        if not Path(args.target).is_dir():
            print(f"adhara: not a directory: {args.target}", file=sys.stderr)
            return 2
        try:
            project = ProjectInspector(args.target).inspect()
            plan = analyze_migration(project, verify(project), strategy=args.strategy)
            report = migration_report(plan, statuses=load_statuses(args.status) if args.status else None)
        except Exception as exc:
            print(f"adhara: cannot plan migration for {args.target}: {exc}", file=sys.stderr)
            return 2
        _write(render_json(report) if args.json else render_markdown(report), args.output)
        return 0
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
