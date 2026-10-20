#!/usr/bin/env python3
"""todo-blame: annotate TODO/FIXME comments with their age via git blame."""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanner import scan, DEFAULT_MARKERS
from gitinfo import blame_line, repo_root_for


def main():
    parser = argparse.ArgumentParser(
        prog="todo-blame",
        description="Scan a repository for TODO/FIXME/HACK/XXX/NOTE comments and annotate each with its age and author via git blame.",
    )
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--markers", default=",".join(DEFAULT_MARKERS),
                        help="Comma-separated list of markers to scan for.")
    parser.add_argument("--stale-days", type=int, default=90,
                        help="Age in days after which a TODO is considered stale.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--top", type=int, default=0, help="Show only the N oldest items.")
    parser.add_argument("--extensions", default="",
                        help="Comma-separated extensions to include (default: common code/docs).")
    args = parser.parse_args()

    root = os.path.realpath(os.path.abspath(args.path))
    markers = [m.strip().upper() for m in args.markers.split(",") if m.strip()]
    exts = None
    if args.extensions:
        exts = set(e.strip() if e.strip().startswith(".") else "." + e.strip()
                   for e in args.extensions.split(",") if e.strip())

    items = scan(root, markers=markers, extensions=exts)
    repo_root = repo_root_for(root)

    enriched = []
    for it in items:
        real_path = os.path.realpath(it.path)
        rel = os.path.relpath(real_path, repo_root) if repo_root else real_path
        blame = blame_line(repo_root, rel, it.line) if repo_root else None
        rec = {
            "path": os.path.relpath(real_path, root),
            "line": it.line,
            "marker": it.marker,
            "text": it.text,
            "author": blame.author if blame else None,
            "date": blame.date if blame else None,
            "age_days": blame.age_days if blame else None,
            "commit": blame.commit if blame else None,
            "stale": bool(blame is not None and blame.age_days >= args.stale_days),
        }
        enriched.append(rec)

    enriched.sort(key=lambda r: (r["age_days"] is None, -(r["age_days"] or 0)))

    if args.top and args.top > 0:
        enriched = enriched[:args.top]

    if args.format == "json":
        print(json.dumps({"root": root, "repo_root": repo_root, "items": enriched}, indent=2))
        return

    if not enriched:
        print("No TODO-style comments found.")
        return
    for r in enriched:
        age = f"{r['age_days']}d" if r["age_days"] is not None else "?"
        stale = " [STALE]" if r["stale"] else ""
        author = r["author"] or "unknown"
        print(f"{r['path']}:{r['line']}  {r['marker']}  ({age}, {author}){stale}")
        if r["text"]:
            print(f"    {r['text']}")
    print(f"\nTotal: {len(enriched)}")


if __name__ == "__main__":
    main()
