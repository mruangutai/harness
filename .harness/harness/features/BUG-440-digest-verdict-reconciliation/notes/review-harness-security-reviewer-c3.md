# Security Review — BUG-440 — Cycle 3 (final, pin `442e0d24`)

## BLUF
PASS, `severity_max: none`. The c2→c3 delta is a pure test-refactor confined to
`tests/integration/test-check-state.py`; `check-state.sh` is byte-identical to the c2 pin
(verified by hash, not assumed). No new write path, no new subprocess/shell surface, no change
to the INV-37 message content or its data-exposure profile. V-04/V-05/V-07/V-08 carry forward
unchanged at their existing severities (all `check-state.sh`-anchored, and that file didn't move).
V-02/V-03 bindings — single-run blocking fixture, run X's `"VERDICT: FAIL\n"` digest text — are
still bound verbatim in the restructured code.

## Measured census
`git diff a1a6795..442e0d2 --stat`: **1 file**, `tests/integration/test-check-state.py`
(+41/-22). No other path touched — confirmed by `--stat`, not inferred.

`check-state.sh` byte-identity check (not assumed, per dispatch requirement): sha256 of
`git show a1a6795:.claude/skills/harness/bin/check-state.sh` and
`git show 442e0d2:.claude/skills/harness/bin/check-state.sh` are both
`c25e85ed61c1448bde8668272c1081b58f21470e6efdae7423a2992313d3c455` — identical. `git diff
a1a6795..442e0d2 -- <that path>` returns 0 lines. Cycle-1/2 clearances for check-state.sh
(REQ-01..04, D-07, PF-b884d6ee, SC-07, and V-04/V-05/V-06/V-07/V-08) carry forward by name per
the contract.

## What the diff actually does
Splits the monolithic `case_bug440_digest_verdict_reconciliation()` into four helpers —
`_bug440_validator()`, `_bug440_mixed_case`, `_bug440_blocking_case`, `_bug440_clean_case` — each
taking the already-loaded `validator` module. The fixture-building primitives it calls
(`_bug440_digest`, `_bug440_build`, `_bug440_validate_fixture`, lines 4618–4661) are **outside**
the diff hunk (`@@ -4663,15 +4663,18 @@` starts after them) and are untouched.

- **Write surface (REQ-04 concern):** unchanged. Every fixture write still routes through
  `_bug440_build` → `os.path.join(fdir, "runs", name)` rooted at `tempfile.TemporaryDirectory()`
  via `_bug1305_invariant_scaffold(tmp)`. `entries`/`name` values are fixed test literals
  (`"M"`,`"E"`,`"N"`,`"I"`,`"G"`,`"X"`,`"O"`), never attacker- or input-derived — no traversal
  vector. Confirmed live: ran `case_bug440_digest_verdict_reconciliation()` directly — exits
  `ok`/`True`, and the pre-existing before/after sha256 hash-equality assertion (`unchanged`)
  still holds, i.e. the check-under-test still writes nothing to the fixture tree.
- **INV-37 message / data exposure:** the new code only changes *how the test asserts on*
  `check-state.sh`'s stdout (`re.findall(r"^.*INV-37.*$", out, re.M)` + `out.count(...)` in place
  of list comprehensions) — the message itself is produced by the unchanged binary. Same tokens
  are asserted (`FEAT-TEST`, `M`, `FAIL`, `PASS`, `feature.json`, `digest.md`) and the same
  silent-on-other-runs check is present (`silent = ("runs/E", "runs/N", "runs/I", "runs/G",
  "runs/X", "runs/O")`). No new exposure surface; the existing one (V-04, order-blind token
  check) is unmoved and not re-litigated here.
- **V-02/V-03 bindings, still bound:** `_bug440_blocking_case` fixture is still
  `entries=("M",)` with exactly one run — single-cause exit 1. `runs` list in
  `_bug440_mixed_case` still sets X's digest to the literal `"VERDICT: FAIL\n"` (unescaped,
  matchable VERDICT line in an otherwise-invalid digest) — unchanged from c2.
- No new imports beyond stdlib `re` (test file already imported `hashlib`, `tempfile`, `os`).
  No new subprocess/shell invocation, no credentials, no new dependency.

## Threat model
Nothing in this diff crosses a trust boundary: it is test code exercising an already-audited,
byte-identical script, with fixture I/O confined to a per-call `TemporaryDirectory`. No STRIDE
category applies beyond what was already assessed against `check-state.sh` in cycles 1–2.

```yaml
VERDICT: PASS
DIGEST:
  headline: "c2→c3 delta is test-only complexity refactor; check-state.sh byte-identical (sha256 match); no new write path, injection, or data-exposure surface"
  in_scope: true
  scope_reason: "Dispatch specifically asked whether the restructured fixtures could escape tempfile.TemporaryDirectory or introduce a write path, and whether INV-37 message content changed exposure — examined both, found nothing"
  severity_max: none
  findings: 0
  must_fix: []
  threat_model:
    - { boundary: "test fixture write path (tempfile.TemporaryDirectory -> runs/<name>/{state.yaml,digest.md})", stride: T, mitigated: true }
    - { boundary: "check-state.sh stdout -> INV-37 assertion (unchanged binary, unchanged message shape)", stride: I, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-440-digest-verdict-reconciliation/.harness/harness/features/BUG-440-digest-verdict-reconciliation/notes/review-harness-security-reviewer-c3.md
```
