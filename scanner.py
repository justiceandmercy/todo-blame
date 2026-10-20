"""Scan source files for TODO-style comments."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import List, Optional, Set

DEFAULT_MARKERS = ["TODO", "FIXME", "HACK", "XXX", "NOTE"]

DEFAULT_IGNORE_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build", "__pycache__",
    ".venv", "venv", "target", ".tox", ".mypy_cache", ".pytest_cache",
}

DEFAULT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".c",
    ".cpp", ".h", ".hpp", ".cs", ".rb", ".php", ".sh", ".bash", ".yaml",
    ".yml", ".toml", ".md", ".html", ".css", ".scss", ".vue", ".svelte",
}

COMMENT_DELIMITERS = ("#", "//", "/*", "*", "<!--", "--", ";")


def _is_comment_context(stripped_before):
    if not stripped_before:
        return True
    return stripped_before.endswith(COMMENT_DELIMITERS)


@dataclass
class TodoItem:
    path: str
    line: int
    marker: str
    text: str
    raw: str


def _marker_pattern(markers):
    alt = "|".join(re.escape(m) for m in markers)
    return re.compile(r"\b(" + alt + r")\b[:\s]*(.*)")


def scan_file(path, markers, pattern=None):
    items = []
    if pattern is None:
        pattern = _marker_pattern(markers)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, 1):
                m = pattern.search(line)
                if m:
                    before = line[:m.start()]
                    if before.strip() and not _is_comment_context(before.strip()):
                        continue
                    marker = m.group(1).upper()
                    text = m.group(2).strip().rstrip(" */").strip()
                    items.append(TodoItem(path=path, line=i, marker=marker, text=text, raw=line.rstrip("\n")))
    except (OSError, UnicodeError):
        pass
    return items


def iter_files(root, extensions=None, ignore_dirs=None):
    if extensions is None:
        extensions = DEFAULT_EXTENSIONS
    if ignore_dirs is None:
        ignore_dirs = DEFAULT_IGNORE_DIRS
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs and not d.startswith(".")]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if extensions and ext not in extensions:
                continue
            yield os.path.join(dirpath, fn)


def scan(root, markers=None, extensions=None, ignore_dirs=None):
    markers = markers or DEFAULT_MARKERS
    pattern = _marker_pattern(markers)
    results = []
    for path in iter_files(root, extensions, ignore_dirs):
        results.extend(scan_file(path, markers, pattern))
    return results
