#!/usr/bin/env python3
"""digest_projection.py and gen-agent-output.py (BUG-2565 D-01, SC-07).

The provider projection of every persona digest schema, its refusals (each naming file and
JSON pointer), its freshness across calls, and the generator that writes the projection into
each harness agent's frontmatter as `structured: true` plus `output:`.
"""
from unit_support import ROOT, BIN

from contextlib import contextmanager
from pathlib import Path
import json
import re
import shutil
import subprocess
import sys
import tempfile

from check_support import Checks
import digest_schema

SCHEMAS = ROOT / ".claude/skills/harness/schemas/digest"
GENERATOR = BIN / "gen-agent-output.py"
STRUCTURAL = {"type", "properties", "required", "additionalProperties", "items", "enum", "anyOf"}
C = Checks()
check = C.check


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


def refusal(name, mutate, file, pointer):
    with tempfile.TemporaryDirectory(prefix="bug2565-projection-") as scratch:
        target = Path(scratch) / "digest"
        shutil.copytree(SCHEMAS, target)
        mutate(target)
        try:
            projection().provider_bundle("harness-qa", target)
        except projection().ProjectionError as error:
            check(name, str(error).startswith(f"digest schema {file}#{pointer}"), str(error))
        else:
            check(name, False, "no ProjectionError")


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
              persona in bundles and projection().provider_bundle(alias) == bundles[persona])
    bad = {persona: found for persona, bundle in bundles.items() if (found := walk(bundle))}
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
    refusal("an anyOf at the schema root reached through $ref names the referenced pointer",
            lambda t: (put(t, "common.json", {"$defs": {"r": {"anyOf": [{"type": "object"}, {"type": "null"}]}}}),
                       put(t, "harness-qa.json", {"$ref": "common.json#/$defs/r"})),
            "common.json", "/$defs/r/anyOf: anyOf at the schema root is unsupported")


def case_fresh_read():
    def entry(required):
        return {"type": "object", "additionalProperties": False, "required": required,
                "properties": {name: {"type": "string"} for name in required}}

    with tempfile.TemporaryDirectory(prefix="bug2565-fresh-") as name:
        scratch = Path(name)
        put(scratch, "harness-qa.json", {"type": "object", "properties": {"x": {"$ref": "common.json#/$defs/e"}}})
        put(scratch, "common.json", {"$defs": {"e": entry(["op"])}})
        first = projection().provider_bundle("harness-qa", scratch)
        put(scratch, "common.json", {"$defs": {"e": entry(["op", "persona"])}})
        second = projection().provider_bundle("harness-qa", scratch)
        check("a schema file changed on disk changes the next result",
              first["properties"]["x"]["required"] == ["op"]
              and second["properties"]["x"]["required"] == ["op", "persona"], (first, second))


@contextmanager
def generator_root():
    """A scratch root holding a copy of the agents and digest schemas; removed on exit."""
    with tempfile.TemporaryDirectory(prefix="bug2565-generator-") as name:
        scratch = Path(name)
        shutil.copytree(ROOT / ".omp/agents", scratch / ".omp/agents")
        shutil.copytree(SCHEMAS, scratch / ".claude/skills/harness/schemas/digest")
        yield scratch


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
    with generator_root() as root:
        agents = root / ".omp/agents"
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


@contextmanager
def rewritten_qa(rewrite):
    """Yield (root, qa path, rewritten text, generator run) after `rewrite(text)` of harness-qa.md."""
    with generator_root() as root:
        qa = root / ".omp/agents/harness-qa.md"
        before = rewrite(qa.read_bytes().decode("utf-8"))
        qa.write_bytes(before.encode("utf-8"))
        yield root, qa, before, generate(root)


def edge(name, rewrite, accept):
    """Regenerate one agent after `rewrite(text)`; `accept(before, after)` judges the bytes."""
    with rewritten_qa(rewrite) as (root, qa, before, run):
        after = qa.read_bytes().decode("utf-8")
        stable = generate(root, "--check").returncode == 0
        check(name, run.returncode == 0 and stable and accept(before, after), run.stderr or after[:400])


