#!/usr/bin/env python3
"""quarantine.py — the explicit adopt/discard CLI for orphaned canonical writes (FEAT-51 T-04).

FEAT-51's earlier tasks record when a write to a canonical artifact (plan.yaml, BRIEF.md,
feature.json, STATE.md) becomes an orphan — a compatibility-host writer whose session is no
longer live — and redirect it into a quarantine directory instead of losing it silently
(inflight_registry.orphan_write, inflight_registry.quarantine_rel). This tool is the only way
that quarantined content is ever acted on: there is no scheduler, no timer, no TTL, and no
implicit action anywhere in this file. An operator runs one of three subcommands, and only that
command's own effect happens.

  list   — enumerate quarantined files for a feature. Read-only.
  adopt  — replace the canonical artifact with a quarantined one (plan.yaml unions through
           plan-merge.py; the other three replace via harness_merge.locked_update). Leaves the
           quarantine directory in place — adoption is auditable, discard is a separate act.
  discard — remove one quarantine directory tree, and only a directory that resolves under a
            features/*/quarantine/ segment.

python3 stdlib only, plus the two in-repo modules whose rules this tool reuses rather than
restates: inflight_registry (CANONICAL_ARTIFACTS) and harness_merge (locked_update).
"""
import argparse
import datetime
import glob
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness_boundary  # noqa: E402
import harness_merge  # noqa: E402
import inflight_registry  # noqa: E402

# Both adopt and discard share ONE containment rule, applied to the REALPATH, never the
# argument as given (same discipline as harness_merge.require_destination): a dot-dot
# segment or a symlink must not be able to walk this tool's write, or its rm -rf, out of
# the class it owns, AND the words "under <root>" are load-bearing — a path that merely
# LOOKS like a quarantine path anywhere on the filesystem is not enough; it must resolve
# under the SAME root the caller pointed this invocation at. The legal shape is exactly
#   <root>/.harness/<repo>/features/<feature>/quarantine/<one writer dir>[/<basename>]
# — discard's target is the writer dir itself (no trailing basename); adopt's target is a
# file one level deeper. Anything shallower, deeper, or off this shape fails to match.
_QUARANTINE_PATH_RE = re.compile(
    r"\.harness/([^/]+)/features/([^/]+)/quarantine/([^/]+)(?:/([^/]+))?"
)


def _quarantine_containment(root, realpath):
    """Parse REALPATH against the containment rule above, requiring it resolve under ROOT.
    Both sides are realpath'd before comparison — comparing a realpath to a mere abspath is
    the trap here: `_resolve_root` returns abspath, not realpath, and macOS realpaths
    tempfile.mkdtemp()'s `/var/folders/...` to `/private/var/folders/...`, so an abspath-vs-
    realpath comparison would reject every fixture. `os.path.relpath` between the two
    realpaths is what enforces containment: a result starting with `..` or absolute means
    REALPATH is outside ROOT, refused regardless of whether the tail looks quarantine-shaped.
    Returns (repo, feature, writer, basename) on a match — basename is None when realpath
    resolves to the writer directory itself, or a string when it resolves to a file one
    level deeper — or None when realpath is outside root, shallower than, deeper than, or
    otherwise off the shape."""
    root_real = os.path.realpath(root)
    rel = os.path.relpath(realpath, root_real)
    if rel == os.pardir or rel.startswith(os.pardir + os.sep) or os.path.isabs(rel):
        return None
    match = _QUARANTINE_PATH_RE.fullmatch(rel)
    return match.groups() if match else None


def _resolve_root(explicit_root):
    """`--root` wins outright; otherwise the checkout this script's own location implies
    (harness_boundary.resolve_root). Returns None when neither resolves, so a caller can
    report the failure instead of raising past its own argument parsing."""
    if explicit_root:
        return os.path.abspath(explicit_root)
    try:
        return harness_boundary.resolve_root(os.path.dirname(os.path.abspath(__file__)))
    except ValueError:
        return None


def _resolve_path(path, root):
    """A relative --file/--dir is resolved against the checkout root, never against cwd —
    the same convention `--root` exists to make possible."""
    return path if os.path.isabs(path) else os.path.join(root, path)


def _split_agent_session(dirname):
    """The inverse of inflight_registry.quarantine_rel's `f"{agent}-{session_key}"` naming.
    `session_key` is either the literal `nosession` or `session[:8]` of a caller-supplied
    session id, and both are hyphen-free in every caller in this tree, so the LAST hyphen is
    always the boundary between the two — including for agent names that are themselves
    hyphenated, e.g. `harness-backend-dev-12345678`."""
    agent, sep, session = dirname.rpartition("-")
    return (agent, session) if sep else (dirname, "")


def _canonical_for_listing(root, path):
    """The printed canonical= value, derived through the SAME root-anchored
    _quarantine_containment rule _adopt_target uses — list and adopt must never disagree
    about where a file would land, because list is what an operator reads before deciding
    what to adopt. An entry `_quarantine_containment` cannot parse (basename is None, e.g.
    a symlink whose realpath escapes containment) is reported as `<unresolvable>`; list
    stays read-only and keeps exiting 0 on it — it reports, it does not refuse."""
    parts = _quarantine_containment(root, os.path.realpath(path))
    if parts is None or parts[3] is None:
        return "<unresolvable>"
    repo, feature, _writer, basename = parts
    return os.path.join(root, ".harness", repo, "features", feature, basename)


