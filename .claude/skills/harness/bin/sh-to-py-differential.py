#!/usr/bin/env python3
"""Prove a .sh -> .py conversion changed no observable behaviour (issue #1674).

WHY THIS EXISTS AND WHY IT IS A SCRIPT, NOT A TEST. The conversion moves ~6,600
lines of Python out of `.sh` heredocs where no Python tool can read them. Every
one of those files is a gate, a validator or a CLI whose exit code routes control
flow, so "it still works" is not a judgement anyone should make by reading a diff.
This captures what a caller can observe -- exit status, stdout, stderr -- across a
corpus of real inputs BEFORE the move, replays it after, and requires the two to
be identical byte for byte.

It is deliberately a throwaway proof rather than a permanent suite. A test that
asserts "the old and new implementations agree" has no meaning once the old one is
deleted, and keeping it would be exactly the parity-harness mistake BUG-285 made:
policing two implementations instead of having one.

USAGE
  capture:  sh-to-py-differential.py capture <tool> <baseline.json>
  verify:   sh-to-py-differential.py verify  <tool> <baseline.json>

`<tool>` is a bare name such as `check-expertise`; the runner resolves
`<tool>.sh` when capturing and `<tool>.py` when verifying, so the SAME corpus
runs against both. A corpus case that crashes the runner is a FAILED case, never
a skipped one -- a proof that can silently cover nothing is worse than no proof.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BIN, "..", "..", "..", ".."))


def corpus(tool, scratch, impl):
    """Cases to run. Real repository inputs plus the edge cases.

    A case is `{"argv": [...], "cwd": <dir>, "isolate": bool}`. Edge cases are not
    decoration: argument handling and root resolution are the parts that move from
    shell into Python, so usage errors, working directory and the refusal path are
    precisely where a conversion goes wrong. Exit 2 paths matter as much as exit 0.

    `isolate` copies bin/ to a scratch tree with NO harness marker above it and runs
    the copy there. That is the only way to reach the "no root could be resolved"
    branch, which is a refusal the real tree can never produce.
    """
    if tool == "check-expertise":
        exp = os.path.join(ROOT, ".harness", "expertise")
        cases = [
            [],                                            # no args -> usage, exit 2
            ["/nonexistent/path.md"],                      # missing -> exit 2
            [scratch],                                     # empty dir -> "nothing to check"
            [exp],                                         # real dir, expanded and sorted
        ]
        if os.path.isdir(exp):
            mds = sorted(f for f in os.listdir(exp) if f.endswith(".md"))
            cases += [[os.path.join(exp, m)] for m in mds]          # each real file
            if len(mds) >= 2:                                        # multi-file argv
                cases.append([os.path.join(exp, mds[0]), os.path.join(exp, mds[1])])
        for seg in sorted(os.listdir(os.path.join(ROOT, ".harness"))):
            d = os.path.join(ROOT, ".harness", seg, "expertise")
            if os.path.isdir(d):
                cases.append([d])                                    # repository tier
        # synthetic violations: the failing path must be proven too, not just the clean one
        bad = os.path.join(scratch, "bad.md")
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write("## Patterns\n- P-01: " + "word " * 80 + "\n## Bogus\n- X-01: FEAT-12 T-03 #55\n")
        cases.append([bad])
        empty = os.path.join(scratch, "empty.md")
        open(empty, "w", encoding="utf-8").close()
        cases.append([empty])
        return [{"argv": a} for a in cases]
    if tool == "check-state":
        # Takes NO arguments: the shell wrapper passes only $root and $_selfdir to
        # the interpreter and never forwards "$@". Stray args must stay ignored.
        # The wrapper also cd's to the root, so the answer must not depend on cwd --
        # that is the property most likely to break when the cd moves into Python.
        return [
            {"argv": []},
            {"argv": [], "cwd": os.path.join(ROOT, ".claude", "skills", "harness", "bin")},
            {"argv": [], "cwd": os.path.join(ROOT, ".harness")},
            {"argv": [], "cwd": scratch},                       # outside the repo entirely
            {"argv": ["--nonsense", "extra"]},                  # ignored, not an error
            {"argv": [], "isolate": True},                      # no root -> refuse, exit 2
        ]
    raise SystemExit(f"no corpus defined for {tool!r} -- add one before converting it")


def run(impl, case, scratch):
    argv, cwd = case.get("argv", []), case.get("cwd", ROOT)
    if case.get("isolate"):
        # Copy the bin dir somewhere with no harness marker above it. shutil.copytree
        # keeps the relative layout the script resolves its siblings through.
        iso = os.path.join(scratch, "isolated")
        if not os.path.exists(iso):
            shutil.copytree(BIN, iso)
        impl, cwd = os.path.join(iso, os.path.basename(impl)), iso
    p = subprocess.run([impl] + argv, capture_output=True, text=True, cwd=cwd)
    # Absolute paths leak roots that differ between capture and verify: the checkout
    # (harmless but noisy) and the scratch dir (a fresh mkdtemp each run). Without
    # scrubbing both, synthetic cases report false differences and the proof reddens
    # for reasons unrelated to the change, which teaches you to ignore it.
    def scrub(s):
        return s.replace(ROOT, "<ROOT>").replace(scratch, "<SCRATCH>")
    return {"case": {"argv": [scrub(a) for a in argv], "cwd": scrub(cwd),
                     "isolate": bool(case.get("isolate"))},
            "exit": p.returncode, "stdout": scrub(p.stdout), "stderr": scrub(p.stderr)}


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("capture", "verify"):
        raise SystemExit(__doc__)
    mode, tool, store = sys.argv[1], sys.argv[2], sys.argv[3]
    impl = os.path.join(BIN, f"{tool}.sh" if mode == "capture" else f"{tool}.py")
    if not os.path.exists(impl):
        raise SystemExit(f"{impl} does not exist")

    with tempfile.TemporaryDirectory() as scratch:
        results = [run(impl, case, scratch) for case in corpus(tool, scratch, impl)]

    if mode == "capture":
        with open(store, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)
        print(f"captured {len(results)} cases from {os.path.basename(impl)} -> {store}")
        codes = sorted({r["exit"] for r in results})
        print(f"exit codes observed: {codes}")
        if codes == [0]:
            # A corpus that only ever succeeds cannot detect a conversion that
            # breaks failure handling -- which is most of what argument parsing does.
            print("WARNING: no non-zero exit in the corpus; failure paths are unproven")
        return 0

    baseline = json.load(open(store, encoding="utf-8"))
    if len(baseline) != len(results):
        print(f"FAIL: corpus size changed ({len(baseline)} -> {len(results)})")
        return 1
    bad = 0
    for b, a in zip(baseline, results):
        diffs = [k for k in ("exit", "stdout", "stderr") if b[k] != a[k]]
        if diffs:
            bad += 1
            desc = ' '.join(b['case']['argv']) or '<no args>'
            if b['case'].get('isolate'):
                desc += ' [isolated: no harness root]'
            desc += f" (cwd {b['case']['cwd']})"
            print(f"FAIL {desc}: differs in {', '.join(diffs)}")
            for k in diffs:
                print(f"  --- {k} before ---\n{b[k]!r}\n  --- {k} after ---\n{a[k]!r}")
    print(f"{len(results) - bad}/{len(results)} cases byte-identical")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
