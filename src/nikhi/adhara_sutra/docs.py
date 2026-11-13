"""Validate documentation structure and machine-verifiable references (FR-DOC-007)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)


def validate_documentation(document: str | Path, *,
                           required_sections: Iterable[str] = ()) -> list[str]:
    """Return problems found in one Markdown document.

    Checks that each required section heading is present and that every local
    link target resolves to an existing file or directory.
    """
    path = Path(document)
    text = path.read_text(encoding="utf-8", errors="replace")
    headings = {heading.strip().casefold() for heading in _HEADING.findall(text)}
    problems = [f"missing required section: {section}" for section in required_sections
                if section.strip().casefold() not in headings]
    for target in _LINK.findall(text):
        if "://" in target or target.startswith(("mailto:", "#")):
            continue
        relative = target.split("#", 1)[0]
        if relative and not (path.parent / relative).exists():
            problems.append(f"broken local link: {target}")
    return problems
