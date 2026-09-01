# Security review c1 — BUG-1071 era guard remedies — review_sha 6b65ecc (base 75daa3bb)

## BLUF

F1 and F2 close exactly what cycle 0 named — verified, not accepted on faith. But F2's remedy
(moving the era boundary from a literal into `.harness/harness.json`) introduces a **new,
unmitigated privilege escalation**: `harness-dev-ops` holds a pre-existing, legitimate
(`upsert: true`) write grant on `.harness/harness.json` (`team-config.yaml:210`) yet holds **no**
authority over `plan.yaml`'s `approval:`/`panel:` fragments (those are main-session-exclusive,
DEC-120, enforced by `approval_guard` — `check-domain.sh:537`). This diff makes
`panel_era_start` — a field dev-ops can write through the normal, sanctioned `Write` tool path
with **zero domain violation, zero bypass, exit 0** — the sole gate on whether *every* approved
plan in the tree needs a panel record at all. One future date (`"2099-12-31"`, or even a
calendar-impossible-but-regex-legal `"9999-99-99"`, since the comparison is bare lexicographic
string comparison with no calendar validity check) silently and permanently exempts the entire
tree from INV-32 grading. **Rated HIGH, not the MED cycle 0 gave the analogous
`approval.date` gap** — because cycle 0's own dispensation (P-02: an actor who already controls
a value already holds the privilege it grants) explicitly does not transfer: dev-ops does not
already hold panel/approval authority by any other route, so this is new capability, not a
cheaper route to an old one.

**[SUPERSEDED BY RE-ADJUDICATION BELOW — the "dev-ops does not already hold... by any other
route" premise is false. See `## Re-adjudication (loop-back)`. Final severity: MED, `must_fix: []`,
`VERDICT: PASS`.]**

## What I re-ran vs adopted

