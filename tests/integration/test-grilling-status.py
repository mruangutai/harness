#!/usr/bin/env python3
"""Grilling-note lifecycle fixtures (FEAT-53 T-25, D-26): the parser, the writer, the backfill
tool's check mode, and INV-45 as check-state reports it."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))
import grilling_status as gs  # noqa: E402

FAILURES = []
BODY = "# Grilling — x — 2026-09-16\n\n## Destination\nx\n"


def check(name, condition, detail=""):
    print(f"{'PASS ' if condition else 'FAIL '} {name}{' — ' + detail if detail else ''}")
    if not condition:
        FAILURES.append(name)


def refuses(fn, needle):
    try:
        fn()
    except gs.GrillingStatusError as exc:
        return needle in str(exc)
    return False


def lifecycle_cases():
    fresh = gs.mark(BODY, "open")
    check("creation is open with null became", gs.parse(fresh) == ("open", None) and fresh.startswith("---\nstatus: open\nbecame: null\n---\n"))
    check("creation preserves the body", gs.strip(fresh) == BODY)
    planned = gs.mark(fresh, "handed-off", "FEAT-90-thing")
    check("plan intake hands off with the full id", gs.parse(planned) == ("handed-off", "FEAT-90-thing"))
    patched = gs.mark(fresh, "handed-off", "BUG-91-fix-thing")
    check("patch intake hands off with the full id", gs.parse(patched) == ("handed-off", "BUG-91-fix-thing"))
    check("abandonment records abandoned with null became", gs.parse(gs.mark(fresh, "abandoned")) == ("abandoned", None))
    check("hand-off is idempotent", gs.mark(planned, "handed-off", "FEAT-90-thing") == planned)
    check("conflicting hand-off refuses", refuses(lambda: gs.mark(planned, "handed-off", "FEAT-92-other"), "already handed off to FEAT-90-thing"))
    check("short id is not a full feature id", refuses(lambda: gs.mark(fresh, "handed-off", "FEAT-90"), "full FEAT-NN-slug"))


def invariant_cases():
    check("missing block is rejected", refuses(lambda: gs.parse(BODY), "no front-matter block"))
    check("unknown status is rejected", refuses(lambda: gs.parse("---\nstatus: paused\nbecame: null\n---\n" + BODY), "not one of"))
    check("handed-off without became is rejected", refuses(lambda: gs.parse("---\nstatus: handed-off\nbecame: null\n---\n" + BODY), "requires became"))
    check("open with became is rejected", refuses(lambda: gs.parse("---\nstatus: open\nbecame: FEAT-90-thing\n---\n" + BODY), "must carry became: null"))
    check("extra key is rejected", refuses(lambda: gs.parse("---\nstatus: open\nbecame: null\nowner: me\n---\n" + BODY), "exactly status and became"))


def checkout(tmp):
    root = Path(tmp)
    (root / ".harness" / "notes").mkdir(parents=True)
    (root / ".harness" / "harness" / "features" / "FEAT-90-thing").mkdir(parents=True)
    return root


def write_note(root, name, text):
    (root / ".harness" / "notes" / name).write_text(text, encoding="utf-8")


def backfill_check(root, manifest=None):
    cmd = [sys.executable, str(BIN / "backfill-grilling-status.py"), "--check", "--root", str(root)]
    if manifest:
        cmd += ["--manifest", str(manifest)]
    done = subprocess.run(cmd, capture_output=True, text=True)
    return done.returncode, done.stdout


def tool_cases():
    with tempfile.TemporaryDirectory() as tmp:
        root = checkout(tmp)
        write_note(root, "grilling-a-2026-09-16.md", gs.mark(BODY, "handed-off", "FEAT-90-thing"))
        write_note(root, "grilling-b-2026-09-16.md", gs.mark(BODY, "abandoned"))
        code, out = backfill_check(root)
        check("check mode passes a marked corpus", code == 0 and "0 fault(s)" in out, out.strip().splitlines()[-1])
        code2, out2 = backfill_check(root)
        check("check mode is idempotent", (code2, out2) == (code, out))
        write_note(root, "grilling-c-2026-09-16.md", gs.mark(BODY, "handed-off", "FEAT-99-ghost"))
        code, out = backfill_check(root)
        check("check mode fails a hand-off to a missing feature", code == 1 and "FEAT-99-ghost" in out)
        write_note(root, "grilling-c-2026-09-16.md", BODY)
        code, out = backfill_check(root)
        check("check mode fails an unmarked note", code == 1 and "no front-matter" in out)
        manifest = root / "m.yaml"
        manifest.write_text("schema: grilling-status-backfill/1\nnotes:\n  - path: .harness/notes/grilling-c-2026-09-16.md\n    status: conflict\n    became: null\n    reviewed: false\n", encoding="utf-8")
        code, out = backfill_check(root, manifest)
        check("check mode reports an unresolved manifest entry", "unresolved" in out)
        applied = subprocess.run([sys.executable, str(BIN / "backfill-grilling-status.py"), "apply", "--root", str(root), "--manifest", str(manifest)], capture_output=True, text=True)
        check("apply refuses an unreviewed manifest", applied.returncode != 0 and "REFUSED" in (applied.stderr + applied.stdout))


def repository_cases():
    manifest = ROOT / ".harness" / "notes" / "grilling-status-backfill-2026-09-15.yaml"
    code, out = backfill_check(ROOT, manifest)
    check("this repository's notes and manifest pass", code == 0, out.strip().splitlines()[-1] if out else "")
    src = (BIN / "check-state.py").read_text(encoding="utf-8")
    check("check-state INV-45 reads through grilling_status.parse", "INV-45" in src and "grilling_status" in src and "_gs45.parse(" in src)


def main():
    lifecycle_cases()
    invariant_cases()
    tool_cases()
    repository_cases()
    raise SystemExit(1 if FAILURES else 0)


if __name__ == "__main__":
    main()
