#!/usr/bin/env python3
"""Sync shared skills into each coding agent's skills directory as references.

The single source of truth is ``<repo>/skills/``. Every agent, however, reads
skills from its own directory, so this script creates one directory link per
skill inside each agent directory, pointing back at the shared skill folder.
Edit a skill once in ``skills/<name>/`` and every agent sees the change.

Targets (override with --agents):

    opencode     .opencode/skills      OpenCode
    antigravity  .agents/skills        Antigravity default, also the open
                                       SKILL.md standard read by Codex, Gemini
                                       CLI and GitHub Copilot
    claude       .claude/skills        Claude Code
    github       .github/skills        GitHub Copilot
    codex        .codex/skills         Codex (legacy path)

Usage::

    python scripts/sync_skills.py            # create/refresh references
    python scripts/sync_skills.py --verify   # check every reference resolves
    python scripts/sync_skills.py --prune    # drop references to deleted skills
    python scripts/sync_skills.py --dry-run  # show what would change
"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SHARED = REPO / "skills"

AGENT_DIRS = {
    "opencode": ".opencode/skills",
    "antigravity": ".agents/skills",
    "claude": ".claude/skills",
    "github": ".github/skills",
    "codex": ".codex/skills",
}


def _is_link(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def _exists(path: Path) -> bool:
    return os.path.lexists(path)


def _remove_link(path: Path) -> None:
    if path.is_symlink():
        path.unlink()
    else:
        os.rmdir(path)  # Windows junction: removes the link, not the target


def _junction(link: Path, target: Path) -> None:
    subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link.absolute()), str(target.absolute())],
        check=True,
        capture_output=True,
        text=True,
    )


def create_link(link: Path, target: Path, mode: str) -> str:
    if mode == "copy":
        shutil.copytree(target, link)
        return "copy"
    if mode == "junction":
        _junction(link, target)
        return "junction"
    rel = os.path.relpath(target, link.parent)
    try:
        os.symlink(rel, link, target_is_directory=True)
        return f"symlink -> {rel}"
    except OSError:
        if mode == "symlink" or os.name != "nt":
            raise
        _junction(link, target)  # symlink privilege unavailable; junction fallback
        return "junction (auto fallback)"


def shared_skills() -> list[Path]:
    if not SHARED.is_dir():
        return []
    return sorted((p for p in SHARED.iterdir() if p.is_dir()), key=lambda p: p.name.lower())


def _skill_ok(skill: Path) -> bool:
    return (skill / "SKILL.md").is_file()


def sync_agent(name: str, rel: str, skills: list[Path], args) -> list[str]:
    agent_dir = REPO / rel
    log: list[str] = []
    if not args.dry_run:
        agent_dir.mkdir(parents=True, exist_ok=True)

    wanted = {s.name for s in skills}
    for skill in skills:
        link = agent_dir / skill.name
        state = "missing" if not _exists(link) else ("link" if _is_link(link) else "dir")
        if state == "link" and os.path.realpath(link) == os.path.realpath(skill):
            log.append(f"  = {name}: {skill.name} (already linked)")
            continue
        if state in ("link", "missing") or (state == "dir" and args.force):
            if _exists(link):
                if args.dry_run:
                    log.append(f"  ~ {name}: would replace {skill.name} ({state})")
                    continue
                _remove_link(link) if state == "link" else shutil.rmtree(link)
            else:
                if args.dry_run:
                    log.append(f"  + {name}: {skill.name}")
                    continue
            if not args.dry_run:
                how = create_link(link, skill, args.mode)
                log.append(f"  + {name}: {skill.name} ({how})")
        else:  # real directory, not forced
            log.append(f"  ! {name}: {skill.name} exists as a real dir - use --force to replace")

    if args.prune:
        for entry in sorted(agent_dir.iterdir()) if agent_dir.is_dir() else []:
            if (entry.name not in wanted and _is_link(entry)
                    and Path(os.path.realpath(entry)).parent == SHARED.resolve()):
                action = "would remove" if args.dry_run else "removed"
                if not args.dry_run:
                    _remove_link(entry)
                log.append(f"  - {name}: {action} stale link {entry.name}")
    return log


def verify(skills: list[Path], agents: list[str], mode: str) -> int:
    failures = 0
    for name in agents:
        rel = AGENT_DIRS[name]
        agent_dir = REPO / rel
        if not agent_dir.is_dir():
            print(f"[FAIL] {name}: {rel} does not exist")
            failures += 1
            continue
        for skill in skills:
            link = agent_dir / skill.name
            valid = _is_link(link) and os.path.realpath(link) == os.path.realpath(skill)
            if mode == "copy" and link.is_dir() and not _is_link(link):
                def same_tree(left: str, right: str) -> bool:
                    comparison = filecmp.dircmp(left, right)
                    _, different, errors = filecmp.cmpfiles(
                        left, right, comparison.common_files, shallow=False
                    )
                    return (not comparison.left_only and not comparison.right_only
                            and not comparison.funny_files
                            and not different and not errors
                            and all(same_tree(os.path.join(left, sub), os.path.join(right, sub))
                                    for sub in comparison.common_dirs))
                valid = same_tree(str(link), str(skill))
            if not valid:
                print(f"[FAIL] {name}: {rel}/{skill.name} is not a valid reference")
                failures += 1
    print(f"verify: {len(skills)} skills x {len(agents)} agents, {failures} failure(s)")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--verify", action="store_true", help="check every reference resolves, then exit")
    parser.add_argument("--dry-run", action="store_true", help="show planned changes without writing")
    parser.add_argument("--prune", action="store_true", help="remove references to skills no longer in skills/")
    parser.add_argument("--force", action="store_true", help="replace a real directory with a reference")
    parser.add_argument("--mode", choices=["auto", "symlink", "junction", "copy"], default="auto",
                        help="link strategy (default: auto - symlink, junction fallback on Windows)")
    parser.add_argument("--agents", nargs="*", choices=list(AGENT_DIRS), default=list(AGENT_DIRS),
                        help="subset of agents to sync (default: all)")
    args = parser.parse_args(argv)

    skills = shared_skills()
    if not skills:
        print(f"no skills found under {SHARED}", file=sys.stderr)
        return 1
    invalid = [skill for skill in skills if not _skill_ok(skill)]
    if invalid:
        for skill in invalid:
            print(f"[error] {skill.name} has no SKILL.md", file=sys.stderr)
        return 1

    if args.verify:
        return verify(skills, args.agents, args.mode)

    print(f"shared skills: {SHARED} ({len(skills)})")
    for name in args.agents:
        for line in sync_agent(name, AGENT_DIRS[name], skills, args):
            print(line)
    if args.dry_run:
        print("(dry run - nothing written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
