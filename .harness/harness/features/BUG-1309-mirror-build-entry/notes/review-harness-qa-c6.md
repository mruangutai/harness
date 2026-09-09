# QA c6 — gate re-run + pair-binding audit, merge-gate.py @ 894adc0f

## BLUF
Matrix satisfied (unit + integration, both exit 0, non-empty discovered sets). The pairwise
cases added at this pin close all four historically-broken pairs and the panel's real question:
no unattributable record influences an outcome, and no deny names an unfixable target, across
every combination I could construct — including three pairs the 19 shipped cases never bind.
One pre-existing (not new at this pin) wording defect found by hand: the DEC-138 stderr line is
misleading, not decision-wrong, when the local record is HELD during a remote-read failure.

## 1. Matrix re-run
`merge-gate.py`/`merge-gate.sh` is task T-05, `change_type: feature` (plan.yaml:873). Floor from
`.harness/harness.json:191-195` (`feature.always`): `unit`, `integration`.

| kind | cmd | exit | discovered |
|---|---|---|---|
| unit | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | 33 files, all PASS (no FAIL/ERROR lines) |
| integration | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | 50 files, all PASS; `test-merge-gate.py` exit 0, 19/19 `ok`, `ALL PASSED` |

Both runs `env -u HARNESS_AGENT_TYPE`ed per repo Expertise G-07. Non-empty discovered set on both
(not an exit-0-over-nothing false pass). **matrix_ok: true.**

## 2. Pair-binding audit — the main job

Six axes: CMD {git, gh, non-merge} · REMOTE (gh only) {ok, fail-OSError, fail-cmd(nonzero exit)} ·
MATCH {yes, no} · OWNREC (the branch's own would-be record) {healthy dict, non-dict, unparseable
bytes/unreadable, absent} · FOREIGN (an unusable record elsewhere in the tree) {present, absent} ·
RECEIPT (only when MATCH=yes, OWNREC=healthy) {held, owed, era-exempt, repo-unpinned, plan-error}.

**Structural impossibilities** (not gaps — code makes the pair unreachable):
- OWNREC∈{non-dict, unparseable} ⇒ MATCH=no always: `feature_for` (merge-gate.py:100-109) can only
  return a match through `isinstance(document, dict) and document.get("branch") == branch`; a
  non-dict or unopenable record fails that test by construction, so it can never own a branch.
- RECEIPT=repo-unpinned × RECEIPT=held: mutually exclusive by definition (one field).
- RECEIPT=repo-unpinned × era-exempt: the era check (line ~140) returns before `repo_pinned` is
  ever evaluated (line ~152), so era-exempt always wins over an unpinned repo — order-guaranteed,
  confirmed by hand (case E below).
- CMD=non-merge × anything else: `main()`'s `not merge_ref(command)` returns before any record
  logic runs — orthogonal by construction, one case fully covers it (L80-81).

**Case-to-pair bindings** (`tests/integration/test-merge-gate.py`):

| Pair | Bound by (name, line) |
|---|---|
| MATCH=yes,healthy × RECEIPT=owed | L64-65 `recovery-required denies` |
| MATCH=yes,healthy × RECEIPT=held | L70-73 `opened/not-applicable/recovered-terminal allows` |
| MATCH=yes,healthy × RECEIPT=repo-unpinned | L68-69 `unpinned repo absent build_entry denies` |
| MATCH=yes,healthy × RECEIPT=era-exempt(absent) | L90-92 `era-exempt absent build_entry allows` |
| **era-exempt × RECEIPT=owed underlying** (owed-vs-era-exempt) | L93-96 `era-exempt recovery-required allows` — **BOUND** |
| MATCH=yes,healthy × RECEIPT=plan-error(exception) | L122-127 `empty plan fails closed` |
| MATCH=no (branch mismatch, no FOREIGN) | L77-79 `branch matching no feature allows` |
| CMD=gh,REMOTE=ok × MATCH=yes,owed | L82-87 `path-prefixed gh is still detected` |
| CMD=gh,REMOTE=fail-OSError × MATCH=yes,owed (via local-branch fallback) | L97-101 `unresolvable gh falls back and denies` |
| CMD=gh,REMOTE=fail-cmd × MATCH=no × **FOREIGN=present** (unusable-target-vs-no-record) | L102-116 `gh outage with no matching feature allows` — **BOUND** |
| CMD=gh,REMOTE=fail-cmd × MATCH=yes,owed × **FOREIGN=present** (gh-outage-vs-foreign-unusable-record) | L117-121 `gh outage with a feature owing a receipt denies` — **BOUND** |
| MATCH=yes,healthy × RECEIPT=held × **FOREIGN=present** (bystander-vs-healthy) | L128-135 `unrelated non-object feature record does not block healthy merge` — **BOUND** |
| MATCH=no × **FOREIGN=present**, CMD=git (no remote involved) | L136-148 `no-record branch ignores unrelated malformed record` — **BOUND** |

