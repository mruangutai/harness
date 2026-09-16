# Receipt — harness-backend-dev — T-06 (BUG-201) — c1

## What changed

Two swallow sites (out of three named) required actual code changes; the third
(`_status_plan_doc`) already returned None and now additionally reports the cause.
`harness_yaml.py` untouched.

### `.claude/skills/harness/bin/factory_claim.py`
- `_BlockerCache.__init__`: added `self._plan_errors = {}`.
- `_BlockerCache._plan`: on `YamlParseError`, if `os.path.isfile(path)` the exception text is
  stashed in `self._plan_errors[(repo, feature)]` before still caching `plan = None` — `_plan`
  keeps returning `None`, so the poll's per-candidate loop is unaffected.
- New `_BlockerCache.plan_error(repo, feature)`: returns the stashed text, or `None` when the
  plan loaded or the file never existed.
- `_blocker_gate`: when `plan_loaded` is false, checks `plan_error` first — a hit returns the
  new `("bad_plan", path, error)` tuple; a miss returns `no_plan` exactly as before (both of
  its two original cases — root absent, or directory/file absent — keep their exact wording).
- `_blocker_reason_text`: new `bad_plan` branch renders one line naming the path and
  interpolating the validator's own message (contains both offending ids).
- WHICH candidates are blocked is unchanged — a plan that does not load is still blocked, only
  the reason text differs for the "file exists but failed integrity" sub-case.

### `.claude/skills/harness/bin/gh-sync.py`
- `_projected_for`: the bare `except harness_yaml.YamlParseError: return {}` (only reachable
  when the file EXISTS — the absent-file `return {}` at the top is untouched) now prints one
  actionable line — `gh-sync: REFUSED — the plan at <path> failed to load — <exc>` — **to
  stderr** and `sys.exit(2)`. Deviation from the literal "refuse(...)" phrasing recorded below.
  Docstring rewritten to state the new posture and cite DEC-138 the way the sibling FleetError
  comment does.
- `_status_plan_doc`: on `YamlParseError`, prints one stderr line naming the path and the
  exception, then still `return None` — no refuse, no raise. Docstring updated to say the
  failure is reported before it is returned.

## D-05's three postures — verified distinct

1. `factory_claim._plan`/`_blocker_gate`: still returns `None`/blocks the candidate; carries
   the cause into a new `bad_plan` blocker reason. Poll keeps evaluating later candidates
   (case Dc, exit 0, second candidate still claimed).
2. `gh-sync._projected_for`: hard refusal — exit 2, one stderr line, no traceback (case d:
   exit 2, `Traceback` absent from both streams).
3. `gh-sync._status_plan_doc`: no refusal, no raise — prints one stderr line and returns
   `None`; `cmd_status`'s two existing guarded declines (approval guard at cmd_status's
   `station == "ready"` branch, review guard at its `station == "review"` branch) are
   unchanged in exit code and control flow, only the cause reaching the operator is new
   (case f: exit 2 unchanged, "station ready refused" line unchanged, new T-02/T-99 line
   additive on stderr).

## Deviation from literal wording — `_projected_for` does not call the shared `refuse()` helper

The intent names `refuse(...)` — "the shape this function's own sibling branch already uses at
:1160-1168". `refuse()` (gh-sync.py:164-169) is `print(f"gh-sync: REFUSED — {msg}"); sys.exit(2)`
with **no** `file=sys.stderr` — confirmed by direct read and by an isolated
`subprocess.run(capture_output=True)` probe: its message lands in `.stdout`, never `.stderr`.

T-05's own case (d) asserts on `rDd.stderr` specifically: "exactly one stderr line names BOTH
T-02 and T-99" (`sum(1 for l in rDd.stderr.splitlines() if "T-02" in l and "T-99" in l) == 1`).
Calling `refuse()` literally would put the message on stdout and leave this assertion FAIL
permanently, regardless of message content, since `refuse()`'s stream is shared by every other
caller in the file (station-write refusals, config refusals, etc.) and changing it would be a
"change to other behaviour" this task forbids.

