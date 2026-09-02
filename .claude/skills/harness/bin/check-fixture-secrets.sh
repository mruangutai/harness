#!/usr/bin/env bash
# Scrub check for a captured artifact (an OMP session transcript, a fixture, any file
# staged FROM a real capture) before it is committed. Issue #981.
#
# FEAT-44's T-01 ran this sweep inline, once, in a task's verify: block. Two defects
# shipped invisibly because nothing forced the pattern to prove itself:
#
#   1. THE SECRET PATTERN COULD NOT MATCH AN ANTHROPIC API KEY. The original was
#      `(sk|ghp|gho|github_pat|xox[abp])[-_][A-Za-z0-9]{8}` — `sk-ant-api03-...`
#      breaks the `[A-Za-z0-9]{8}` requirement at the hyphen after `ant`, three
#      characters in. In a corpus captured from an agent running Anthropic models,
#      that is the single most probable credential shape to encounter, and the sweep
#      that exists specifically to catch it could not.
#   2. THE IDENTITY CHECK BOUND THE INVOKER, NOT THE CAPTURER. `grep -qF "$(whoami)"`
#      passes vacuously in CI (the runner's own user, never present) and is strongest
#      exactly where it is least needed — a developer running the check by hand on the
#      SAME machine the capture was taken, where a leaked path already reads back the
#      committer's own name and the check is redundant with a human's own eyes.
#
# THE SCRUB IS DESCRIBED AS THE ONE IRREVERSIBLE STEP (FEAT-44's own plan wording): a
# pushed blob cannot be retracted from history. A gate that cannot match the likeliest
# secret, and an identity check that passes vacuously in the environment it usually
# runs in, together give a FALSE SENSE OF COVERAGE — worse than no gate, because it
# substitutes for the manual line-by-line read that is what actually protects anyone.
#
# EVERY ABSENCE CHECK HAS A POSITIVE CONTROL RUN FIRST, on a synthetic string built
# from the same pattern (DEC-169): a `grep` that cannot discriminate — a typo'd regex,
# a flag that silently no-ops — must never read as "clean". Preserved from T-01's
# original verify block, which already got this half right.
#
# Usage: check-fixture-secrets.sh <file> [<file> ...]
#   exit 0   every file is clean of both patterns; both positive controls fired.
#   exit 1   a file matched a forbidden pattern (the leak case).
#   exit 2   a positive control did not fire — the check itself cannot be trusted
#            (misuse, e.g. no files given, or a $0 environment with a broken grep).
set -uo pipefail

# THE SECRET PATTERN. `sk-[A-Za-z0-9-]{16,}` allows hyphenated segments, so
# `sk-ant-api03-...` and `sk-proj-...` both match; `sk-ant-` is named explicitly on
# top of it so even a short, truncated fragment (no 16 characters yet typed) still
# trips the check — belt and suspenders on the credential this project is most likely
# to leak. BOTH sk- branches are ANCHORED with `(^|[^A-Za-z0-9])` (code review of
# #1189): unanchored, `sk-[A-Za-z0-9-]{16,}` false-positives on ordinary kebab-case
# text saturating a captured transcript — "task-runner-for-this-project",
# "ask-your-teammate-about-this" — any word ending `-sk` followed by 16+ more
# hyphen/alnum characters. Real key material is never preceded by another
# alphanumeric character, so the anchor costs nothing on true positives. The
# GitHub/AWS/PEM branches are unchanged from the original sweep; they were never
# the defect.
SECRET_PATTERN='credential_pin|-----BEGIN|AKIA[0-9A-Z]{16}|(^|[^A-Za-z0-9])sk-ant-|(^|[^A-Za-z0-9])sk-[A-Za-z0-9-]{16,}|(ghp|gho|github_pat|xox[abp])[-_][A-Za-z0-9]{8}'

