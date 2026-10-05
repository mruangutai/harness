#!/usr/bin/env python3
"""worktree-state.py — assert or repair a checkout's sparse feature layout (FEAT-1559, #1559).

    worktree-state.py --verify [--checkout PATH] [--json]
    worktree-state.py --repair [--checkout PATH] [--json]

A record-bearing checkout — a planning worktree under `.claude/worktrees/<segment>/<id>` or a
validator pin under `.claude/worktrees/.pins/<feature>--<run-id>--<persona>` — materialises its
ACTIVE feature directory and no other; every other feature is read from the main corpus at the
owner root (feature_corpus.py). A plain clone, a code-only checkout and an arbitrary worktree are
not record-bearing: both modes report the no-op and exit 0.

EXITS. Every detected category is reported, and the exit names the first present in this order:

    8  dirty         class-C work in the tree (below); repair refuses and touches nothing
    3  cone          sparse-checkout is off, not cone mode, not the derived cone, or the active
                     feature is ambiguous
    4  skip-bits     an index entry's skip-worktree bit disagrees with the cone
    7  materialisation  a feature directory other than the active one is on disk
    2  error         the checkout or its git state could not be read
    0  converged, or a no-op subject

REPAIR CLASSIFIES EVERY CHANGED PATH BEFORE IT MUTATES ANYTHING (operator ruling, 2026-10-04):

    A  outside the cone, absent on disk, index entry == HEAD  → restore the skip bit; no bytes move
    B  outside the cone, present, byte-identical to the index → remove it
    C  real divergence: a modified file, any staged change (staged deletion included), a deletion
       inside the cone, or any untracked or ignored file in a hidden feature directory

Any C anywhere refuses with exit 8 and mutates nothing, mixed A/B/C included. An unstaged
deletion of a hidden feature's file is A by design: writing another feature's record from this
checkout is already forbidden, and the bytes remain in the index and HEAD. Repair does A and B
with `git sparse-checkout set` alone, then removes hidden feature directories left EMPTY; a second
repair finds nothing and changes nothing. Verify never mutates: every git call it makes runs with
`--no-optional-locks`, so not even the index stat cache is refreshed.

The hook tier (post-checkout, post-merge, post-rewrite) is repair's only automatic caller; gates
call `--verify --json` and inspect every structural finding, never one exit code alone.
"""
import argparse
import json
import os
import subprocess
import sys

_BIN = os.path.dirname(os.path.abspath(__file__))
if _BIN not in sys.path:
    sys.path.insert(0, _BIN)

import feature_corpus as fc  # noqa: E402

from feature_corpus import CONE, DIRTY, LABELS, MATERIALISATION, SKIP_BITS  # noqa: E402

ERROR = 2
PRIORITY = tuple((code, LABELS[code]) for code in (DIRTY, CONE, SKIP_BITS, MATERIALISATION))
SELF = os.path.join(".claude", "skills", "harness", "bin", "worktree-state.py")


def finding(code, paths, detail):
    return {"code": code, "label": LABELS[code], "paths": sorted(set(paths)), "detail": detail}


def exit_code(findings):
    present = {f["code"] for f in findings}
    for code, _label in PRIORITY:
        if code in present:
            return code
    return 0


# ---------------------------------------------------------------------------------------------
# Reading the tree — every call read-only
# ---------------------------------------------------------------------------------------------

def _z(text):
    return [p for p in text.split("\0") if p]


def index_entries(checkout):
    """`{path: (skip_worktree, blob, mode)}` for every index entry."""
    tags = {}
    for line in _z(fc.git(checkout, "ls-files", "-z", "-t")):
        tag, path = line[0], line[2:]
        tags[path] = tag
    entries = {}
    for line in _z(fc.git(checkout, "ls-files", "-z", "-s")):
        meta, path = line.split("\t", 1)
        mode, blob = meta.split()[:2]
        entries[path] = (tags.get(path) == "S", blob, mode)
    return entries


def status_entries(checkout):
    """`[(X, Y, path)]` from porcelain v1, renames off, every untracked file listed."""
    out = []
    for item in _z(fc.git(checkout, "status", "--porcelain=v1", "-z", "--no-renames",
                          "--untracked-files=all")):
        out.append((item[0], item[1], item[3:]))
    return out