def cmd_list(args):
    root = _resolve_root(args.root)
    if root is None:
        print("quarantine: no checkout root and no --root was given", file=sys.stderr)
        return 1
    pattern = os.path.join(
        root, ".harness", "*", "features", args.feature, "quarantine", "*", "*"
    )
    for path in sorted(glob.glob(pattern)):
        if not os.path.isfile(path):
            continue
        agent, session = _split_agent_session(os.path.basename(os.path.dirname(path)))
        mtime = datetime.datetime.fromtimestamp(
            os.path.getmtime(path), tz=datetime.timezone.utc
        ).isoformat()
        canonical = _canonical_for_listing(root, path)
        print(f"{path} persona={agent} session={session} mtime={mtime} canonical={canonical}")
    return 0


def _run_plan_merge(canonical, quarantined):
    """DELEGATED, NOT REIMPLEMENTED: union-by-id and the byte-identical approval
    carry-forward are plan-merge.py's answer. Both exit codes it can raise here
    (7 — an existing id carries a different value; 8 — the approval mappings differ)
    are surfaced verbatim, stdout and stderr both, never swallowed or collapsed into
    a generic message — an operator must be able to act on either outcome. Returns the
    child's own returncode."""
    bin_dir = os.path.dirname(os.path.abspath(__file__))
    result = subprocess.run(
        [
            sys.executable,
            os.path.join(bin_dir, "plan-merge.py"),
            "apply",
            "--file", canonical,
            "--proposal", quarantined,
        ],
        capture_output=True,
        text=True,
    )
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.returncode


def _adopt_target(root, file_arg):
    """Resolve --file to (canonical, given, resolved) via the shared containment rule.
    `given` is the plain abspath — used for reads and for the ADOPTED message, matching the
    caller's own path exactly. `resolved` is its realpath, used only to defeat a symlink
    escape when parsing containment; canonical is None on refusal, in which case `resolved`
    is what the refusal message reports."""
    given = os.path.abspath(_resolve_path(file_arg, root))
    resolved = os.path.realpath(given)
    parts = _quarantine_containment(root, resolved)
    basename = parts[3] if parts else None
    if parts is None or basename not in inflight_registry.CANONICAL_ARTIFACTS:
        return None, given, resolved
    repo, feature, _writer, basename = parts
    canonical = os.path.join(root, ".harness", repo, "features", feature, basename)
    return canonical, given, resolved


def _refuse_adopt(file_arg, quarantined):
    legal = ", ".join(inflight_registry.CANONICAL_ARTIFACTS)
    print(
        f"REFUSED: adopt only accepts one of {legal}, under a "
        f"features/*/quarantine/*/ directory, not {file_arg!r}.",
        file=sys.stderr,
    )
    print(f"  resolved to: {quarantined}", file=sys.stderr)


def _adopt_payload(canonical, quarantined):
    """Replace CANONICAL with QUARANTINED's content: plan.yaml delegates to plan-merge.py's
    union merge (returns its own returncode); everything else is a locked atomic replace
    via harness_merge.locked_update (returns 0)."""
    if os.path.basename(canonical) == "plan.yaml":
        return _run_plan_merge(canonical, quarantined)
    with open(quarantined, "rb") as fh:
        payload = fh.read()
    harness_merge.locked_update(canonical, lambda _base, payload=payload: payload)
    return 0


def cmd_adopt(args):
    root = _resolve_root(args.root)
    if root is None:
        print("quarantine: no checkout root and no --root was given", file=sys.stderr)
        return 1
    canonical, given, resolved = _adopt_target(root, args.file)
    if canonical is None:
        _refuse_adopt(args.file, resolved)
        return 2
    returncode = _adopt_payload(canonical, given)
    if returncode != 0:
        return returncode
    print(f"ADOPTED {canonical} FROM {given}")
    return 0


def cmd_discard(args):
    root = _resolve_root(args.root)
    if root is None:
        print("quarantine: no checkout root and no --root was given", file=sys.stderr)
        return 1
    target = os.path.realpath(os.path.abspath(_resolve_path(args.dir, root)))
    parts = _quarantine_containment(root, target)
    if parts is None or parts[3] is not None:
        print(
            f"REFUSED: {args.dir} does not resolve under a features/*/quarantine/ directory.",
            file=sys.stderr,
        )
        print(f"  resolved to: {target}", file=sys.stderr)
        return 2
    shutil.rmtree(target)
    print(f"DISCARDED {args.dir}")
    return 0


def main(argv=None):
    argv = list(argv) if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(prog="quarantine.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="list quarantined files for a feature")
    p_list.add_argument("--feature", required=True)
    p_list.add_argument("--root")
    p_list.set_defaults(func=cmd_list)

    p_adopt = sub.add_parser("adopt", help="adopt a quarantined file onto its canonical target")
    p_adopt.add_argument("--file", required=True)
    p_adopt.add_argument("--root")
    p_adopt.set_defaults(func=cmd_adopt)

    p_discard = sub.add_parser("discard", help="discard one quarantine directory")
    p_discard.add_argument("--dir", required=True)
    p_discard.add_argument("--root")
    p_discard.set_defaults(func=cmd_discard)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
