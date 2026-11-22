#!/usr/bin/env python3
"""THE one harness.json fixture builder (FEAT-2297 D-06).

Every valid serialized harness.json a test needs comes from here: start from the minimal
version-3 document, merge `overrides` recursively (a list replaces, never extends), then let the
canonical loader apply the schema defaults and validate. There is deliberately no way to build an
unchecked config: a test that needs an invalid one builds a valid result and corrupts it.

    build_config(overrides=None)        -> the validated mapping
    write_config(path, overrides=None)  -> writes it as JSON and returns the mapping
    harness_config_support.py --overrides-json '{"github": {"sync": false}}'   (prints it)

Never copy live project values (commands, github identity, era dates) into a fixture.
"""
import argparse
import copy
import json
import sys
from pathlib import Path

BIN = Path(__file__).resolve().parents[1] / ".claude" / "skills" / "harness" / "bin"
if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))
import artifact_accessors  # noqa: E402

MINIMAL = {"schema_version": 3}


def _merged(base, overrides):
    out = copy.deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merged(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def build_config(overrides=None):
    document = _merged(MINIMAL, overrides or {})
    return artifact_accessors.load_harness_json(
        text=json.dumps(document), context="fixture harness.json")


def write_config(path, overrides=None):
    config = build_config(overrides)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return config


def main(argv=None):
    parser = argparse.ArgumentParser(description="Print a validated harness.json fixture.")
    parser.add_argument("--overrides-json", default="{}",
                        help="a JSON object merged over the minimal version-3 config")
    args = parser.parse_args(argv)
    overrides = artifact_accessors.load_json_mapping(
        text=args.overrides_json, context="--overrides-json")
    print(json.dumps(build_config(overrides), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