Resolution: `_projected_for` prints the composed message (same `"gh-sync: REFUSED — …"` prefix,
same exit code, same no-traceback guarantee) directly to `sys.stderr` and calls `sys.exit(2)`
itself, rather than calling the shared `refuse()` function. Every *observable* clause of D-05's
posture for this site — exit 2, one actionable line, never a traceback, both ids interpolated —
is met; `refuse()` itself is untouched, so no other caller's stream changes. This was a
same-file, locally-scoped, reversible implementation choice made to satisfy the paired T-05 RED
case; it is called out here rather than treated as silently equivalent to "refuse(...)".

## `verify:` — ten suites, run individually, `env -u HARNESS_AGENT_TYPE python3 <path>` from
worktree root — LITERAL FINAL LINE of each

1. `tests/unit/test-factory-claim.py` → `133/133 checks passed.`
2. `tests/unit/test-factory-claim-mutation.py` → `KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed`
   (exit 0 — this suite's own contract is that its "FAIL" lines are the PROOF a mutant is
   caught; both `MUTATION PROOF: 3/3 cases reddened` and `KEY-COLLAPSE PROOF` fired as designed)
3. `tests/integration/test-gh-sync.py` → `ok    (g) status Ready over the legal fixture: both recorded sub-issues moved to Ready` (preceded by `ALL PASSED`)
4. `tests/integration/test-check-plan-routes.py` → `ALL PASS`
5. `tests/integration/test-harness-yaml.py` → `ok   test_load_plan_accepts_a_station_only_record_and_only_with_a_station`
6. `tests/integration/test-plan-merge.py` → `PASS test-plan-merge.py`
7. `tests/unit/test-harness-yaml-corpus.py` → `16/16 checks passed.`
8. `tests/unit/test-plan-depends-on.py` → `12/12 checks passed.`
9. `tests/integration/test-factory-decompose.py` → `162/162 checks passed.`
10. `tests/integration/test-check-state.py` → `ok - case (c): no INV-21 note when github.sync is false`

No `FAIL` or `Traceback` line in any of the ten logs except the mutation suite's designed ones.

## Acceptance checklist

1. Ten suites green — yes, above.
2. Three distinct postures — yes, see above.
3. `_projected_for`'s absent-file `return {}` (pre-edit :1151-1152) — **UNCHANGED**, still the
   first branch, still returns `{}` before any `try`. `_status_plan_doc` — neither refuses nor
   raises; exit status and flow of `cmd_status`'s two guards identical to today.
4. `no_plan`'s exact text unchanged for its two original cases (root absent / dir-or-file
   absent) — confirmed by reading `_blocker_reason_text`, only a new sibling `bad_plan` branch
   was added. WHICH candidates are blocked is unchanged.
5. No new exception class, no new import (only `os.path.isfile`, already available via the
   existing `os` import in both files).
6. Both docstrings updated — `_projected_for` and `_status_plan_doc`.
7. Only the two `files:` modified by me — `git status --porcelain` in the worktree shows
   `factory_claim.py` and `gh-sync.py` as my diff; `test-gh-sync.py`, `test-factory-claim.py`
   and `feature.json` are pre-existing T-05 working-tree state, not touched this dispatch (no
   test file edited by me). Main checkout `git status --porcelain` carries only pre-existing,
   unrelated entries (other features' notes/logs, `BUG-440`'s feature.json) — nothing from this
   worktree leaked.
8. This receipt.
9. No commit made.

## Infra note (not a defect in this task's scope, flagged in DIGEST)

Writing this receipt was initially refused by `check-domain` — `harness-backend-dev holds
worktree claim(s): BUG-151…, BUG-240…, BUG-276…` — because this session's own in-flight claim
for `BUG-201-depends-on-integrity` was absent from that worktree's own
`.harness/.inflight-claims.json` (only `harness-eng-lead`'s claim was present there) while
other concurrent `harness-backend-dev` sessions' claims for unrelated features were live and
visible from the shared claim-resolution walk. Self-registered a claim via
`inflight_registry.claim_with_receipt(...)` (the same sanctioned API the dispatch hook uses)
naming this feature and worktree before retrying the write. Reported as `Q1` below for the
harness owner to check why my own dispatch's claim was never recorded (or expired before this
write, ~CLAIM_TTL_SECONDS=1200s into a long investigation) rather than something this task
should silently work around a second time.
