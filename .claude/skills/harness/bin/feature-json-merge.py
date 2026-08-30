#!/usr/bin/env python3
"""feature-json-merge.py — the thin CLI over feature_json_write.py (mirrors plan-merge.py's
and observations-merge.py's own split): every caller performs one of a small set of
STRUCTURED ops against feature.json, so no caller ever hand-edits the document as raw text.

Each subcommand loads the current document, applies exactly its one op, and hands the result
to feature_json_write.write_feature_json -- which locks, schema-validates the candidate text,
and atomically replaces the file, or refuses (leaving it byte-for-byte unchanged) and this CLI
prints the refusal lines and exits its code, per plan-merge.py's/observations-merge.py's own
pattern.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feature_json_write  # noqa: E402  (local import, after sys.path fix-up)
import harness_merge  # noqa: E402  (local import, after sys.path fix-up)


def _apply(path, mutate):
    """Load `path`'s document, apply `mutate(doc) -> doc`, and write the result under the
    lock. A `path` whose document does not exist is refused: this CLI modifies an existing
    feature.json only -- it is never the tool that instantiates one."""

    def transform(base):
        doc = feature_json_write.parse_doc(base, path)
        if doc is None:
            raise harness_merge.MergeRefusal(
                feature_json_write.SCHEMA_REFUSAL_CODE,
                [f"REFUSED: {path} does not exist.",
                 "  this tool modifies an existing feature.json only."],
            )
        new_doc = mutate(doc)
        return json.dumps(new_doc, indent=2) + "\n"

    try:
        feature_json_write.write_feature_json(path, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)


def _parse_json_arg(name, raw):
    try:
        return json.loads(raw)
    except ValueError as e:
        print(f"feature-json-merge: {name} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(2)


def cmd_set_key(args):
    value = _parse_json_arg("value", args.value)

    def mutate(doc):
        doc[args.key] = value
        return doc

    _apply(args.file, mutate)
    print(f"SET {args.key} = {json.dumps(value)}")
    print(f"APPLIED {args.file}")
    sys.exit(0)


def cmd_append_run(args):
    entry = _parse_json_arg("entry", args.entry)
    if not isinstance(entry, dict):
        print(f"feature-json-merge: entry must be a JSON object, got {type(entry).__name__}",
              file=sys.stderr)
        sys.exit(2)

    def mutate(doc):
        runs = doc.get("runs")
        runs = list(runs) if isinstance(runs, list) else []
        runs.append(entry)
        doc["runs"] = runs
        return doc

    _apply(args.file, mutate)
    print(f"APPENDED run {entry.get('id', '?')!r}")
    print(f"APPLIED {args.file}")
    sys.exit(0)


def cmd_set_github(args):
    value = _parse_json_arg("value", args.value)
    if not isinstance(value, dict):
        print(f"feature-json-merge: value must be a JSON object, got {type(value).__name__}",
              file=sys.stderr)
        sys.exit(2)

    def mutate(doc):
        doc["github"] = value
        return doc

    _apply(args.file, mutate)
    print(f"SET github = {json.dumps(value)}")
    print(f"APPLIED {args.file}")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(prog="feature-json-merge.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_set_key = sub.add_parser("set-key", help="set a top-level key to a JSON scalar value")
    p_set_key.add_argument("file", help="path to feature.json")
    p_set_key.add_argument("key", help="the top-level key to set")
    p_set_key.add_argument("value", help="the new value, as JSON (e.g. '\"Done\"', '3', 'null')")
    p_set_key.set_defaults(func=cmd_set_key)

    p_append_run = sub.add_parser("append-run", help="append one entry to the runs array")
    p_append_run.add_argument("file", help="path to feature.json")
    p_append_run.add_argument("entry", help="the run entry, as a JSON object")
    p_append_run.set_defaults(func=cmd_append_run)

    p_set_github = sub.add_parser("set-github", help="set the whole github block")
    p_set_github.add_argument("file", help="path to feature.json")
    p_set_github.add_argument("value", help="the new github block, as a JSON object")
    p_set_github.set_defaults(func=cmd_set_github)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
