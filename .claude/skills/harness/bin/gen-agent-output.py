#!/usr/bin/env python3
"""Write each harness persona's digest schema into its agent definition (BUG-2565 D-01).

usage: gen-agent-output.py [--check] [ROOT]

For every persona in digest_schema.PERSONAS, ROOT/.omp/agents/<persona>.md gets two top-level
frontmatter keys, generated and never hand-edited: `structured: true`, which binds the child's
yield to a schema while global task.structured stays off, and `output:`, the provider
projection of schemas/digest/<persona>.json + common.json (digest_projection.provider_bundle).
Every other frontmatter line and the body stay byte-identical, line endings included. A
generated key is recognised as YAML reads it, quoted or bare; its value runs through the indented
lines and `- ` sequence items after it, with any blank or comment lines between them. Before a
write, both frontmatters are parsed strictly, and a result that would not parse or would change
any other key or its value is refused.

Without --check it writes each file whose bytes change and prints `wrote RELPATH`. With
--check it writes nothing, prints `DRIFT RELPATH` per stale agent and exits 1, else prints
`agent output: ok`. --check is a generator self-test aid; check-omp-port.py is the drift gate.
A missing agent file, a schema that cannot be projected or a refused frontmatter exits 2 having
written nothing.
"""
from pathlib import Path
import re
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artifact_accessors  # noqa: E402
import digest_projection  # noqa: E402
import digest_schema  # noqa: E402
import harness_yaml  # noqa: E402

DEFAULT_ROOT = Path(__file__).resolve().parents[4]
USAGE = "usage: gen-agent-output.py [--check] [ROOT]"
GENERATED = ("structured", "output")
# A top-level mapping key: double-quoted, single-quoted or plain, then a colon that ends the key.
TOP_KEY = re.compile(r"""(?:"([^"]*)"|'([^']*)'|([^\s:#"'-][^:]*?))\s*:(?:\s|$)""")
# An indentationless sequence item: a dash followed by whitespace or the end of the line.
SEQUENCE_ITEM = re.compile(r"-(?:[ \t\r\n]|$)")


class Refused(Exception):
    """A run that writes nothing: the message is printed and the exit is 2."""


def bare(line):
    return line.rstrip("\r\n")


def top_key(line):
    """The key a top-level frontmatter line opens, as YAML reads it; None for any other line."""
    match = TOP_KEY.match(line)
    if not match:
        return None
    double, single, plain = match.groups()
    if plain is not None:
        return plain
    try:
        return harness_yaml.load_str(f'"{double}"' if double is not None else f"'{single}'", "frontmatter key")
    except harness_yaml.YamlParseError:
        return None


def continues(line):
    """A line inside the value above it: indented, or an indentationless sequence item."""
    return line[:1] in (" ", "\t") or SEQUENCE_ITEM.match(line) is not None


def interlude(line):
    """A blank or comment line, which belongs to a value only if the value continues after it."""
    return not bare(line).strip() or line.startswith("#")


def value_end(front, start):
    """The index just past the value of the key at `front[start]`: its continuation lines and
    any blank or comment lines between them, never those trailing its last continuation line."""
    end = start + 1
    for index in range(start + 1, len(front)):
        if continues(front[index]):
            end = index + 1
        elif not interlude(front[index]):
            break
    return end


def kept(front):
    """Frontmatter lines without the generated keys and their values; the rest byte-identical."""
    out, index = [], 0
    while index < len(front):
        if top_key(front[index]) in GENERATED:
            index = value_end(front, index)
        else:
            out.append(front[index])
            index += 1
    return out


def closing(lines):
    """The index of the frontmatter's closing `---` line."""
    ends = [index for index, line in enumerate(lines) if bare(line) == "---"]
    if len(ends) < 2 or ends[0] != 0:
        raise ValueError("no frontmatter block")
    return ends[1]


def other_entries(front, what):
    """The frontmatter's top-level entries outside GENERATED, keys and values, read by the
    canonical strict reader (duplicate keys refused)."""
    try:
        parsed, _body = artifact_accessors.load_frontmatter("---\n" + "".join(front) + "---\n", what)
    except artifact_accessors.ArtifactAccessError as error:
        raise ValueError(str(error)) from None
    return {key: value for key, value in parsed.items() if key not in GENERATED}


def render(text, bundle):
    """`text` with its frontmatter's generated keys replaced by freshly rendered ones, inserted
    immediately before the closing `---` in the file's own line ending. Refused when the result
    would not parse or would change any other key or its value."""
    lines = [line for line in re.split(r"(?<=\n)", text) if line]
    close = closing(lines)
    newline = lines[0][len(bare(lines[0])):] or "\n"
    dumped = yaml.safe_dump(bundle, sort_keys=False, default_flow_style=False, allow_unicode=True, width=4096)
    generated = ["structured: true", "output:", *("  " + line for line in dumped.rstrip("\n").split("\n"))]
    front = [*kept(lines[1:close]), *(line + newline for line in generated)]
    if other_entries(front, "regenerated") != other_entries(lines[1:close], "current"):
        raise ValueError("regeneration would change another frontmatter key or its value")
    return "".join([lines[0], *front, *lines[close:]])


def regenerate(root, persona):
    """(path, relpath, current text, rendered text) for one persona's agent definition."""
    path = root / ".omp/agents" / f"{persona}.md"
    rel = path.relative_to(root).as_posix()
    try:
        text = path.read_bytes().decode("utf-8")
    except FileNotFoundError:
        raise Refused(f"{rel}: agent definition missing") from None
    try:
        bundle = digest_projection.provider_bundle(persona, root / digest_projection.SCHEMA_RELPATH)
        return path, rel, text, render(text, bundle)
    except digest_projection.ProjectionError as error:
        raise Refused(str(error)) from None
    except ValueError as error:
        raise Refused(f"{rel}: {error}") from None


def parse(argv):
    """(check, root), or None on a usage error."""
    rest = [arg for arg in argv if arg != "--check"]
    if len(rest) > 1 or any(arg.startswith("-") for arg in rest):
        return None
    return "--check" in argv, (Path(rest[0]).resolve() if rest else DEFAULT_ROOT)


def main(argv):
    parsed = parse(argv)
    if parsed is None:
        print(USAGE, file=sys.stderr)
        return 2
    check, root = parsed
    try:
        agents = [regenerate(root, persona) for persona in digest_schema.PERSONAS]
    except Refused as error:
        print(f"{error}; nothing written", file=sys.stderr)
        return 2
    return report([(path, rel, rendered) for path, rel, text, rendered in agents if rendered != text], check)


def report(stale, check):
    """Write (or, with --check, name) each stale agent; the exit status."""
    for path, rel, rendered in stale:
        if check:
            print(f"DRIFT {rel}")
        else:
            path.write_bytes(rendered.encode("utf-8"))
            print(f"wrote {rel}")
    if check and not stale:
        print("agent output: ok")
    return 1 if check and stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
