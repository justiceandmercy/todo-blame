"""Git blame integration for todo items."""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class BlameInfo:
    commit: str
    author: str
    author_email: str
    author_time: int
    age_days: int
    date: str


def blame_line(repo_root, rel_path, line):
    try:
        out = subprocess.run(
            ["git", "blame", "-L", f"{line},{line}", "--porcelain", rel_path],
            cwd=repo_root, capture_output=True, text=True, timeout=30,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return None
    if out.returncode != 0:
        return None
    commit = ""
    author = ""
    email = ""
    ts = 0
    for ln in out.stdout.splitlines():
        if ln.startswith("author "):
            author = ln[len("author "):]
        elif ln.startswith("author-mail "):
            email = ln[len("author-mail "):].strip("<>")
        elif ln.startswith("author-time "):
            ts = int(ln[len("author-time "):])
        elif not commit:
            parts = ln.split()
            if parts and len(parts[0]) == 40 and all(c in "0123456789abcdef" for c in parts[0]):
                commit = parts[0]
    if not ts:
        return None
    age = int((time.time() - ts) / 86400)
    dt = datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()
    return BlameInfo(commit=commit, author=author, author_email=email, author_time=ts, age_days=age, date=dt)


def repo_root_for(path):
    cwd = path if os.path.isdir(path) else os.path.dirname(path)
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd, capture_output=True, text=True, timeout=30,
        )
    except Exception:
        return None
    if out.returncode != 0:
        return None
    val = out.stdout.strip() or None
    return os.path.realpath(val) if val else None


def is_git_repo(path):
    return repo_root_for(path) is not None
