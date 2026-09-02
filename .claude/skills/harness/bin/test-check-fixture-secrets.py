#!/usr/bin/env python3
"""Tests for check-fixture-secrets.sh (issue #981).

FEAT-44's T-01 ran an inline scrub sweep, once, in a task's verify: block, with two
blind spots that shipped invisibly: the secret pattern could not match an Anthropic
API key (`sk-ant-api03-...` breaks the old `[A-Za-z0-9]{8}` requirement at the first
hyphen), and the identity check bound `$(whoami)` — the invoker, not the capturer —
so it passed vacuously in CI. This suite pins both fixes with the exact credential
shape that escaped before, proves the positive controls actually discriminate, and
RED-proofs the sk- fix against the original broken pattern.

    ./test-check-fixture-secrets.py     -> exit 0 all pass, 1 otherwise
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GUARD = os.environ.get("CHECK_FIXTURE_SECRETS_BIN") or os.path.join(
    HERE, "check-fixture-secrets.sh")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


def write(tmp, name, content):
    path = os.path.join(tmp, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def fire(*paths, guard=GUARD):
    return subprocess.run([guard, *paths], capture_output=True, text=True)


def run_cases():
    tmp = tempfile.mkdtemp(prefix="check-fixture-secrets-")

    # ---- THE ACTUAL DEFECT (#981, blind spot 1): a real Anthropic key shape. The
    # original sweep's `sk[-_][A-Za-z0-9]{8}` breaks at the hyphen three characters
    # into "ant" and never matches this.
    anthropic_key = write(tmp, "anthropic.jsonl",
                          '{"event": "auth", "key": "sk-ant-api03-'
                          'AbCdEfGh12345678-XyZ99900112233"}\n')
    r = fire(anthropic_key)
    check("an sk-ant- key is caught — the exact shape that escaped before",
          r.returncode == 1 and "BLOCKED" in r.stderr, f"rc={r.returncode} {r.stderr!r}")

    # ---- A hyphenated sk-proj- key, the other shape item 1 names.
    proj_key = write(tmp, "proj.jsonl", '{"key": "sk-proj-AbCdEfGh-1234-5678-XyZ9"}\n')
    r = fire(proj_key)
    check("an sk-proj- key (hyphenated, non-Anthropic) is also caught",
          r.returncode == 1 and "BLOCKED" in r.stderr, f"rc={r.returncode} {r.stderr!r}")

    # ---- NEGATIVE CONTROL: a clean file passes.
    clean = write(tmp, "clean.jsonl", '{"event": "tool_call", "name": "Read"}\n')
    r = fire(clean)
    check("a genuinely clean file passes, exit 0",
          r.returncode == 0 and "clean" in r.stdout, f"rc={r.returncode} {r.stdout!r}")

    # ---- REGRESSION: pre-existing coverage (GitHub PAT, AWS key, PEM header) is
    # unchanged by the sk- fix.
    for label, content in (
        ("a github_pat token", 'token=github_pat_11ABCDEFG01234567\n'),
        ("a ghp token", 'GH_TOKEN=ghp_ABCDEFGH12345678\n'),
        ("an AWS access key id", 'AKIA' + 'A' * 16 + '\n'),
        ("a PEM private key header", '-----BEGIN PRIVATE KEY-----\n'),
        ("a credential_pin literal", 'credential_pin=xyz\n'),
    ):
        f = write(tmp, "regress-" + label.replace(" ", "-") + ".txt", content)
        r = fire(f)
        check(f"regression: {label} is still caught",
              r.returncode == 1 and "BLOCKED" in r.stderr, f"rc={r.returncode}")

    # ---- THE ACTUAL DEFECT (#981, blind spot 2): a baked-in home-directory path,
    # matched regardless of who is RUNNING this check. `whoami` on the machine
    # running this test is never literally "alice" or "bob-dev-laptop", so a
    # $(whoami)-bound check would pass this vacuously; the home-directory-shape
    # check must not.
    leaked_path = write(tmp, "leak.jsonl",
                        '{"cwd": "/Users/alice-not-the-invoker/project/repo"}\n')
    r = fire(leaked_path)
    check("a baked-in /Users/<name>/ path is caught, independent of $(whoami)",
          r.returncode == 1 and "home-directory" in r.stderr, f"rc={r.returncode} {r.stderr!r}")

    leaked_home = write(tmp, "leak-home.jsonl",
                        '{"path": "/home/bob-dev-laptop/.config/x"}\n')
    r = fire(leaked_home)
    check("a baked-in /home/<name>/ path is caught too",
          r.returncode == 1 and "home-directory" in r.stderr, f"rc={r.returncode}")

    # ---- Multiple files: every file is checked, not short-circuited on the first.
    r = fire(clean, anthropic_key, leaked_path)
    check("multiple files: all are checked, one dirty file still blocks",
          r.returncode == 1 and r.stderr.count("BLOCKED") >= 2,
          f"rc={r.returncode} stderr={r.stderr!r}")

    # ---- Misuse: no files given is a loud usage error, not a silent clean pass.
    r = fire()
    check("no files given exits 2 (usage), never 0",
          r.returncode == 2, f"rc={r.returncode} {r.stderr!r}")

    # ---- Misuse: a missing/unreadable file is BLOCKED, not silently skipped as
    # clean — an absence of the file must never read as an absence of the secret.
    r = fire(os.path.join(tmp, "does-not-exist.jsonl"))
    check("a missing file blocks rather than silently passing as clean",
          r.returncode == 1 and "not a readable file" in r.stderr, f"rc={r.returncode}")

    # ---- FALSE-POSITIVE REGRESSION (code review of PR #1189): the unanchored
    # sk-[A-Za-z0-9-]{16,} branch matched ordinary kebab-case text — "task-runner-
    # for-this-project", "ask-your-teammate-about-this-config" — any word ending
    # `-sk` followed by 16+ more hyphen/alnum characters, which saturates a
    # captured transcript. The anchor `(^|[^A-Za-z0-9])` must let this stay clean.
    kebab = write(tmp, "kebab.txt",
                  "task-runner-for-this-project\n"
                  "ask-your-teammate-about-this-config-value\n"
                  "please-desk-check-the-risk-assessment-document\n")
    r = fire(kebab)
    check("ordinary kebab-case text (task-/ask-/desk-/risk-...) is NOT a false "
          "positive after anchoring the sk- branch",
          r.returncode == 0 and "clean" in r.stdout, f"rc={r.returncode} {r.stdout!r}")

    return clean, anthropic_key


def run_positive_control_red_proof():
    """The script's OWN positive controls must actually discriminate: if the secret
    pattern is broken, the script must refuse to run at all (exit 2), never silently
    report every file clean. Proven by mutating SECRET_PATTERN to a pattern that
    cannot match any of its own control values."""
    with open(GUARD, encoding="utf-8") as f:
        source = f.read()
    anchor = ("SECRET_PATTERN='credential_pin|-----BEGIN|AKIA[0-9A-Z]{16}|"
             "(^|[^A-Za-z0-9])sk-ant-|(^|[^A-Za-z0-9])sk-[A-Za-z0-9-]{16,}|"
             "(ghp|gho|github_pat|xox[abp])[-_][A-Za-z0-9]{8}'")
    if anchor not in source:
        check("positive-control-red", False,
              "INCONCLUSIVE: SECRET_PATTERN anchor not found by its source text")
        return
    broken = source.replace(
        anchor, "SECRET_PATTERN='this-pattern-matches-nothing-real-xyz123'", 1)
    if broken == source:
        check("positive-control-red", False, "INCONCLUSIVE: mutant is byte-identical")
        return
    mutant = os.path.join(HERE, ".check-fixture-secrets-mutant-%d.sh" % os.getpid())
    try:
        with open(mutant, "w", encoding="utf-8") as f:
            f.write(broken)
        os.chmod(mutant, os.stat(GUARD).st_mode)
        tmp = tempfile.mkdtemp(prefix="check-fixture-secrets-redcontrol-")
        clean = write(tmp, "clean.jsonl", '{"event": "tool_call"}\n')
        r = fire(clean, guard=mutant)
        check("positive-control-red: a broken secret pattern refuses to run at all "
              "(exit 2), rather than silently reporting every file clean",
              r.returncode == 2 and "POSITIVE CONTROL FAILED" in r.stderr,
              f"rc={r.returncode} {r.stderr!r}")
    finally:
        try:
            os.unlink(mutant)
        except OSError:
            pass


def run_sk_ant_red_proof():
    """RED-proof of the actual #981 fix: revert SECRET_PATTERN's sk- branches to the
    ORIGINAL broken shape (`sk[-_][A-Za-z0-9]{8}`, no hyphens allowed, unanchored)
    and confirm the exact Anthropic key from the real case above is silently
    accepted as clean — proving this suite's first case would have caught the
    historical defect, and that the fix (not merely the test) is what closes it."""
    with open(GUARD, encoding="utf-8") as f:
        source = f.read()
    fixed = "(^|[^A-Za-z0-9])sk-ant-|(^|[^A-Za-z0-9])sk-[A-Za-z0-9-]{16,}"
    original_broken = "(sk|ghp|gho|github_pat|xox[abp])[-_][A-Za-z0-9]{8}"
    if fixed not in source:
        check("sk-ant-red", False,
              "INCONCLUSIVE: the fixed sk- pattern anchor was not found")
        return
    reverted = source.replace(
        fixed + "|(ghp|gho|github_pat|xox[abp])[-_][A-Za-z0-9]{8}",
        original_broken, 1)
    # The mutant's OWN positive controls for the two sk- branches must still pass —
    # their purpose here is to prove the FILE check silently passes, not to trip the
    # (still-correct, and already separately proven) positive-control safeguard.
    reverted = reverted.replace(
        '"sk-ant-api03-THIS-IS-A-SYNTHETIC-CONTROL-VALUE-NOT-A-REAL-KEY"',
        '"sk-AbCdEfGh12345678synthetic1"', 1)
    reverted = reverted.replace(
        '"sk-proj-AbCdEfGh-1234-5678-XyZ9"',
        '"sk-AbCdEfGh12345678synthetic2"', 1)
    if reverted == source:
        check("sk-ant-red", False, "INCONCLUSIVE: mutant is byte-identical")
        return
    mutant = os.path.join(HERE, ".check-fixture-secrets-skant-mutant-%d.sh" % os.getpid())
    try:
        with open(mutant, "w", encoding="utf-8") as f:
            f.write(reverted)
        os.chmod(mutant, os.stat(GUARD).st_mode)
        tmp = tempfile.mkdtemp(prefix="check-fixture-secrets-skantred-")
        anthropic_key = write(tmp, "anthropic.jsonl",
                              '{"key": "sk-ant-api03-AbCdEfGh12345678-XyZ99900112233"}\n')
        real = fire(anthropic_key)
        muted = fire(anthropic_key, guard=mutant)
        ok = (real.returncode == 1 and muted.returncode == 0
              and "Traceback" not in muted.stderr)
        check("sk-ant-red: the original broken pattern silently passes the exact "
              "key that shipped invisibly before #981's fix",
              ok, f"real={real.returncode} mutant={muted.returncode}: {muted.stdout!r}")
    finally:
        try:
            os.unlink(mutant)
        except OSError:
            pass

def main():
    run_cases()
    run_positive_control_red_proof()
    run_sk_ant_red_proof()
    fails = 0
    for name, ok, detail in RESULTS:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n        {detail}")
    print(f"\n{len(RESULTS) - fails}/{len(RESULTS)} cases passed.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