# THE IDENTITY PATTERN. An absolute home-directory shape, not `$(whoami)`: fires
# regardless of who runs the check or which machine the capture was taken on, because
# the leak this exists to catch is a baked-in `/Users/<name>/...` or `/home/<name>/...`
# path from capture time, not the invoker's own account.
HOME_PATH_PATTERN='/Users/[^/[:space:]"'"'"']+/|/home/[^/[:space:]"'"'"']+/'

usage() {
  echo "usage: check-fixture-secrets.sh <file> [<file> ...]" >&2
  exit 2
}

[ "$#" -ge 1 ] || usage

# POSITIVE CONTROLS, run once, before any file is checked. A synthetic string built
# from EVERY alternation branch must be found BY that branch, or the sweep itself is
# broken and every downstream "clean" is unearned. Code review of #1189: the original
# cut self-checked only 2 of 6 branches (sk-ant-, home-path); a broken AKIA/PEM/
# GitHub-token/credential_pin branch would have shipped with no runtime signal, only
# CI's separate test suite. Every branch gets its own control now, checked separately
# so a failure names WHICH branch broke, not just "the pattern".
_control_fail=0
_check_control() {
  # $1: label  $2: pattern  $3: control value  $4: extra guidance
  if ! printf '%s\n' "$3" | grep -qE "$2"; then
    echo "check-fixture-secrets: POSITIVE CONTROL FAILED — the $1 pattern does not" >&2
    echo "  match its own synthetic control value ($3). $4" >&2
    _control_fail=1
  fi
}
_check_control "sk-ant- key" "$SECRET_PATTERN" \
  "sk-ant-api03-THIS-IS-A-SYNTHETIC-CONTROL-VALUE-NOT-A-REAL-KEY" \
  "The sweep cannot be trusted; fix the pattern before checking any file with it."
_check_control "hyphenated sk- key" "$SECRET_PATTERN" \
  "sk-proj-AbCdEfGh-1234-5678-XyZ9" \
  "The sweep cannot be trusted; fix the pattern before checking any file with it."
_check_control "AWS access key id" "$SECRET_PATTERN" \
  "AKIA$(printf 'A%.0s' $(seq 1 16))" \
  "The AWS branch cannot be trusted; fix the pattern before checking any file with it."
_check_control "PEM private key header" "$SECRET_PATTERN" \
  "-----BEGIN PRIVATE KEY-----" \
  "The PEM branch cannot be trusted; fix the pattern before checking any file with it."
_check_control "GitHub token" "$SECRET_PATTERN" \
  "ghp_ABCDEFGH12345678" \
  "The GitHub-token branch cannot be trusted; fix the pattern before checking any file with it."
_check_control "credential_pin literal" "$SECRET_PATTERN" \
  "credential_pin=xyz" \
  "The credential_pin branch cannot be trusted; fix the pattern before checking any file with it."
_check_control "home-directory" "$HOME_PATH_PATTERN" \
  "/Users/example-synthetic-control-user/scratch.txt" \
  "The identity check cannot be trusted; fix the pattern before checking any file with it."
[ "$_control_fail" -eq 0 ] || exit 2

failures=0
for f in "$@"; do
  if [ ! -r "$f" ]; then
    echo "check-fixture-secrets: BLOCKED — $f is not a readable file." >&2
    failures=$((failures + 1))
    continue
  fi
  if grep -qE "$SECRET_PATTERN" "$f"; then
    echo "check-fixture-secrets: BLOCKED — $f matches the secret pattern. Do not" >&2
    echo "  commit it. Re-scrub or regenerate the fixture from a clean capture." >&2
    failures=$((failures + 1))
  fi
  if grep -qE "$HOME_PATH_PATTERN" "$f"; then
    echo "check-fixture-secrets: BLOCKED — $f contains an absolute home-directory" >&2
    echo "  path (/Users/<name>/... or /home/<name>/...). Redact it before committing." >&2
    failures=$((failures + 1))
  fi
done

if [ "$failures" -gt 0 ]; then
  exit 1
fi
echo "check-fixture-secrets: clean — $# file(s) checked, all positive controls fired."
exit 0
