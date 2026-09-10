# STATE

## Current

- feature: FEAT-104-strict-digest-schema
- runs: `2026-09-10-11-goalcheck-product` (pm goal-check, hosted by `harness-product-lead`, at
  `review_sha` 168f875f)
- squads: product
- status: validate — **the goal-check is done and ONE criterion is unmet: SC-08, a PROOF gap, not a
  delivery gap.** The c9 reviewer panel's PASS at `168f875f` is unchanged. Owed before ship: SC-08
  resolved by the main session (no squad may take it), the SC-13 UAT, the CEO briefing.

**REQ-01..REQ-09 all met. Of the 15 live criteria, 14 met, SC-13 pending-operator, SC-14 struck.**
Table with per-item counts and `file:line` evidence:
`notes/research-FEAT-104-goalcheck-build-c9.md`; lead assessment in
`runs/2026-09-10-11-goalcheck-product/digest.md`. pm graded per ITEM wherever a criterion
quantifies — 9/9 personas (SC-02), 16/16 documented fields + 5/5 passthrough rows + 22/22 step keys
(SC-05), 16/16 `CONTRACT_SOURCES` personas (SC-16) — so no file-global grep stood in for the Nth item.

**SC-08 is unmet, and I verified both halves at this tier rather than relaying them.** It demands
the declaration route be named at TWO seams and *asserted as a substring*.
- Delivery CORRECT at both: at the pin, `check-domain.sh:1653-1658` emits
  `.claude/skills/harness/bin/run-state-schema.json` and the `evidence` container;
  `check-state.sh:1526-1530` emits the same route in its INV-16 message.
- Proof exists at ONE: the digest seam is asserted (`test-validate-digest.py:3138-3146`). Across all
  three integration test files at the pin the only `run-state-schema` occurrence is the `open()` at
  `test-check-domain.py:117` — an argument, not an assertion. The step-seam refusal cases
  (`test-check-domain.py:85-87`, `:105-110`, `test-check-state.py:51-54`) assert only `undeclared
  step key` plus the key name.

**No fix cycle exists for it, so none was dispatched.** The remedy is one substring assertion inside
`tests/integration/test-check-domain.py`, a DEC-174 carve-out file — main-session-direct, routable to
no lead at any severity. Up as Q8, blocking. **The two routes differ in cost:** adding the assertion
satisfies an already-approved criterion and needs no re-signature; NARROWING SC-08 to the digest seam
amends a SIGNED criterion and is the operator's call alone.

**SC-12 (`verify: inspection`) was actually executed, and I re-ran both halves myself.** pm ran
T-10's `verify:` at the owner root: positive `manifested 728 changed 0 vanished 0`, exit 0;
discrimination against a mutated manifest COPY, exit 1 naming
`.harness/harness/features/FEAT-18-board-truth/runs/2026-08-13-06-validator/state.yaml`. My
independent re-run reproduced both, same named path, mutating only an in-memory copy. 728 ≥ the 726
floor (runs are append-only). **Neither of us touched a real run artifact** — that is the criterion's
own subject, so proving it by mutation would falsify it. The check demonstrably CAN go red.

**SC-13 remains pending-operator and nothing here closes it** — the DEC-174 human diff read. Two
concrete targets for it: CF-4's raw Python `None` in the `schema_version` downgrade message's
omitted-on-update edge case, and CF-1's unescaped `run_id`/step-id in `check-state.sh`'s INV-16
message. **The UAT may now be generated;** SC-08's resolution is orthogonal to the diff read.

**Two record corrections, so neither is silently inherited.** pm's note mislabels two question ids
from the previous `## Current` (it maps Q1 to a downgrade comparison and Q3 to the raw-persona
at-rest question; here Q1=CF-1, Q3=CF-2, Q5=CF-4) — the lead caught it in its `adequacy_notes`, the
labels are wrong and the routing they carry is not, and it was not worth a spawn. And SC-09's BRIEF
anchor is stale: it cites `validate-digest.py:1744`, where at the pin the `stop_hook_active` guard
sits at `:1828-1829` ahead of every `validate()`. pm graded on substance and said so.

