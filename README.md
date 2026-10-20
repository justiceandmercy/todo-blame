# todo-blame

Annotate TODO/FIXME/HACK/XXX/NOTE comments in a codebase with their age and author using `git blame`, so stale comments surface first.

## Description

`todo-blame` scans a repository for TODO-style comments and uses `git blame` to determine when each was introduced and by whom. Results are sorted oldest-first, with an optional staleness threshold, making it easy to find comments that have lingered too long and triage them.

## Features

- Scans common source and documentation files by default.
- Supports custom markers (e.g. `BUG`, `REVIEW`) and file extensions.
- Annotates each comment with author, date, age in days, and commit hash.
- Flags comments older than a configurable threshold as `[STALE]`.
- Text and JSON output formats.
- Works outside git repositories (age info simply omitted).

## Install

```bash
git clone https://github.com/example/todo-blame.git
cd todo-blame
chmod +x todo_blame.py
```

No external dependencies; requires Python 3.8+ and (optionally) git.

## Usage

```bash
# Scan current directory
python3 todo_blame.py

# Scan a specific path, show oldest 20
python3 todo_blame.py ./src --top 20

# Custom markers and staleness threshold
python3 todo_blame.py --markers "TODO,FIXME,BUG" --stale-days 30

# JSON output
python3 todo_blame.py --format json > report.json

# Restrict to specific extensions
python3 todo_blame.py --extensions py,js,ts
```

Example output:

```
src/api.py:42  TODO  (312d, alice) [STALE]
    handle retry logic
src/util.js:7  FIXME  (12d, bob)
    off-by-one in parser

Total: 2
```

## License

MIT
