#!/usr/bin/env python3
"""Check the contract is well formed before anyone publishes it.

Runs in CI on every push. Exits non-zero on the first category that fails, and
prints every problem in that category rather than stopping at the first one.

Checks:
  1. pages.json matches its schema.
  2. pages and props cover exactly the same set of names.
  3. every prop listed as required also appears in props.
  4. each conformance fixture parses and matches its schema.
  5. fixture ids are unique, and match the path they live at.
  6. every fixture names a source document that exists, when the context repo
     is available locally. Skipped with a note when it is not.

Usage:
    python scripts/validate.py
    python scripts/validate.py --context ../escalated-developer-context
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRACT = os.path.join(ROOT, "contract")
SCHEMA = os.path.join(CONTRACT, "schema")
CONFORMANCE = os.path.join(CONTRACT, "conformance")


def read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def read_yaml(path):
    try:
        import yaml
    except ImportError:
        sys.stderr.write(
            "PyYAML is needed to validate fixtures. pip install pyyaml\n"
        )
        raise SystemExit(2)
    with io.open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def validate_against(schema, doc, label, problems):
    """Validate with jsonschema when it is installed, else check the parts of
    the schema we rely on most. The fallback exists so the repo stays checkable
    on a machine with nothing installed; CI installs jsonschema."""
    try:
        import jsonschema
    except ImportError:
        for key in schema.get("required", []):
            if key not in doc:
                problems.append("%s: missing required key %r" % (label, key))
        return "fallback"
    validator = jsonschema.Draft7Validator(schema)
    for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
        where = "/".join(str(p) for p in err.path) or "(root)"
        problems.append("%s: %s -> %s" % (label, where, err.message))
    return "jsonschema"


def check_pages(problems):
    pages_path = os.path.join(CONTRACT, "pages.json")
    doc = read_json(pages_path)
    schema = read_json(os.path.join(SCHEMA, "pages.schema.json"))
    mode = validate_against(schema, doc, "pages.json", problems)

    names = set(doc.get("pages", []))
    prop_names = set(doc.get("props", {}))

    for missing in sorted(names - prop_names):
        problems.append("pages.json: %s is listed in pages with no props entry" % missing)
    for orphan in sorted(prop_names - names):
        problems.append("pages.json: %s has props but is not in pages" % orphan)

    for name, entry in sorted(doc.get("props", {}).items()):
        declared = set(entry.get("props", []))
        for req in entry.get("required", []):
            if req not in declared:
                problems.append(
                    "pages.json: %s requires %r which is not in its props list" % (name, req)
                )

    return len(names), mode


def check_fixtures(problems, context_dir):
    schema = read_json(os.path.join(SCHEMA, "conformance.schema.json"))
    seen = {}
    count = 0

    for dirpath, _dirnames, filenames in os.walk(CONFORMANCE):
        for filename in sorted(filenames):
            if not filename.endswith((".yaml", ".yml")):
                continue
            path = os.path.join(dirpath, filename)
            rel = os.path.relpath(path, CONFORMANCE).replace("\\", "/")
            count += 1

            try:
                doc = read_yaml(path)
            except Exception as exc:  # noqa: BLE001 - report and continue
                problems.append("%s: will not parse: %s" % (rel, exc))
                continue

            if not isinstance(doc, dict):
                problems.append("%s: expected a mapping at the top level" % rel)
                continue

            validate_against(schema, doc, rel, problems)

            fixture_id = doc.get("id")
            if fixture_id:
                if fixture_id in seen:
                    problems.append(
                        "%s: id %r is already used by %s" % (rel, fixture_id, seen[fixture_id])
                    )
                seen[fixture_id] = rel

                area = rel.split("/")[0]
                if not fixture_id.startswith(area + "/"):
                    problems.append(
                        "%s: id %r does not start with its directory %r"
                        % (rel, fixture_id, area)
                    )

            source = doc.get("source")
            if source and context_dir:
                if not os.path.exists(os.path.join(context_dir, source)):
                    problems.append(
                        "%s: source %s not found in %s" % (rel, source, context_dir)
                    )

    return count, len(seen)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--context",
        default=os.environ.get("ESCALATED_CONTEXT_DIR", ""),
        help="path to a checkout of escalated-developer-context, so `source:` can be checked",
    )
    args = parser.parse_args()

    context_dir = args.context or ""
    if context_dir and not os.path.isdir(context_dir):
        print("note: --context %s is not a directory, skipping source checks" % context_dir)
        context_dir = ""

    problems = []
    page_count, mode = check_pages(problems)
    fixture_count, id_count = check_fixtures(problems, context_dir)

    print("pages.json      %d pages, props for all of them" % page_count)
    print("conformance     %d fixtures, %d distinct ids" % (fixture_count, id_count))
    print("schema check    %s" % ("jsonschema" if mode == "jsonschema" else "fallback (jsonschema not installed)"))
    if not context_dir:
        print("source check    skipped (pass --context to enable)")
    print("")

    if problems:
        print("%d problem(s):" % len(problems))
        for p in problems:
            print("  " + p)
        return 1

    print("contract is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