**All four named historically-broken pairs are bound** at this pin: bystander-vs-healthy (L128-135),
unusable-target-vs-no-record (L102-116 and L136-148, two command forms), gh-outage-vs-foreign-unusable-record
(L117-121, and the allow leg at L102-116), owed-vs-era-exempt (L93-96).

### Unbound pairs — named explicitly, then constructed by hand in /tmp (repro not committed)

None of the 19 cases exercises OWNREC∈{non-dict, unparseable-bytes, unreadable} as the branch's
**own** would-be record (only ever as a FOREIGN record, and only the valid-JSON-but-non-dict shape
`[]`). Note the case this pin **replaced** — the old `T-05 unusable target record fails closed`
(deny, sentinel-era behavior, own record `[]`) — was rewritten into `no-record branch ignores
unrelated malformed record`, whose fixture no longer makes the retargeted record `[]`-own-shaped;
the *own-record-is-malformed* pair genuinely dropped out of the suite when the fixture was
repurposed. Also unbound: REMOTE=fail × RECEIPT=held (only REMOTE=fail × RECEIPT=owed is tested).

Constructed by hand against `merge-gate.sh` via `HARNESS_PROJECT_DIR` (same harness the suite
uses), disposable fixtures under `/tmp` (script not committed):

| Constructed pair | Observed | Verdict |
|---|---|---|
| A: OWNREC=unparseable-bytes as the ONLY candidate (own record, no FOREIGN) | rc=0, decision=None, no stderr | **allow, correct** — silently skipped, matches design intent |
| G: OWNREC=`[]` (exact shape the removed pre-fix case used) as the ONLY candidate | rc=0, decision=None, no stderr | **allow, correct** — replays the exact removed case and confirms the fix generalizes past the one now-different fixture |
| B: FOREIGN=unparseable-bytes + MATCH=yes healthy **owed** | rc=0, decision=`deny`, reason names `FEAT-9001-fixture-non-era` (the real, actionable feature) | **deny, correct and actionable** — the JSONDecodeError leg is skipped the same as the isinstance leg |
| C: FOREIGN=unreadable (chmod 000, OSError leg) + MATCH=yes healthy **held** | rc=0, decision=None, no stderr | **allow, correct** — the OSError leg of `except (OSError, json.JSONDecodeError)` is also inert |
| D: CMD=gh, REMOTE=fail-OSError (`/nonexistent/gh`) + MATCH=yes healthy **held** (`opened`) | rc=0, decision=None; **stderr says "the local branch feature/test owes no build-entry receipt"** | allow decision correct; **stderr text is wrong** — a receipt exists (held), it is not owed |
| F: CMD=gh, REMOTE=fail-cmd (exit 9) + MATCH=yes healthy **held** (`not-applicable`) | rc=0, decision=None; same misleading stderr | same wording defect |
| E: era-exempt feature + `repo=None` (repo-unpinned) + RECEIPT=owed underlying | rc=0, decision=None, stderr says "predates the build-entry receipt" (era message only) | **allow, correct** — confirms era-exempt check precedes and preempts the repo-unpinned deny, exactly as the code's line order requires |