FRONT_KEY = re.compile(r"""^(?:"([^"]*)"|'([^']*)'|([^\s:#"'-][^:]*?))\s*:(?:\s|$)""")


def front_keys(text):
    """Top-level frontmatter keys, unquoted, one entry per occurrence."""
    found = (FRONT_KEY.match(line) for line in split(text.replace("\r\n", "\n"))[0])
    return [next(group for group in match.groups() if group is not None) for match in found if match]


def case_generator_edges():
    edge("CRLF frontmatter and body keep their CRLF bytes when stale output is rewritten",
         lambda text: text.replace("additionalProperties: false", "additionalProperties: true", 1).replace("\n", "\r\n"),
         lambda before, after: "\n" not in after.replace("\r\n", "")
         and after.split("\r\n---\r\n", 1)[1] == before.split("\r\n---\r\n", 1)[1])
    edge("a quoted structured key is replaced, never duplicated",
         lambda text: text.replace("\nstructured: true\n", '\n"structured": true\n', 1),
         lambda before, after: front_keys(after).count("structured") == 1 and '"structured"' not in after)
    edge("an indentationless output sequence is replaced whole, never orphaned",
         lambda text: re.sub(r"\noutput:\n(?:  .*\n)+", "\noutput:\n- stale\n- stale\n", text, count=1),
         lambda before, after: "- stale" not in after and front_keys(after).count("output") == 1)
    edge("a dash-prefixed sibling key after a stale output survives byte-for-byte",
         lambda text: re.sub(r"(\noutput:\n(?:  .*\n)+)", r"\1-mode: keep\n", text, count=1)
         .replace("additionalProperties: false", "additionalProperties: true", 1),
         lambda before, after: "\n-mode: keep\n" in after.split("\n---\n", 1)[0])
    edge("a commented indentationless output sequence leaves no orphan item, and a comment before the next key stays",
         lambda text: re.sub(r"\noutput:\n(?:  .*\n)+", "\noutput:\n# stale note\n- stale\n# about mode\nmode: keep\n", text, count=1),
         lambda before, after: "- stale" not in after and "# stale note" not in after
         and "\n# about mode\nmode: keep\n" in after)
    edge("an escaped quoted structured key is replaced, never duplicated",
         lambda text: text.replace("\nstructured: true\n", '\n"struc\\u0074ured": true\n', 1),
         lambda before, after: "struc\\u0074ured" not in after
         and after.split("\n---\n", 1)[0].count("\nstructured: true\n") == 1)


def refused(name, rewrite):
    """Regenerate one agent after `rewrite(text)`: the generator must exit 2 with its bytes unchanged."""
    with rewritten_qa(rewrite) as (_root, qa, before, run):
        check(name, run.returncode == 2 and qa.read_bytes() == before.encode("utf-8") and "nothing written" in run.stderr,
              f"exit {run.returncode}: {run.stderr[:300]}")


def lookalike_in_description(line):
    """A stale output plus a multiline single-quoted description whose middle line spells `line`."""
    description = f"\ndescription: 'first\n{line}\nlast'\n"
    return lambda text: re.sub(r"\ndescription: .*\n", lambda _match: description, text, count=1) \
        .replace("additionalProperties: false", "additionalProperties: true", 1)


def case_generator_guard():
    # Each also fails if the pre-write guard is deleted: the lossy rewrite would then exit 0.
    refused("a bare output: line inside a multiline description is refused, never deleted",
            lookalike_in_description("output: middle"))
    refused("an escaped quoted output key inside a multiline description is refused, never deleted",
            lookalike_in_description('"out\\u0070ut": middle'))


def main():
    for case in (case_projection, case_refusals, case_fresh_read, case_generator, case_generator_edges,
                 case_generator_guard):
        try:
            case()
        except Exception as error:  # noqa: BLE001 — a crashing case is a failing case, reported by name
            check(case.__name__, False, repr(error))
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