def current_cone(checkout):
    """`(enabled, cone_mode, dirs)` — the checkout's own sparse configuration."""
    def flag(key):
        proc = subprocess.run(["git", "--no-optional-locks", "config", "--type=bool", "--get",
                               key], cwd=checkout, capture_output=True, text=True)
        return proc.returncode == 0 and proc.stdout.strip() == "true"
    enabled, cone_mode = flag("core.sparseCheckout"), flag("core.sparseCheckoutCone")
    if not enabled:
        return False, cone_mode, []
    proc = subprocess.run(["git", "--no-optional-locks", "sparse-checkout", "list"],
                          cwd=checkout, capture_output=True, text=True)
    dirs = sorted(unquote(line.strip()) for line in proc.stdout.splitlines() if line.strip()) \
        if proc.returncode == 0 else []
    return True, cone_mode, dirs


_C_ESCAPES = {"a": 7, "b": 8, "t": 9, "n": 10, "v": 11, "f": 12, "r": 13, '"': 34, "\\": 92}


def unquote(name):
    """A path as git prints it, decoded: git C-quotes a name holding non-ASCII bytes or special
    characters (`"space \\303\\274"`), and the cone is compared with real names (#2103 panel)."""
    if len(name) < 2 or not (name.startswith('"') and name.endswith('"')):
        return name
    body, out, i = name[1:-1], bytearray(), 0
    while i < len(body):
        if body[i] != "\\":
            out += body[i].encode()
            i += 1
        elif body[i + 1] in _C_ESCAPES:
            out.append(_C_ESCAPES[body[i + 1]])
            i += 2
        else:
            out.append(int(body[i + 1:i + 4], 8))
            i += 4
    return out.decode("utf-8", errors="surrogateescape")


_C_QUOTED = {v: k for k, v in _C_ESCAPES.items()}


def quote(name):
    """`name` C-quoted the way git reads a `--stdin` line, so a name opening with `"` or holding
    a newline arrives as itself (validate c4): every byte outside printable ASCII is octal."""
    out = []
    for byte in os.fsencode(name):
        if byte in _C_QUOTED:
            out.append("\\" + _C_QUOTED[byte])
        elif 32 <= byte < 127:
            out.append(chr(byte))
        else:
            out.append(f"\\{byte:03o}")
    return '"' + "".join(out) + '"'


def stdin_lines(names):
    """One C-quoted name per line: input git's `--stdin` readers decode back to `names`."""
    return "".join(quote(n) + "\n" for n in names)


def hidden_dirs(checkout, active):
    """Feature directories on disk other than the active paths, as relative paths. A checkout
    whose cone dropped `.harness` altogether reaches none — the cone finding reports that break."""
    allowed = set(active)
    out = []
    for name in fc.reached_feature_dirs(checkout):
        segment, fid = name.split("/", 1)
        rel = f".harness/{segment}/features/{fid}"
        if rel not in allowed:
            out.append(rel)
    return out


def files_under(checkout, rel):
    out = []
    for dirpath, _dirnames, filenames in os.walk(os.path.join(checkout, rel)):
        for name in filenames:
            out.append(os.path.relpath(os.path.join(dirpath, name), checkout).replace(os.sep, "/"))
    return sorted(out)


SYMLINK_MODE = "120000"


def _hash(checkout, args, data):
    proc = subprocess.run(["git", "--no-optional-locks", "hash-object", *args], cwd=checkout,
                          input=data, capture_output=True)
    if proc.returncode != 0:
        raise fc.CorpusError(f"git hash-object in {checkout}: "
                             f"{proc.stderr.decode(errors='replace').strip()}")
    return proc.stdout.decode().split()


def present_blobs(checkout, paths, index):
    """`{path: blob}` of each present file's RAW working-tree content, or None when its type
    disagrees with the index. Raw, never through the repository's filters: a clean filter can
    make different bytes hash equal, and B must mean the bytes on disk are the index's (#2103
    panel). A symlink is its link text, as git stores it; hash-object would follow it."""
    files, links, out = [], {}, {}
    for p in paths:
        is_link = os.path.islink(os.path.join(checkout, p))
        if is_link != (index[p][2] == SYMLINK_MODE):
            out[p] = None
        elif is_link:
            links[p] = os.fsencode(os.readlink(os.path.join(checkout, p)))
        else:
            files.append(p)
    if files:
        out.update(zip(files, _hash(checkout, ["--no-filters", "--stdin-paths"],
                                    stdin_lines(files).encode())))
    for p, text in links.items():
        out[p] = _hash(checkout, ["--stdin"], text)[0]
    return out


