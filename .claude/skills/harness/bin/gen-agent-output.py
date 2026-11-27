#!/usr/bin/env python3
"""Write each harness persona's digest schema into its agent definition (BUG-2565 D-01).

usage: gen-agent-output.py [--check] [ROOT]

For every persona in digest_schema.PERSONAS, ROOT/.omp/agents/<persona>.md gets two top-level
frontmatter keys, generated and never hand-edited: `structured: true`, which binds the child's
yield to a schema while global task.structured stays off, and `output:`, the provider
projection of schemas/digest/<persona>.json + common.json (digest_projection.provider_bundle).
Every other frontmatter line and the body stay byte-identical.

Without --check it writes each file whose bytes change and prints `wrote RELPATH`. With
--check it writes nothing, prints `DRIFT RELPATH` per stale agent and exits 1, else prints
`agent output: ok`. --check is a generator self-test aid; check-omp-port.py is the drift gate.
A missing agent file or a schema that cannot be projected exits 2.
"""
from pathlib import Path
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import digest_projection  # noqa: E402
import digest_schema  # noqa: E402

DEFAULT_ROOT = Path(__file__).resolve().parents[4]


def render(text, bundle):
    """`text` with its frontmatter's structured/output keys replaced by freshly rendered ones,
    inserted immediately before the closing `---`."""
    lines = text.split("\n")
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        raise ValueError("no frontmatter block")
    close = lines.index("---", 1)
    kept, skipping = [], False
    for line in lines[1:close]:
        if skipping and line.startswith(" "):
            continue
        skipping = line.startswith("output:")
        if skipping or line.startswith("structured:"):
            continue
        kept.append(line)
    dumped = yaml.safe_dump(bundle, sort_keys=False, default_flow_style=False, allow_unicode=True, width=4096)
    output = ["output:", *("  " + line for line in dumped.rstrip("\n").split("\n"))]
    return "\n".join([lines[0], *kept, "structured: true", *output, *lines[close:]])


def main(argv):
    check = "--check" in argv
    rest = [arg for arg in argv if arg != "--check"]
    if len(rest) > 1 or any(arg.startswith("-") for arg in rest):
        print("usage: gen-agent-output.py [--check] [ROOT]", file=sys.stderr)
        return 2
    root = Path(rest[0]).resolve() if rest else DEFAULT_ROOT
    schemas = root / ".claude/skills/harness/schemas/digest"
    drift = []
    for persona in digest_schema.PERSONAS:
        path = root / ".omp/agents" / f"{persona}.md"
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"{rel}: agent definition missing", file=sys.stderr)
            return 2
        try:
            rendered = render(text, digest_projection.provider_bundle(persona, schemas))
        except digest_projection.ProjectionError as error:
            print(error, file=sys.stderr)
            return 2
        except ValueError as error:
            print(f"{rel}: {error}", file=sys.stderr)
            return 2
        if rendered == text:
            continue
        if check:
            drift.append(rel)
            print(f"DRIFT {rel}")
        else:
            path.write_text(rendered, encoding="utf-8")
            print(f"wrote {rel}")
    if check and not drift:
        print("agent output: ok")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
