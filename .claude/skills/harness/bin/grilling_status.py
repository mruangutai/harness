"""Grilling-note lifecycle front-matter: the one parser and writer (FEAT-53 T-25, D-26).

A grilling note begins with a YAML front-matter block carrying exactly two keys:

    ---
    status: open | handed-off | abandoned
    became: null | FEAT-NN-slug | BUG-NN-slug
    ---

`became` is a full feature id only for `handed-off`; every other status carries null. Both
check-state (INV-45) and the dashboard collector read notes through `parse`, so the rule
is spelled once here. Writers go through `mark`, which is idempotent and refuses a
conflicting hand-off.
"""
import re

STATUSES = ("open", "handed-off", "abandoned")
FEATURE_ID = re.compile(r"^(?:FEAT|BUG)-\d+(?:-[a-z0-9]+)+$")
_FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)
_LINE = re.compile(r"^([a-z_]+):[ \t]*(.*?)[ \t]*$")


class GrillingStatusError(ValueError):
    """The front-matter is missing, malformed, or violates the lifecycle rule."""


def _fields(text):
    """The front-matter mapping, exactly {status, became}; raises on any other shape."""
    match = _FRONT.match(text)
    if match is None:
        raise GrillingStatusError("no front-matter block (---/status/became/---) at the top of the note")
    fields = {}
    for line in match.group(1).splitlines():
        entry = _LINE.match(line)
        if entry is None:
            raise GrillingStatusError(f"front-matter line is not `key: value`: {line!r}")
        fields[entry.group(1)] = entry.group(2)
    if set(fields) != {"status", "became"}:
        raise GrillingStatusError(f"front-matter keys must be exactly status and became, got {sorted(fields)}")
    return fields


def _became(status, raw):
    """The became value checked against the status: a full id for handed-off, null otherwise."""
    became = None if raw in ("null", "~", "") else raw.strip("'\"")
    if status == "handed-off":
        if became is None or not FEATURE_ID.match(became):
            raise GrillingStatusError(f"handed-off requires became to be a full FEAT-NN-slug or BUG-NN-slug id, got {became!r}")
    elif became is not None:
        raise GrillingStatusError(f"status {status} must carry became: null, got {became!r}")
    return became


def parse(text):
    """(status, became) from a note's text; raises GrillingStatusError naming the fault."""
    fields = _fields(text)
    status = fields["status"]
    if status not in STATUSES:
        raise GrillingStatusError(f"status {status!r} is not one of {', '.join(STATUSES)}")
    return status, _became(status, fields["became"])


def render(status, became):
    """The front-matter block for (status, became), validated through `parse`."""
    block = f"---\nstatus: {status}\nbecame: {became if became is not None else 'null'}\n---\n"
    parse(block + "# x\n")
    return block


def strip(text):
    """The note body without its front-matter block."""
    match = _FRONT.match(text)
    return text[match.end():] if match else text


def mark(text, status, became=None):
    """The note text with its front-matter set to (status, became).

    Idempotent: marking a note that already carries the same values returns it unchanged.
    A note already handed off to a different feature is a conflict, never a silent rewrite.
    """
    try:
        current = parse(text)
    except GrillingStatusError:
        current = None
    if current == (status, became):
        return text
    if current is not None and current[0] == "handed-off" and status == "handed-off" and current[1] != became:
        raise GrillingStatusError(f"note is already handed off to {current[1]}, not {became}")
    return render(status, became) + strip(text)


def check_exists(became, root):
    """True when `became` names a feature directory under root/.harness/*/features/."""
    import glob
    import os
    return bool(glob.glob(os.path.join(root, ".harness", "*", "features", became)))