# ---------------------------------------------------------------------------------------------
# Diagnosis
# ---------------------------------------------------------------------------------------------

def divergent_paths(checkout, index, cone, active):
    """Every class-C path against the TARGET cone, sorted.

    Everything else outside the cone is A (absent, index equal to HEAD) or B (present and
    byte-identical to the index), and git's own sparse reapply settles both. They need no list:
    only a C path changes what repair may do."""
    hidden = hidden_dirs(checkout, active)
    class_c = []
    for x, y, path in status_entries(checkout):
        if x == "?" and y == "?":
            if any(path.startswith(h + "/") for h in hidden):
                class_c.append(path)
            continue
        if x not in " ?" or "U" in (x, y):
            class_c.append(path)            # staged, or unmerged
        elif y in "MT":
            class_c.append(path)            # modified in the working tree
        elif y == "D" and fc.in_cone(path, cone):
            class_c.append(path)            # a deletion inside the cone; outside it is A
    # Ignored files never appear in status; any non-index file in a hidden directory is C.
    for h in hidden:
        class_c.extend(p for p in files_under(checkout, h) if p not in index)
    divergent = set(class_c)
    present = [p for p in index
               if not fc.in_cone(p, cone) and p not in divergent
               and os.path.lexists(os.path.join(checkout, p))]
    blobs = present_blobs(checkout, present, index)
    # A present out-of-cone file is B only when byte-identical to the index.
    class_c.extend(p for p in present if blobs.get(p) != index[p][1])
    return sorted(set(class_c))


def target(sel, configured):
    """`(cone, active_paths)` to judge the checkout against. The exact form, unless the checkout
    still holds the every-segment form it was cut with before its record existed: that form
    hides exactly what the exact one hides, so re-cutting it would be churn, not a repair."""
    pre = sel["pre_record"]
    if configured and configured == pre["cone"]:
        return pre["cone"], pre["active_paths"]
    return sel["cone"], sel["active_paths"]


def diagnose(checkout, sel):
    """Every finding for a record-bearing selection."""
    if sel["refusal"]:
        return [finding(CONE, sel["active_paths"], sel["refusal"])]
    enabled, cone_mode, configured = current_cone(checkout)
    cone, active = target(sel, configured if enabled and cone_mode else None)
    index = index_entries(checkout)
    findings = []
    class_c = divergent_paths(checkout, index, cone, active)
    if class_c:
        findings.append(finding(DIRTY, class_c,
                                f"{len(class_c)} path(s) carry work that repair must not touch"))
    if not enabled:
        findings.append(finding(CONE, cone, "sparse-checkout is not enabled"))
    elif not cone_mode:
        findings.append(finding(CONE, cone, "sparse-checkout is not in cone mode"))
    elif configured != cone:
        missing = sorted(set(cone) - set(configured))
        extra = sorted(set(configured) - set(cone))
        findings.append(finding(CONE, missing + extra,
                                f"cone differs from the derived set: missing "
                                f"{missing or 'none'}, unexpected {extra or 'none'}"))
    wrong = [p for p, (skip, _blob, _mode) in index.items() if skip == fc.in_cone(p, cone)]
    if wrong:
        findings.append(finding(SKIP_BITS, wrong,
                                f"{len(wrong)} index entr(y/ies) with a skip-worktree bit that "
                                f"disagrees with the cone"))
    hidden = hidden_dirs(checkout, active)
    if hidden:
        findings.append(finding(MATERIALISATION, hidden,
                                f"{len(hidden)} feature director(y/ies) other than "
                                f"{sel['active_feature']} on disk"))
    return findings


# ---------------------------------------------------------------------------------------------
# Repair
# ---------------------------------------------------------------------------------------------