**Verdict on the unbound set:** every constructed combination decides correctly (no unattributable
record ever influences an outcome; no deny ever fires without a real, named, actionable feature).
The one real finding is D/F's stderr wording, not a gating defect.

### Novelty check (894adc0f^)
Confirmed at the parent commit: the identical duplicated stderr string ("...owes no build-entry
receipt...") appears twice in `merge-gate.py` at parent HEAD too (`git show 894adc0f^:...|grep`,
two hits). **This wording defect predates this pin — not introduced by the decision-table
rewrite.** Also confirmed: the parent's `feature_for` still returns a third `unusable` sentinel
value (cycle 5's finding); that return shape is gone at this pin — the rewrite is real and is what
the new/changed cases (L102-116's added FOREIGN record, and the fixture rewrite at L136-148)
exist to pin.

## 3. Could-not-fail judgment on the new/changed cases
Diffing `894adc0f^` → `894adc0f` on the test file, exactly two regions changed:
- L102-116 (`gh outage with no matching feature allows`): a FOREIGN `[]` record was added to an
  existing case. Mutation: revert `feature_for` to the parent's sentinel-returning shape (add back
  `unusable=True` on non-dict). The case's own assertion (`d is None and "could not verify" in
  r.stderr`) does NOT redden under that mutation by itself in this exact case, because MATCH is
  already `no` via REMOTE=fail-cmd and the sentinel would only change the *reason* text when
  `document is None` — worth flagging: **this case's assertion does not by itself discriminate
  the sentinel regression**; L136-148 is what carries that weight (see below). Live in this
  fixture: the FOREIGN record's presence, not its effect on this case's own assertion.
- L136-148 (`no-record branch ignores unrelated malformed record`, replacing `unusable target
  record fails closed`): mutation = revert `feature_for` to the sentinel shape. Under that
  mutation the parent behavior denies with `"malformed feature record"` in the reason; the new
  assertion `r.returncode == 0 and d is None` reddens immediately (`d` becomes `"deny"`). **This
  mutant is live and this case is the one that actually pins the cycle-5 fix** — confirmed by the
  fact that this exact case, unmodified, is what the parent commit's code fails (I did not need to
  hand-mutate; the parent's own committed code IS the mutant, and case G above independently
  reproduces the same discrimination against the *old* fixture shape).

## Coverage gaps (Phase 1 vs Phase 2 delta)
- OWNREC=unparseable/unreadable as the branch's own record: never suite-covered (only hand-verified). Recommend a case using the removed pre-fix fixture shape (own record `[]` or invalid bytes) so the suite itself pins this, not just this note.
- REMOTE=fail × RECEIPT=held: never suite-covered; hand-verified correct but surfaced the stderr wording defect below.

## Findings
- **F1 (low, pre-existing, not new at this pin):** `merge-gate.py`'s two `if failure: print(...)`
  call sites (the `document is None` branch and the `entry in {held-states}` branch) share one
  f-string that always says "...owes no build-entry receipt". In the held-record branch this is
  false — a receipt exists, it just isn't owed. No decision is wrong (still correctly allows), so
  this is a diagnostics-accuracy finding, not a gating defect. Confirmed present at `894adc0f^`
  too, so it is carried, not introduced, by this cycle's rewrite — flagging per the correction in
  the record (cycle 5 precedent).
- **F2 (info):** the `gh outage with no matching feature allows` case's own assertion does not
  discriminate a reintroduction of the cycle-5 sentinel by itself (see §3); the discrimination for
  that regression class lives entirely in the adjacent case at L136-148. Not a gap in outcome
  coverage — both pairs are bound — but worth the next reader knowing which case actually carries
  the weight if either is touched in isolation.

## SC evidence
This cycle is gate-only / audit; no SC text was assigned to me to bind. matrix + pair-audit are
the deliverable per dispatch.
