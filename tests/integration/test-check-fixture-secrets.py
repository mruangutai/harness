#!/usr/bin/env python3
"""Tests for check-fixture-secrets.py (issue #981).

FEAT-44's T-01 ran an inline scrub sweep, once, in a task's verify: block, with two
blind spots that shipped invisibly: the secret pattern could not match an Anthropic
API key (`sk-ant-api03-...` breaks the old `[A-Za-z0-9]{8}` requirement at the first
hyphen), and the identity check bound `$(whoami)` — the invoker, not the capturer —
so it passed vacuously in CI. This suite pins both fixes with the exact credential
shape that escaped before, proves the positive controls actually discriminate, and
RED-proofs the sk- fix against the original broken pattern.

    ./test-check-fixture-secrets.py     -> exit 0 all pass, 1 otherwise
"""
from integration_support import BIN  # noqa: E402 -- first import, puts tests/ on sys.path
import os
import subprocess
import sys
import tempfile

from check_support import Checks

GUARD = os.environ.get("CHECK_FIXTURE_SECRETS_BIN") or str(BIN / "check-fixture-secrets.py")

C = Checks()
check = C.check


def write(tmp, name, content):
    path = os.path.join(tmp, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def fire(*paths, guard=GUARD):
    return subprocess.run([guard, *paths], capture_output=True, text=True)


def check_blocked(tmp, label, name, content, needle, detail_stderr=True):
    """Write one dirty file, fire the guard on it alone, and check it exits 1 naming needle."""
    path = write(tmp, name, content)
    r = fire(path)
    detail = f"rc={r.returncode} {r.stderr!r}" if detail_stderr else f"rc={r.returncode}"
    check(label, r.returncode == 1 and needle in r.stderr, detail)
    return path


def check_clean(tmp, label, name, content):
    r = fire(write(tmp, name, content))
    check(label, r.returncode == 0 and "clean" in r.stdout, f"rc={r.returncode} {r.stdout!r}")
    return r


def run_dirty_cases(tmp):
    # ---- THE ACTUAL DEFECT (#981, blind spot 1): a real Anthropic key shape. The
    # original sweep's `sk[-_][A-Za-z0-9]{8}` breaks at the hyphen three characters
    # into "ant" and never matches this.
    anthropic_key = check_blocked(
        tmp, "an sk-ant- key is caught — the exact shape that escaped before", "anthropic.jsonl",
        '{"event": "auth", "key": "sk-ant-api03-AbCdEfGh12345678-XyZ99900112233"}\n', "BLOCKED")

    # ---- A hyphenated sk-proj- key, the other shape item 1 names.
    check_blocked(tmp, "an sk-proj- key (hyphenated, non-Anthropic) is also caught", "proj.jsonl",
                  '{"key": "sk-proj-AbCdEfGh-1234-5678-XyZ9"}\n', "BLOCKED")
    return anthropic_key


def run_regression_cases(tmp):
    # ---- REGRESSION: pre-existing coverage (GitHub PAT, AWS key, PEM header) is
    # unchanged by the sk- fix.
    for label, content in (
        ("a github_pat token", 'token=github_pat_11ABCDEFG01234567\n'),
        ("a ghp token", 'GH_TOKEN=ghp_ABCDEFGH12345678\n'),
        ("an AWS access key id", 'AKIA' + 'A' * 16 + '\n'),
        ("a PEM private key header", '-----BEGIN PRIVATE KEY-----\n'),
        ("a credential_pin literal", 'credential_pin=xyz\n'),
    ):
        check_blocked(tmp, f"regression: {label} is still caught",
                      "regress-" + label.replace(" ", "-") + ".txt", content, "BLOCKED",
                      detail_stderr=False)


def run_home_path_cases(tmp):
    # ---- THE ACTUAL DEFECT (#981, blind spot 2): a baked-in home-directory path,
    # matched regardless of who is RUNNING this check. `whoami` on the machine
    # running this test is never literally "alice" or "bob-dev-laptop", so a
    # $(whoami)-bound check would pass this vacuously; the home-directory-shape
    # check must not.
    leaked_path = check_blocked(
        tmp, "a baked-in /Users/<name>/ path is caught, independent of $(whoami)", "leak.jsonl",
        '{"cwd": "/Users/alice-not-the-invoker/project/repo"}\n', "home-directory")
    check_blocked(tmp, "a baked-in /home/<name>/ path is caught too", "leak-home.jsonl",
                  '{"path": "/home/bob-dev-laptop/.config/x"}\n', "home-directory",
                  detail_stderr=False)
    return leaked_path


def run_misuse_cases(tmp, clean, anthropic_key, leaked_path):
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


def run_cases():
    with tempfile.TemporaryDirectory(prefix="check-fixture-secrets-") as tmp:
        anthropic_key = run_dirty_cases(tmp)

        # ---- NEGATIVE CONTROL: a clean file passes.
        clean = os.path.join(tmp, "clean.jsonl")
        check_clean(tmp, "a genuinely clean file passes, exit 0", "clean.jsonl",
                    '{"event": "tool_call", "name": "Read"}\n')

        run_regression_cases(tmp)
        leaked_path = run_home_path_cases(tmp)
        run_misuse_cases(tmp, clean, anthropic_key, leaked_path)

        # ---- FALSE-POSITIVE REGRESSION (code review of PR #1189): the unanchored
        # sk-[A-Za-z0-9-]{16,} branch matched ordinary kebab-case text — "task-runner-
        # for-this-project", "ask-your-teammate-about-this-config" — any word ending
        # `-sk` followed by 16+ more hyphen/alnum characters, which saturates a
        # captured transcript. The anchor `(^|[^A-Za-z0-9])` must let this stay clean.
        check_clean(tmp, "ordinary kebab-case text (task-/ask-/desk-/risk-...) is NOT a false "
                    "positive after anchoring the sk- branch", "kebab.txt",
                    "task-runner-for-this-project\n"
                    "ask-your-teammate-about-this-config-value\n"
                    "please-desk-check-the-risk-assessment-document\n")


def read_guard():
    with open(GUARD, encoding="utf-8") as f:
        return f.read()


def fire_mutant(mutant_text, input_name, content, real_too=False):
    """Run mutant_text as the guard (stdlib only, so a plain temp dir hosts it) on one input
    file. Returns the mutant's result, or (real, mutant) when real_too also fires GUARD."""
    with tempfile.TemporaryDirectory(prefix="check-fixture-secrets-mutant-") as d:
        mutant = os.path.join(d, "check-fixture-secrets-mutant.py")
        with open(mutant, "w", encoding="utf-8") as f:
            f.write(mutant_text)
        os.chmod(mutant, os.stat(GUARD).st_mode)
        path = write(d, input_name, content)
        muted = fire(path, guard=mutant)
        return (fire(path), muted) if real_too else muted


def run_positive_control_red_proof():
    """The script's OWN positive controls must actually discriminate: if the secret
    pattern is broken, the script must refuse to run at all (exit 2), never silently
    report every file clean. Proven by mutating SECRET_PATTERN to a pattern that
    cannot match any of its own control values."""
    source = read_guard()
    anchor = ("SECRET_PATTERN_TEXT = r'credential_pin|-----BEGIN|AKIA[0-9A-Z]{16}|"
              "(^|[^A-Za-z0-9])sk-ant-|(^|[^A-Za-z0-9])sk-[A-Za-z0-9-]{16,}|"
              "(ghp|gho|github_pat|xox[abp])[-_][A-Za-z0-9]{8}'")
    if anchor not in source:
        check("positive-control-red", False,
              "INCONCLUSIVE: SECRET_PATTERN anchor not found by its source text")
        return
    broken = source.replace(
        anchor, "SECRET_PATTERN_TEXT = r'this-pattern-matches-nothing-real-xyz123'", 1)
    r = fire_mutant(broken, "clean.jsonl", '{"event": "tool_call"}\n')
    check("positive-control-red: a broken secret pattern refuses to run at all "
          "(exit 2), rather than silently reporting every file clean",
          r.returncode == 2 and "POSITIVE CONTROL FAILED" in r.stderr,
          f"rc={r.returncode} {r.stderr!r}")


def _sk_ant_mutant(source):
    fixed = "(^|[^A-Za-z0-9])sk-ant-|(^|[^A-Za-z0-9])sk-[A-Za-z0-9-]{16,}"
    if fixed not in source:
        return None
    original_broken = "(sk|ghp|gho|github_pat|xox[abp])[-_][A-Za-z0-9]{8}"
    reverted = source.replace(
        fixed + "|(ghp|gho|github_pat|xox[abp])[-_][A-Za-z0-9]{8}",
        original_broken, 1)
    controls = [
        ('"sk-ant-api03-THIS-IS-A-SYNTHETIC-CONTROL-VALUE-NOT-A-REAL-KEY"',
         '"sk-AbCdEfGh12345678synthetic1"'),
        ('"sk-proj-AbCdEfGh-1234-5678-XyZ9"',
         '"sk-AbCdEfGh12345678synthetic2"'),
    ]
    for fixed_control, broken_control in controls:
        reverted = reverted.replace(fixed_control, broken_control, 1)
    return reverted


def run_sk_ant_red_proof():
    """Prove the original #981 sk-ant pattern silently accepted the reported key."""
    source = read_guard()
    reverted = _sk_ant_mutant(source)
    if reverted is None or reverted == source:
        check("sk-ant-red", False, "INCONCLUSIVE: mutant could not be constructed")
        return
    real, muted = fire_mutant(reverted, "anthropic.jsonl",
                              '{"key": "sk-ant-api03-AbCdEfGh12345678-XyZ99900112233"}\n',
                              real_too=True)
    ok = real.returncode == 1 and muted.returncode == 0 and "Traceback" not in muted.stderr
    check("sk-ant-red: the original broken pattern silently passes the exact "
          "key that shipped invisibly before #981's fix",
          ok, f"real={real.returncode} mutant={muted.returncode}: {muted.stdout!r}")


def main():
    run_cases()
    run_positive_control_red_proof()
    run_sk_ant_red_proof()
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