def _sparse(checkout, *args, stdin=None):
    proc = subprocess.run(["git", "sparse-checkout", *args], cwd=checkout, input=stdin,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise fc.CorpusError(f"git sparse-checkout {args[0]} in {checkout} exited "
                             f"{proc.returncode}: {proc.stderr.strip()}")


def remove_empty(checkout, rel):
    """Remove `rel` bottom-up if — and only if — it holds no file at all."""
    top = os.path.join(checkout, rel)
    for dirpath, _dirnames, _files in sorted(os.walk(top), key=lambda w: -len(w[0])):
        try:
            os.rmdir(dirpath)
        except OSError:
            return


def repair(checkout, sel):
    """Converge A/B findings. `set` writes the cone only when it differs — git treats an
    unchanged `set` as a no-op and re-applies nothing. The index stat cache is then refreshed:
    git leaves a present hidden file whose stat data is stale ("not up to date … left despite
    sparse patterns"), and every such file was already proved byte-identical (class B). `reapply`
    then restores every skip bit and removes every class-B file against the cone in force."""
    findings = diagnose(checkout, sel)
    code = exit_code(findings)
    if code in (0, DIRTY) or sel["refusal"]:
        return findings, False
    enabled, cone_mode, configured = current_cone(checkout)
    cone, active = target(sel, configured if enabled and cone_mode else None)
    if not (enabled and cone_mode and configured == cone):
        _sparse(checkout, "set", "--cone", "--stdin", stdin=stdin_lines(cone))
    # Exit 1 means "some path needs updating" — a stat difference, here never content (no C).
    subprocess.run(["git", "update-index", "-q", "--refresh"], cwd=checkout,
                   capture_output=True)
    _sparse(checkout, "reapply")
    for rel in hidden_dirs(checkout, active):
        remove_empty(checkout, rel)
    return diagnose(checkout, sel), True


# ---------------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------------

def report(sel, mode, findings, repaired):
    return {"checkout": sel["checkout"], "checkout_class": sel["checkout_class"],
            "active_feature": sel["active_feature"], "artifact_segment": sel["artifact_segment"],
            "mode": mode, "noop": sel["noop"], "repaired": repaired, "findings": findings}


def _finding_lines(finding):
    """One finding's label line, then up to eight of its paths."""
    lines = [f"  {finding['label']} ({finding['code']}): {finding['detail']}"]
    if finding["paths"]:
        more = " …" if len(finding["paths"]) > 8 else ""
        lines.append(f"    {', '.join(finding['paths'][:8])}{more}")
    return lines


def _outcome(code, checkout):
    """The closing line: the remedy for a failing code, else `converged`."""
    repair = f"python3 {SELF} --repair --checkout {checkout}"
    if code == DIRTY:
        return f"  remedy: commit or stash that work (untracked files included), then run {repair}"
    return f"  remedy: {repair}" if code else "  converged"


def render(doc, code):
    head = f"worktree-state: {doc['mode']} {doc['checkout']}"
    if doc["noop"]:
        return f"{head}\n  no-op: {doc['noop']}"
    where = doc["artifact_segment"] or "every segment (no record yet)"
    lines = [f"{head} — {doc['checkout_class']}, {doc['active_feature']} in {where}"]
    if doc["repaired"]:
        lines.append("  repaired: sparse cone re-applied")
    for finding in doc["findings"]:
        lines += _finding_lines(finding)
    lines.append(_outcome(code, doc["checkout"]))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="worktree-state.py", description=__doc__.split("\n")[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify", action="store_true", help="assert the layout; never mutates")
    mode.add_argument("--repair", action="store_true", help="converge the layout (A/B only)")
    parser.add_argument("--checkout", default=os.getcwd(), help="checkout to examine (cwd)")
    parser.add_argument("--json", action="store_true", help="one JSON object on stdout")
    parser.add_argument("--quiet-dirty", action="store_true",
                        help="print nothing when the only finding is dirty work: the converged "
                             "mid-task state, which the hooks must not nag about (exit unchanged)")
    args = parser.parse_args(argv)
    mode_name = "repair" if args.repair else "verify"
    try:
        sel = fc.select(os.path.abspath(args.checkout))
        if sel["noop"]:
            findings, repaired = [], False
        elif args.repair:
            findings, repaired = repair(sel["checkout"], sel)
        else:
            findings, repaired = diagnose(sel["checkout"], sel), False
    except fc.CorpusError as exc:
        if args.json:
            print(json.dumps({"checkout": os.path.abspath(args.checkout), "mode": mode_name,
                              "error": str(exc)}))
        else:
            print(f"worktree-state: {mode_name}: {exc}", file=sys.stderr)
        return ERROR
    code = exit_code(findings)
    if args.quiet_dirty and findings and all(f["code"] == DIRTY for f in findings):
        return code
    doc = report(sel, mode_name, findings, repaired)
    print(json.dumps(doc, indent=2, sort_keys=True) if args.json else render(doc, code))
    return code


if __name__ == "__main__":
    sys.exit(main())
