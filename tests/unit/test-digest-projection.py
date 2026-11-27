#!/usr/bin/env python3
"""digest_projection.py and gen-agent-output.py (BUG-2565 D-01, SC-07).

The provider projection of every persona digest schema, its refusals (each naming file and
JSON pointer), its freshness across calls, and the generator that writes the projection into
each harness agent's frontmatter as `structured: true` plus `output:`.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude/skills/harness/bin"
SCHEMAS = ROOT / ".claude/skills/harness/schemas/digest"
GENERATOR = BIN / "gen-agent-output.py"
sys.path.insert(0, str(BIN))
import digest_schema  # noqa: E402

STRUCTURAL = {"type", "properties", "required", "additionalProperties", "items", "enum", "anyOf"}
FAILURES = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f" — {detail}"))
    if not ok:
        FAILURES.append(name)


def projection():
    import digest_projection
    return digest_projection


def walk(node, path="#"):
    """Every (path, key) in a projected node that is a $ref or off the structural whitelist."""
    bad = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key not in STRUCTURAL:
                bad.append(f"{path}/{key}")
            if key == "properties":
                for name, child in value.items():
                    bad += walk(child, f"{path}/properties/{name}")
            elif key == "items":
                bad += walk(value, f"{path}/items")
            elif key == "anyOf":
                for index, branch in enumerate(value):
                    bad += walk(branch, f"{path}/anyOf/{index}")
    return bad


def schema_copy():
    scratch = Path(tempfile.mkdtemp(prefix="bug2565-projection-"))
    target = scratch / "digest"
    shutil.copytree(SCHEMAS, target)
    return scratch, target


def refusal(name, mutate, file, pointer):
    scratch, target = schema_copy()
    try:
        mutate(target)
        try:
            projection().provider_bundle("harness-qa", target)
        except projection().ProjectionError as error:
            text = str(error)
            check(name, text.startswith(f"digest schema {file}#{pointer}"), text)
            return
        check(name, False, "no ProjectionError")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def put(target, name, schema):
    (target / name).write_text(json.dumps(schema), encoding="utf-8")


def qa_with_property(target, child):
    put(target, "harness-qa.json", {"type": "object", "properties": {"x": child}})


def case_projection():
    bundles = {}
    for persona in digest_schema.PERSONAS:
        try:
            bundles[persona] = projection().provider_bundle(persona)
        except Exception as error:  # noqa: BLE001 — every persona must project; report which failed
            check(f"{persona} projects", False, repr(error))
    check("all 16 personas project", len(bundles) == 16, sorted(set(digest_schema.PERSONAS) - set(bundles)))
    for alias, persona in digest_schema.ALIASES.items():
        check(f"alias {alias} equals {persona}",
              alias in digest_schema.ALIASES and persona in bundles
              and projection().provider_bundle(alias) == bundles[persona])
    bad = {persona: walk(bundle) for persona, bundle in bundles.items() if walk(bundle)}
    check("no projected node carries $ref or a non-structural key", not bad, bad)


def case_refusals():
    refusal("malformed JSON names the file",
            lambda t: (t / "harness-qa.json").write_text("{not json", encoding="utf-8"), "harness-qa.json", ": malformed JSON")
    refusal("an unresolved reference names file and pointer",
            lambda t: qa_with_property(t, {"$ref": "common.json#/$defs/missing"}),
            "harness-qa.json", "/properties/x: unresolved reference")
    refusal("a reference cycle names file and pointer",
            lambda t: (put(t, "common.json", {"$defs": {"a": {"$ref": "#/$defs/b"}, "b": {"$ref": "#/$defs/a"}}}),
                       qa_with_property(t, {"$ref": "common.json#/$defs/a"})),
            "common.json", "/$defs/b: reference cycle")
    refusal("a reference escaping the directory names file and pointer",
            lambda t: ((t.parent / "outside.json").write_text(json.dumps({"$defs": {"a": {"type": "string"}}})),
                       qa_with_property(t, {"$ref": "../outside.json#/$defs/a"})),
            "harness-qa.json", "/properties/x: reference escapes the schema directory")
    refusal("an unsupported keyword names file and pointer",
            lambda t: qa_with_property(t, {"type": "string", "oneOf": [{"type": "string"}]}),
            "harness-qa.json", "/properties/x/oneOf: unsupported keyword")
    refusal("a property with no type, enum or anyOf names file and pointer",
            lambda t: qa_with_property(t, {"pattern": "\\S"}),
            "harness-qa.json", "/properties/x: a property admits any value")
    refusal("an array without items names file and pointer",
            lambda t: qa_with_property(t, {"type": "array"}),
            "harness-qa.json", "/properties/x: array schema without items")
    refusal("array items holding no type, enum or anyOf names the items pointer",
            lambda t: qa_with_property(t, {"type": "array", "items": {"description": "x"}}),
            "harness-qa.json", "/properties/x/items: array items admits any value")
    refusal("an anyOf at the schema root names file and pointer",
            lambda t: put(t, "harness-qa.json", {"anyOf": [{"type": "object"}, {"type": "null"}]}),
            "harness-qa.json", "/anyOf: anyOf at the schema root is unsupported")


def case_fresh_read():
    scratch = Path(tempfile.mkdtemp(prefix="bug2565-fresh-"))
    try:
        entry = lambda required: {"type": "object", "additionalProperties": False, "required": required,  # noqa: E731
                                  "properties": {name: {"type": "string"} for name in required}}
        put(scratch, "harness-qa.json", {"type": "object", "properties": {"x": {"$ref": "common.json#/$defs/e"}}})
        put(scratch, "common.json", {"$defs": {"e": entry(["op"])}})
        first = projection().provider_bundle("harness-qa", scratch)
        put(scratch, "common.json", {"$defs": {"e": entry(["op", "persona"])}})
        second = projection().provider_bundle("harness-qa", scratch)
        check("a schema file changed on disk changes the next result",
              first["properties"]["x"]["required"] == ["op"]
              and second["properties"]["x"]["required"] == ["op", "persona"], (first, second))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def generator_root():
    scratch = Path(tempfile.mkdtemp(prefix="bug2565-generator-"))
    shutil.copytree(ROOT / ".omp/agents", scratch / ".omp/agents")
    shutil.copytree(SCHEMAS, scratch / ".claude/skills/harness/schemas/digest")
    return scratch


def generate(root, *flags):
    return subprocess.run([sys.executable, str(GENERATOR), *flags, str(root)], capture_output=True, text=True)


def split(text):
    """(frontmatter lines, body) of an agent file."""
    lines = text.split("\n")
    close = lines.index("---", 1)
    return lines[1:close], "\n".join(lines[close + 1:])


def kept_lines(frontmatter):
    """Frontmatter lines outside the generated structured/output keys."""
    kept, skipping = [], False
    for line in frontmatter:
        if line.startswith("structured:"):
            skipping = False
            continue
        if line.startswith("output:"):
            skipping = True
            continue
        if skipping and line.startswith(" "):
            continue
        skipping = False
        kept.append(line)
    return kept


def case_generator():
    root = generator_root()
    agents = root / ".omp/agents"
    try:
        before = {path.name: path.read_text(encoding="utf-8") for path in agents.glob("harness-*.md")}
        first = generate(root)
        once = {path.name: path.read_bytes() for path in agents.glob("harness-*.md")}
        second = generate(root)
        twice = {path.name: path.read_bytes() for path in agents.glob("harness-*.md")}
        check("the generator runs", first.returncode == 0 and second.returncode == 0, first.stderr + second.stderr)
        check("a second run leaves identical bytes", once == twice)
        check("--check exits 0 after generation", generate(root, "--check").returncode == 0)
        for name, text in before.items():
            after = (agents / name).read_text(encoding="utf-8")
            old_front, old_body = split(text)
            new_front, new_body = split(after)
            check(f"{name}: body byte-identical", old_body == new_body)
            check(f"{name}: other frontmatter lines byte-identical", kept_lines(old_front) == kept_lines(new_front))
            check(f"{name}: exactly one structured and one output key",
                  sum(line.startswith("structured:") for line in new_front) == 1
                  and sum(line.startswith("output:") for line in new_front) == 1)
        pm = agents / "harness-pm.md"
        pm.write_text(pm.read_text(encoding="utf-8").replace("additionalProperties: false", "additionalProperties: true", 1),
                      encoding="utf-8")
        drift = generate(root, "--check")
        check("a hand-edited output makes --check exit 1 naming the agent",
              drift.returncode == 1 and "DRIFT .omp/agents/harness-pm.md" in drift.stdout, drift.stdout + drift.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    for case in (case_projection, case_refusals, case_fresh_read, case_generator):
        try:
            case()
        except Exception as error:  # noqa: BLE001 — a crashing case is a failing case, reported by name
            check(case.__name__, False, repr(error))
    print(f"{'FAIL' if FAILURES else 'PASS'} test-digest-projection.py ({len(FAILURES)})")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
