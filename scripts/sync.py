#!/usr/bin/env python3
"""Copy contract/ into each package directory.

contract/ is the only place anything is edited. Every package ships its own
copy because none of these ecosystems can publish a file that sits outside the
package directory. The copies are generated, never edited, and CI fails if they
have drifted from contract/.

    python scripts/sync.py           # write the copies
    python scripts/sync.py --check   # fail if any copy is stale, change nothing
"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "contract")
PACKAGES = os.path.join(ROOT, "packages")

# Each package gets the whole contract directory at <package>/contract.
TARGETS = ["composer", "npm", "go"]


def walk(base):
    for dirpath, _dirnames, filenames in os.walk(base):
        for filename in filenames:
            full = os.path.join(dirpath, filename)
            yield os.path.relpath(full, base).replace("\\", "/")


def check(target_dir):
    """Return the relative paths that differ between contract/ and a copy."""
    stale = []
    wanted = sorted(walk(SOURCE))
    for rel in wanted:
        dest = os.path.join(target_dir, rel.replace("/", os.sep))
        src = os.path.join(SOURCE, rel.replace("/", os.sep))
        if not os.path.exists(dest):
            stale.append(rel + " (missing)")
        elif not filecmp.cmp(src, dest, shallow=False):
            stale.append(rel + " (differs)")

    if os.path.isdir(target_dir):
        for rel in sorted(walk(target_dir)):
            if rel not in wanted:
                stale.append(rel + " (should not be here)")
    return stale


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report stale copies and exit non-zero instead of writing",
    )
    args = parser.parse_args()

    problems = []
    for name in TARGETS:
        target_dir = os.path.join(PACKAGES, name, "contract")

        if args.check:
            stale = check(target_dir)
            status = "stale" if stale else "current"
            print("packages/%-9s %s" % (name, status))
            for rel in stale:
                problems.append("packages/%s/contract/%s" % (name, rel))
            continue

        if os.path.isdir(target_dir):
            shutil.rmtree(target_dir)
        shutil.copytree(SOURCE, target_dir)
        print("packages/%-9s synced %d files" % (name, len(list(walk(target_dir)))))

    if problems:
        print("")
        print("%d file(s) out of date. Run `python scripts/sync.py` and commit." % len(problems))
        for p in problems:
            print("  " + p)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
