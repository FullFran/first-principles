"""Refuse a run that would silently test the wrong module.

Entries here are standalone: each one puts its own directory on `sys.path` so
that `import solve` works after you copy the folder out. That is rule 6 --
this repo is read, not installed -- and it has a consequence at the root.

Two entries both define `solve`. In a single process only one of them can be
`sys.modules["solve"]`, so the other entry's tests import a stranger. pytest
notices the duplicate test *filenames* and stops with `import file mismatch`,
which reads like a caching problem and is not one. Force past it with
`--import-mode=importlib` and collection succeeds, 184 tests fail, and the
reason is nowhere in the output.

So the root run stops here instead, and says why. No import mode fixes this:
the collision is on `sys.path`, not in collection.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).parent


def _entries():
    """An entry is a directory that makes itself importable on its own."""
    return sorted(p.name for p in ROOT.iterdir()
                  if p.is_dir() and (p / "conftest.py").exists())


def _selected(args, entries):
    """Which entries would this invocation collect from?"""
    if not args:
        return set(entries)
    hit = set()
    for arg in args:
        path = Path(str(arg).split("::")[0])
        path = path if path.is_absolute() else ROOT / path
        try:
            relative = path.resolve().relative_to(ROOT.resolve())
        except ValueError:
            continue
        if relative == Path("."):
            hit |= set(entries)
        elif relative.parts and relative.parts[0] in entries:
            hit.add(relative.parts[0])
    return hit


def pytest_configure(config):
    entries = _entries()
    selected = sorted(_selected(config.args, entries))
    if len(selected) < 2:
        return
    listed = "\n".join(f"    uv run pytest {name}" for name in selected)
    raise pytest.UsageError(
        f"\n\nThese entries cannot share one pytest process: {', '.join(selected)}.\n\n"
        "Each is standalone and puts its own directory on sys.path, so they define\n"
        "the same module names. In one process `import solve` resolves once and the\n"
        "other entry tests a stranger. This is the cost of rule 6, not a defect, and\n"
        "no --import-mode setting changes it.\n\n"
        f"Run them one at a time:\n\n{listed}\n\n"
        "Or all of them, each in its own process:\n\n    ./run-tests\n"
    )
