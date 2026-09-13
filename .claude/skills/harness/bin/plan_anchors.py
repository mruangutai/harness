#!/usr/bin/env python3
"""plan_anchors.py — the grammar of a plan task's `files:` entry, and how one resolves
(FEAT-59 SC-07, contract C4).

THE ONE PLACE THE GRAMMAR LIVES. plan-merge.py refuses an illegal entry at write (`apply`,
`add-tasks`, `amend`) and resolves every entry in `check`; harness_yaml.py's plan schema
accepts the same three shapes; check-plan-routes.py strips an anchor to its path before asking
check-domain.sh who owns it. Three readers, one grammar, so a form one of them accepts cannot be
a form another refuses.

Three legal forms:

    path                         a file, existing or to be created inside an existing directory
    path#symbol                  a definition inside the file — a line whose prefix is one of
                                 SYMBOL_PREFIXES followed by the symbol, or the symbol as a
                                 whole token anywhere in the file
    {path: <p>, quote: <q>}      a line of the file that contains <q> verbatim

And one REFUSED form: `path:NN`, a line number. Measured on FEAT-54 (BRIEF ## Problem): the first
build dispatch BLOCKED on five plan paths that four goal-check cycles and three panel cycles had
read without noticing, because nothing resolved them; a line number is worse than a bare path,
since it silently points at different code the moment `main` moves. Refused at WRITE, not
merely reported at check, so it cannot enter a signed plan at all.

python3 stdlib only. Never raises out of `resolve`; `parse` raises AnchorError so a writer can
turn the message into its own refusal.
"""
import glob
import os
import re

LINE_NUMBER_RE = re.compile(r"^(.+):(\d+)$")
GLOB_CHARS = ("*", "?", "[")
SYMBOL_PREFIXES = ("def ", "class ", "function ", "const ", "export ")
_LEGAL = "path, path#symbol, or {path, quote}"


class AnchorError(ValueError):
    """The entry is not one of the three legal forms. The message names the entry."""


def _parse_text(entry):
    if LINE_NUMBER_RE.match(entry):
        raise AnchorError(
            f"{entry!r} is a line-number anchor — a line number does not survive main "
            f"moving. Anchor to a symbol (path#symbol) or to content ({{path, quote}}).")
    path, sep, symbol = entry.partition("#")
    if not path.strip():
        raise AnchorError(f"{entry!r} carries no path before its anchor")
    if sep and not symbol.strip():
        raise AnchorError(f"{entry!r} carries a # with no symbol after it")
    return path, (symbol if sep else None), None


def _parse_mapping(entry):
    if set(entry) != {"path", "quote"}:
        raise AnchorError(
            f"{entry!r} is not a {{path, quote}} mapping — it carries {sorted(map(str, entry))}")
    if not all(isinstance(v, str) and v.strip() for v in entry.values()):
        raise AnchorError(f"{entry!r} needs non-empty strings for both path and quote")
    return entry["path"], None, entry["quote"]


def parse(entry):
    """(path, symbol, quote) for a legal entry, or raise AnchorError naming it.

    Exactly one of `symbol` and `quote` is set for an anchor; both are None for a bare path.
    """
    if isinstance(entry, str):
        return _parse_text(entry)
    if isinstance(entry, dict):
        return _parse_mapping(entry)
    raise AnchorError(f"{entry!r} is not a files entry — legal forms are {_LEGAL}")


def refusals(files):
    """One message per illegal entry in `files`, in order; [] when every entry is legal.

    Never raises: a writer wants EVERY offending entry named in one refusal, not the first."""
    out = []
    for entry in files if isinstance(files, list) else []:
        try:
            parse(entry)
        except AnchorError as exc:
            out.append(str(exc))
    return out


def path_of(entry):
    """The bare path of a legal entry, or the entry itself when it is not one.

    For readers that only need to know WHICH FILE — check-plan-routes.py's resolver asks
    check-domain.sh about paths, and `a.py#foo` matches no grant while `a.py` does. An
    illegal entry is returned unchanged so the reader's own report names what it was given.
    """
    try:
        return parse(entry)[0]
    except AnchorError:
        return entry


def is_glob(path):
    return any(ch in path for ch in GLOB_CHARS)


def _defines(line, symbol):
    """True when `line` is `<prefix> <symbol>` for one of SYMBOL_PREFIXES, symbol whole."""
    stripped = line.lstrip()
    for prefix in SYMBOL_PREFIXES:
        if not stripped.startswith(prefix):
            continue
        rest = stripped[len(prefix):].lstrip()
        if rest.startswith(symbol) and not re.match(r"\w", rest[len(symbol):len(symbol) + 1]):
            return True
    return False


def _symbol_in(text, symbol):
    """True when `symbol` is defined on a prefixed line, or appears as a whole token."""
    if any(_defines(line, symbol) for line in text.splitlines()):
        return True
    return re.search(rf"(?<!\w){re.escape(symbol)}(?!\w)", text) is not None


def _resolve_glob(entry, path, anchored, root):
    if anchored:
        return f"{entry!r}: an anchor cannot sit on a glob"
    if not glob.glob(os.path.join(root, path), recursive=True):
        return f"{path} matches nothing under {root}"
    return None


def _resolve_absent(path, target, anchored, root):
    """A missing file: fine for a bare path whose directory exists, a fault for an anchor."""
    if anchored:
        return f"{path} does not exist under {root}, so its anchor cannot resolve"
    if os.path.isdir(os.path.dirname(target)):
        return None      # a file the task will create, in a directory that exists
    return f"{path} does not exist under {root} and neither does its directory"


def _resolve_content(path, target, symbol, quote):
    """The anchor's own test against the file's text."""
    try:
        with open(target, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        return f"{path} cannot be read: {exc}"
    if symbol is not None:
        if _symbol_in(text, symbol):
            return None
        return f"{path}#{symbol}: no definition or token {symbol!r} in {path}"
    if quote in text:
        return None
    return f"{path} does not contain the quoted text {quote!r}"


def resolve(entry, root):
    """None when `entry` resolves under `root`, else one line saying why it does not.

    A bare path resolves when the file exists OR its parent directory does — a plan may name a
    file its task will create, and a typo'd directory still fails. A symbol or quote anchor
    requires the file to exist and to contain what it names. A glob path resolves when it
    matches at least one file; an anchor cannot sit on a glob.
    """
    try:
        path, symbol, quote = parse(entry)
    except AnchorError as exc:
        return str(exc)
    anchored = symbol is not None or quote is not None
    real_root = os.path.realpath(root)
    target = os.path.realpath(os.path.join(root, path))
    if os.path.commonpath([real_root, target]) != real_root:
        return f"{path} resolves outside {root}"
    if is_glob(path):
        return _resolve_glob(entry, path, anchored, root)
    if not os.path.isfile(target):
        return _resolve_absent(path, target, anchored, root)
    if not anchored:
        return None
    return _resolve_content(path, target, symbol, quote)