**`cycles_used` stays 8, read against DEC-157**, which counts a FAIL routed BACK, an unmet-SC
RE-DISPATCH, or a lead-reported send-back. This was a clean first pass with zero send-backs, and
SC-08 was not routed back because no squad may take it. Discovering an unmet criterion is not itself
rework. Two cycles remain. **`len(runs)` is 21 of `max_total_runs` 20 — the informational tripwire
is now PASSED**, surfaced here and not only at the next `/harness` entry; it stops nothing (#79). My
read: this run earns its place, being the goal-check the feature cannot ship without, and it found a
real gap four reviewers at the same pin did not.

**The pin did not move.** `review_sha` is `168f875f`; no source or test file was modified —
`git status --porcelain` shows only pm's note and its observations log.

## Open Questions

- Q8 (**BLOCKING**, main session, DEC-174 — new): **SC-08 unmet as a PROOF gap.** Add the one
  substring assertion beside `test-check-domain.py:85-87` (satisfies an approved criterion, no
  re-signature) or narrow SC-08 to the digest seam (amends a signed criterion, operator only).
  Evidence in `## Current`; carve-out either way, so no squad may take it.
- Q9 (not blocking, main session — new): REQ-08's generic-lead archive exemption
  (`validate-digest.py:1407`) has no test able to redden. It does NOT falsify REQ-08, which is met on
  other evidence; qa carried the same gap. Backlog chore, or accept as a standing risk?
- Q1 (not blocking, main session, DEC-174): **CF-1** (security, `med`) —
  `check-state.sh:1525-1526`'s INV-16 message interpolates `run_id` and the step id as bare strings,
  alone among this diff's attacker-controlled interpolations, so the accepted DEC-85 Bash-write route
  can spoof or erase the audit line reporting it. One-line remedy (`!r`, or list-wrapping). No
  operator-channel witness exists. Detail: `runs/2026-09-09-10-panel-validator/digest.md`.
- Q2 (not blocking, main session): **CF-3** (code, `low`) — `abff2a84`, a FEAT-56 `plan.yaml` station
  flip, is this branch's root commit and merges with this PR, untracked by any REQ or D. Lead
  recommends ACCEPT and record in the ship note; excising it means rewriting history beneath a
  signed pinned `review_sha`. I concur; the call is the operator's.
- Q3 (not blocking, main session): **CF-2** severity CONTESTED, carried unreconciled — qa `med`, code
  `info`, lead `low`. `check-state.sh:1590`'s literal-`lead` at-rest exemption has no test able to
  report RED; the remedy is a test inside the carve-out, so no squad may close it at any severity.
- Q4 (not blocking, main session, harness defect): the `lead` schema declares no `code_grade`
  (absent from `SCHEMAS['lead']`, `PASSTHROUGH['lead']`, `DOCUMENTED_OPTIONAL`), so a lead hosting a
  code-grading run cannot declare it at top level without tripping this feature's own undeclared-key
  rejection. Plausibly deliberate — the recomputation at `validate-digest.py:1430-1441` binds only
  `harness-code-reviewer` — but my c9 dispatch demanded a field the contract forbids, my error, not
  the lead's. Should `PASSTHROUGH['lead']` gain it as an unverified roll-up, or keep forbidding it?
- Q5 (not blocking, main session, DEC-174): **CF-4** (ui, `low`) — the `schema_version` downgrade
  branch renders a raw Python `None` in the omitted-on-update edge case instead of the floor check's
  "schema_version is absent" phrasing; `T-06` has no omitted-on-update case, so no test saw it.
- Q6 (BLOCKING, main session, DEC-174 — carried forward unchanged): `check-domain.sh:1327`'s
  append-only correction channel cannot repair a run digest — `validate-digest.py`'s parser stops at
  the indent-0 `artifact:` line. Two digests stranded (`runs/-06`, missing `adequacy_notes`;
  `runs/-08`, `PASS` beside a `FAIL` member step). A harness defect, not a finding about this diff.
- Q7 (not blocking, main session): the 3 complete + 2 partial strict-version predicate spellings
  (`check-domain.sh:1594-1597`, `:1761-1764`, `check-state.sh:1487-1489`; partials `:1601`,
  `:1767-1768`) want one `is_strict_schema_version()` home. SIMPLIFY's reuse residual — backlog or
  fold-in before ship?
- Residual non-gating risks, so they do not die silently, detailed in the c9 panel digest: the
  pre-existing DEC-85 Bash-write bypass (CF-1's precondition); F2's runtime residual, an undeclared
  key on a NEW lead digest uncaught AT REST though closed at write time; and `check-domain.sh`'s
  `_no_parser` bootstrap early return, confirmed caught by the next sweep.
- Coverage gap the panel could not close (DEC-174): `run-state-schema.json`'s guards
  (`check-domain.sh:1618-1667`, `check-state.sh:1486-1535`) are ARGUED fail-closed plus a
  non-tautological DECLARED-literal cross-check (`test-check-domain.py:14,114-124`), not
  mutation-proven — the mutation would edit a carve-out file. Red capability rests on reasoning.
- Also standing: qa's `F-QA-1` (`T-05` `change_type` vs DEC-212 `touches_config_shape`), its second
  cycle raised; `matrix_ok: true` is ADOPTED from same-pin evidence
  (`notes/qa-feat104-tip-168f875f.md`), not freshly measured, with provenance md5-verified; and the
  INV-26 card/plan mismatch plus the per-persona worktree-claim guard, both unchanged.