**Re-ran, not trusted:** `check-state.sh` (exit 0, 0 VIOLATION, 32 INV-32 notes, all 32 "pre-era",
0 undated — matches author's claim exactly); `test-check-state.py` (155 ok / 0 FAIL, exit 0);
full `run-unit-tests.sh` all kinds (grepped the complete output for `FAIL <script>` — none exist,
only descriptive test-name text containing the word "FAILS"/"FAILED"; exit 0); the FEAT-40
backfill date, independently, via `git log --all -S'status: approved'` and `git show --stat` on
`2938a5c` — confirmed author date **2026-08-25**, and confirmed via diff that this commit is the
one that flipped `status: pending` → `status: approved` (the actual signature event), with no
later commit touching that line. The backfill is correct.

**Adopted from cycle 0, re-verified only where the diff changed the answer:** P-02 reasoning on
`approval.date` backdating — still valid, unchanged (see below); the mutant-file convention and
`INV32_ERA_START`-in-loop questions — moot, both resolved by this diff's hoist.

## F1 remedy — closes the accidental-omission gap; no new fail-closed hazard

The undated/malformed branch (`check-state.sh:265-276`) is now `bad.append(...)` + `continue`,
unconditionally — reached whether or not `_era_start` is `None`, correctly (comment at :271 says
so, and I verified: `case_inv32_undated_approval_is_violation` passes, and the live tree carries
**0** undated notes post-backfill). No plan can still reach `panel:` grading via an omitted date;
no plan can silently escape via that path either — both were the same fail-open, now closed. The
backdating attack cycle 0 named is **unchanged, not cheaper or more expensive**:
`approval.date` remains bare operator-typed text (`check-state.sh:267`), cross-checked against
nothing, reachable only by the main session (still the sole writer of `plan.yaml`'s `approval:`
fragment, still exempt from `check-domain.sh` entirely). Cycle 0's MED / no-escalation reasoning
for *that* specific gap holds as-is; I re-derived it against this diff and found no change.

## F2 remedy — four of five table rows fail-closed as claimed; the fifth is the finding above

Walked all five declared rows plus the malformed-JSON path against the live code
(`check-state.sh:195-231`): no-config → `_era_start = None` (grade all, correct, INV-1 owns the
finding); absent key → hard `bad` naming `/harness-init --upgrade` (correct); `null` → grade all,
no violation (correct — verified by `case_inv32_null_era_grades_everything`); malformed JSON →
`except Exception: _era_raw = None` routes into the `null`-equivalent branch, i.e. **grade
everything**, fail-closed, confirmed (`_era_raw = None` is not `_MISSING`, so it never re-hits the
absent-key violation — this is a real but harmless behavioral nuance: unparseable JSON produces no
INV-32-specific violation of its own, but the separate `cj`/JSON-validity check at :670 catches it
on its own merit, matching the code's own comment); non-str / non-YYYY-MM-DD → hard `bad`
(correct). **The regex is syntax-only**: `re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", ...)`
accepts `"9999-99-99"` (calendar-impossible) with no calendar check, and the subsequent
comparison (`signed < _era_start`) is pure lexicographic string comparison. This does **not**
change exploitability beyond the real-future-date case already described in the finding above —
any ordinary real date (`"2099-12-31"`) achieves the identical wholesale-exemption effect, so I
rate the impossible-date acceptance itself `info`, folded into the HIGH finding rather than a
separate line.

## The new finding, in full

**Actor:** `harness-dev-ops` (governed, Engineering team, no relation to plan approval/panel
authority; `consult-when`: infra/CI/CD/build tooling). **Channel:** ordinary `Write` tool call to
`.harness/harness.json`, permitted by its own pre-existing domain grant
(`team-config.yaml:210`, `upsert: true`) — the `PreToolUse` `check-domain.sh` hook allows it
cleanly; no `approval_guard`-equivalent fragment check exists for `harness.json` (grepped: zero
mentions of `panel_era_start` anywhere in `check-domain.sh`). **Effect:** setting
`panel_era_start` to any date later than every currently-signed `approval.date` in the tree moves
every one of those 32 (and every future) approved plans from "must carry a complete `panel:`
record or hard-fail" to "warn-only, not graded, permanent" — the exact fail-open shape cycle 0
rated MED for the single-writer `approval.date` case, now reachable by an actor who holds no
approval or panel authority by any other route. **Why this differs from cycle 0's F1 dispensation
(P-02):** dev-ops cannot forge `panel:` or `approval:` directly (denied by `approval_guard`, and
`panel:` is validator-lead's channel by convention) and cannot legitimately fabricate an
INV-32-passing record — this grants it a capability (mass, permanent gate exemption) it does not
otherwise have, which is privilege escalation, not a quieter route to a pre-held authority.
**Compensating factors, weighed and found insufficient to lower severity:** (1) `check-domain.sh`
itself documents that arbitrary Bash from *any* Bash-holding agent is an unwinnable, pre-existing
gap (not new here) — but that is a *different*, already-known risk; the dev-ops `Write`-tool path
is sanctioned and needs no bypass at all. (2) "Merge stays user-gated" (`team-config.yaml:217`
comment) is dev-ops's stated compensating control — but that is the exact same "a diff reviewer
could catch it" argument cycle 0 weighed for the one-field `approval.date` omission and still
rated MED, and a `panel_era_start` date sits inside routine devops/CI config changes, arguably
easier to bury than a plan.yaml edit. **Severity: HIGH** — exploitable by a governed agent against
the gate-integrity control the whole feature exists to protect, reachable via a sanctioned write,
with tree-wide and permanent blast radius.

**[See re-adjudication: compensating factor (1) above was under-weighed — the same
`.claude/skills/harness/bin/**` grant that carries the DEC-85 sharp edge also covers
`check-state.sh` itself, which is a superset route, not a "different, already-known risk."]**

## Verdict (cycle-1, original — see re-adjudication for the current position)

`must_fix`: the `panel_era_start` write channel needs the same protection `approval:` already
has — either restrict it to the main session (mirroring `approval_guard`'s carve-out) or bind it
to independently-verifiable provenance. Implementation is the operator's/eng-lead's call, not
mine to prescribe.

```yaml
VERDICT: FAIL   # SUPERSEDED — see final yaml block under Re-adjudication below
DIGEST:
  headline: "F1 and F2 close what cycle 0 named, verified by re-run — but F2's config-driven boundary lets harness-dev-ops, which holds no approval/panel authority, silently and permanently exempt every approved plan in the tree via a sanctioned Write to harness.json; unmitigated, HIGH, not covered by cycle 0's no-escalation reasoning."
  in_scope: true
  scope_reason: "check-state.sh's INV-32 gate-integrity control gained a config-driven exemption boundary this cycle; the config file's writer set differs from the fragment it now gates, which is exactly the self-attestation surface this role exists to audit."
  severity_max: high
  findings: 4
  must_fix:
    - "panel_era_start (.harness/harness.json) is writable by harness-dev-ops via a sanctioned Write call with no domain or fragment guard, and controls wholesale, permanent INV-32 exemption for every approved plan in the tree — an actor with no approval/panel authority gains authority over gate-integrity grading it does not otherwise have. Needs the same protection approval: already has (main-session-only write, or bound provenance)."
  threat_model:
    - { boundary: ".harness/harness.json panel_era_start (harness-dev-ops Write channel, team-config.yaml:210, pre-existing grant repurposed by this diff into a security-relevant field)", stride: "E (Elevation of Privilege)", mitigated: false }
    - { boundary: "plan.yaml approval.date (main-session-exclusive channel, DEC-120, unchanged by this diff)", stride: "R (Repudiation, self-attested, uncorroborated against git)", mitigated: false }
    - { boundary: "INV-32 undated/malformed approval.date exemption (F1 remedy)", stride: "T (Tampering)", mitigated: true }
    - { boundary: "panel_era_start syntax validation accepting calendar-impossible dates (e.g. 9999-99-99)", stride: "I (Info: no incremental exploitability over a real future date)", mitigated: false }
  open_questions:
    - { id: Q1, question: "Should panel_era_start be moved under the same DEC-120 main-session-only carve-out approval.date already has, or is dev-ops's infra/config trust meant to extend to gate-integrity boundaries — and if so, should that be an explicit decision rather than an implicit consequence of an existing domain grant?", blocking: true }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-1071-inv32-era-guard/notes/review-harness-security-reviewer-bug1071-c1.md
```

---

## Re-adjudication (loop-back)

**Ground under test (from the cycle-1 finding above):** "dev-ops does not already hold
panel/approval authority by any other route, so this is new capability, not a cheaper route to
an old one." This is factually false, and the finding does not survive re-derivation.

### Three facts checked, plus the fourth named in the loop-back dispatch

1. **`harness-dev-ops`'s domain grants `.claude/skills/harness/bin/**` with `upsert: true`**
   (`.harness/team-config.yaml:211`) — the line immediately after the `.harness/harness.json`
   grant (`:210`) in the same domain block. `check-state.sh`, the script that *implements*
   INV-32, lives at `.claude/skills/harness/bin/check-state.sh` (confirmed on disk). **CONFIRMED
   TRUE.** Dev-ops can edit or delete the INV-32 block itself through this same sanctioned
   `Write` channel — strictly greater authority than moving a boundary date, since it is a
   superset of every effect a date change can produce.
2. **Identical grant ships in the template**, `.claude/skills/harness/templates/team-config.yaml:184`
   — same path, same `upsert: true`, same trailing comment. **CONFIRMED TRUE.** This is not an
   artifact of the harness repo reviewing itself; every project onboarded from this template
   inherits the same dev-ops reach over its own INV-32 enforcement script.
3. **DEC-85's trailing comment** (`team-config.yaml:217-219`): dev-ops holds Bash, which "bypasses
   path checks entirely... trusted by design... the compensating control is that merge stays
   user-gated." **CONFIRMED TRUE, re-weighed.** In cycle 1 I set this aside as "a different,
   already-known risk" because the `Write` path to `panel_era_start` needs no bypass. That framing
   was too narrow: DEC-85 is not just a bypass-risk footnote, it is a signed statement that
   dev-ops's trust envelope already spans "own the build and release tooling" — which is precisely
   the envelope fact 1 shows already covers the INV-32 enforcement script. It corroborates fact 1;
   it does not independently move the needle.
4. **`harness.json`'s `gates`/`test_matrix`/`test_kinds` blocks predate this diff, untouched by it,
   and are already writable by dev-ops through the same file-level `upsert: true` grant.**
   `git diff 75daa3bb..6b65ecc -- .harness/harness.json` shows exactly three changes:
   `schema_version` 1→2, the new `panel_era_start`/`_panel_era_start_note` pair, and an unrelated
   JSON-escaping re-encode of the project-board `_note` string. `gates` (`qa_gate: blocking`,
   `review: advisory_unless_high`, `uat: blocking_when_uat_criteria_exist`, `merge: user_gated`),
   `test_matrix` (per-change-type required test kinds), and `test_kinds` (`cmd`/`status`
   active-or-excluded per kind) are all present, unchanged, and covered by the same file-level
   grant dev-ops already held before this diff. **CONFIRMED TRUE.** No field-level guard exists
   inside `check-domain.sh` for any key in `harness.json` (grepped: zero matches for
   `panel_era_start` or field-scoped logic) — the grant has always been all-or-nothing at the file
   level, so dev-ops could already, before this diff, weaken `qa_gate`, flip a `test_kinds` entry to
   `excluded`, or zero a `test_matrix` row's required kinds. That is gate-integrity authority at
   least as consequential as exempting INV-32's panel check, and it long predates this feature.

### Answer to the narrow question: does `panel_era_start` grant a capability dev-ops does not
### already possess by a sanctioned route?

**No.** Two sanctioned, pre-existing, unbypassed routes already reach an equal-or-greater effect:

- **Route A (direct, superset):** `.claude/skills/harness/bin/**` covers `check-state.sh` itself.
  Editing the INV-32 block's logic subsumes every effect a `panel_era_start` date change can
  produce, plus more (e.g. removing the check's `exit 1` entirely, not just moving its window).
- **Route B (same file, sibling fields):** `harness.json`'s `gates`/`test_matrix`/`test_kinds`,
  pre-existing and untouched by this diff, already let dev-ops weaken test-matrix or gate
  enforcement tree-wide through the identical `upsert: true` channel this finding names.

Since both routes were sanctioned and reachable *before* this diff landed, `panel_era_start` is
not a new class of authority — it is one more field inside a domain dev-ops already fully and
legitimately held. This directly falsifies the cycle-1 ground and the finding does not survive as
stated.

### Re-rated severity: **MED**, held down from HIGH

This is exactly the shape cycle 0 rated MED for `approval.date`
(`review-harness-security-reviewer-bug1071.md:77-83,126-129`): P-02 — an actor who already
controls a broader route already holds the privilege a narrower one grants, so this is a quieter,
cheaper path to an already-reachable outcome, not privilege escalation. Cycle 0 closed that MED
with `must_fix: []` — a recommendation, not a blocker — and I apply the identical treatment here
for the identical reason.

**Residual, not eliminated:** a one-field JSON date bump inside a routine devops/CI config change
is a smaller, less conspicuous diff than a `check-state.sh` control-flow edit or a `gates:` value
flip — review attention calibrated to "dev-ops touched bin/ or harness.json for infra reasons"
may not flag a quiet date change the way it would flag deleting a Python `if` block. That
detectability delta is what keeps this above `low`/`info`, same reasoning cycle 0 applied to keep
`approval.date` at MED rather than closing it to nothing. Recommend, not blocking: fold
`panel_era_start` into the same review-diff attention dev-ops's `bin/**`/`harness.json` edits
already receive, and consider (as a follow-up, not a gate) cross-checking it loosely against git
history the way Q2 proposed for `approval.date`.

**`threat_model` correction:** the `panel_era_start` boundary is reclassified from **E (Elevation
of Privilege)** to **T (Tampering)** — the actor is not gaining privilege it lacked, it is
tampering with a gate-relevant value through a channel it already held for a broader purpose.
`mitigated` stays `false` (no independent guard exists), consistent with `approval.date`'s own
unmitigated-but-MED treatment.

### Updated verdict

`must_fix` is now empty. No finding in this set reaches `high`. `severity_max: med`.
`VERDICT: PASS` (advisory notes carried, per cycle 0's own precedent for the same shape). The
five-row walk, F1 verification, FEAT-40 backfill confirmation, and calendar-impossible-date
`info` note are unchanged and still stand.

```yaml
VERDICT: PASS
DIGEST:
  headline: "CHANGED (HELD-in-spirit downgraded, not reversed): panel_era_start is not new capability — dev-ops already holds a superset route (check-state.sh itself, .harness/team-config.yaml:211) and a sibling route (harness.json's own untouched gates/test_matrix/test_kinds, same file-level grant) reaching the same or greater effect; cycle-1's HIGH ground is falsified, re-rated MED matching cycle 0's approval.date precedent, must_fix cleared."
  in_scope: true
  scope_reason: "check-state.sh's INV-32 gate-integrity control gained a config-driven exemption boundary this cycle; re-derivation shows the writer of that boundary already holds broader, pre-existing gate-integrity authority over the same enforcement surface through two other sanctioned channels."
  severity_max: med
  findings: 4
  must_fix: []
  threat_model:
    - { boundary: ".harness/harness.json panel_era_start (harness-dev-ops Write channel, team-config.yaml:210) — reclassified: dev-ops already holds a superset route via .claude/skills/harness/bin/** (team-config.yaml:211, covers check-state.sh itself) and a sibling route via harness.json's own pre-existing gates/test_matrix/test_kinds fields (untouched by this diff, same file-level grant)", stride: "T (Tampering, reclassified from E — not new privilege, a quieter route to an already-held one)", mitigated: false }
    - { boundary: "plan.yaml approval.date (main-session-exclusive channel, DEC-120, unchanged by this diff)", stride: "R (Repudiation, self-attested, uncorroborated against git)", mitigated: false }
    - { boundary: "INV-32 undated/malformed approval.date exemption (F1 remedy)", stride: "T (Tampering)", mitigated: true }
    - { boundary: "panel_era_start syntax validation accepting calendar-impossible dates (e.g. 9999-99-99)", stride: "I (Info: no incremental exploitability over a real future date)", mitigated: false }
  open_questions:
    - { id: Q1, question: "Should panel_era_start (and, more broadly, gates/test_matrix/test_kinds in harness.json) get the same review-diff scrutiny convention as source-code edits under bin/**, given all three are reachable through the identical sanctioned dev-ops Write channel and a quiet config-value change is easier to miss than a logic edit?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-1071-inv32-era-guard/notes/review-harness-security-reviewer-bug1071-c1.md
```
