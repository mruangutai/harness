# FEAT-58 — applying the cycle-2 goal-check gaps and the denial-tier ruling

**All six items applied and re-verified by reading the written files, not my own prose. The plan is
16 tasks / 15 decisions, 12 REQ / 15 SC all traced, `check-plan-routes.py` 0 violations exit 0.
Two corrections to the record are stated below rather than smoothed: cycle-1's G-1 and G-5 were
recorded applied and were NOT, and the paste-ready wording the dispatch located in the backend-dev
receipt is actually in the team digest.**

Every `plan.yaml` write went through `plan-merge.py` — three `amend` calls on T-17
(`title`, `files --yaml-value`, `intent`), one each on `T-08.intent`, `T-07.intent`,
`D-05.because`, all with `--expect-sha256`, plus one `apply` adding D-15. `BRIEF.md` edited
directly, six hunks. No enforcement-path source, no test file, no worktree touched.
`status: plan`, `approval.status: pending`, `## Approval status: pending`, `panel:` (7 keys) and
every task station (all absent, as before) are unchanged.

## Disposition, one line per item

- **G-9 (high) — APPLIED.** T-17 widened to three call sites. `title` now
  "…at all three call sites so the denial tiers reach sibling checkouts"; `files` gained
  `.claude/skills/harness/bin/harness_boundary.py`; the `THE CHANGE, one edit:` and `COST STATEMENT`
  paragraphs are replaced by the ruling's paste-ready block **verbatim** (one resolution, `:752`
  DENY / `:780` DENY / `:2150` REPORT, REFUSE at exit 2 on `corpus_root` returning `None`, the memo,
  `+1.9908` / `+1.1659` against the `18.5-23.6` ms floor, and the stated residual). I also rewrote
  T-17's own `THE DEFECT` paragraph, which still named `:2150` alone and would have contradicted the
  block two paragraphs later. Integration cases restructured from (a)-(d)-grades-the-sweep to seven
  individually asserted cases: (a) `:752` deny, (b) `:780` deny via a claim in a **sibling**
  registry, (c) the `None` refusal at **both** tiers, (d) the `:2150` report — explicitly not a
  substitute for (a)-(c), (e) owner-root identity, (f) legitimate-empty still allows, (g) the memo's
  call count. (a), (b), (c), (d) and (g) each carry their own failing-first assertion.
  **SC-15** replaced entirely with the ruling's section 2 — graded by outcome per clause, the sweep
  clause explicitly declared insufficient, red-first for (a)/(b)/(c) against the pre-change
  spelling. **D-15** added verbatim; decisions 14 → 15.
- **REQ-12 — CHECKED, and it did need a change.** Its old wording was
  "the guard tier … actually reaches the checkouts it claims to cover" — singular, and *reach*
  only. T-17 now delivers reach at three sites **plus a refusal** when the owner root is
  unresolvable, so as written REQ-12 quantified over less than the task delivers and said nothing
  the `None` clause of SC-15 could trace to. Rewritten as an outcome, no implementation:
  "every guard tier that binds writes to the registered worktree reaches the checkouts it claims to
  cover, and refuses a write whose owning checkout it cannot resolve rather than allowing it."
  Two further BRIEF places asserted the old narrow shape and were corrected in the same pass
  (G-13 discipline): `## Problem` ("the guard tier … reaches nothing") and `## Non-goals`
  ("the **one-line** correction"), which is now three sites plus the refusal.
- **G-7 (med) — APPLIED.** T-08's CREATION-precondition paragraph split into three: *which commit*
  `<fix-sha>` is — the commit at which **all six** of T-01/T-03/T-04/T-05/T-06/T-16 are ancestors,
  and the last of them to land if they land separately, because an earlier commit passes a
  partially-fixed branch; *how it is supplied* — a **required argument of `cmd_create` with no
  default**, matching T-09; and *when it is absent* — exit non-zero, name the missing input, create
  nothing, with absent explicitly not collapsed into not-an-ancestor (absent refuses; not-an-ancestor
  creates full at exit 0). New integration case **(g) THE ABSENT INPUT** in
  `tests/integration/test-feature-worktree-sparse.py`, asserting the three outcomes individually and
  stating that (f) does not satisfy it. **`verify:` unchanged and confirmed byte-identical** — the
  suite is already named in the and-chain, so the new case needs no string change.
- **G-1 (re-opened) — APPLIED, and it had NOT been before.** Classified by measurement over the
  hook set `.claude/settings.json` actually registers. PATH-LOGIC, parity rows: `bash-write-guard.sh`
  (single-target regex `RE_FEATURE_ARTIFACT`, no listing), `validate-digest.py`
  (`FEATURE_DIR_IN_ARTIFACT_RE` / `_contained_feature_dir` resolve **one** feature from the digest's
  own artifact line), `dispatch-guard.sh` (its only features path builds a message string).
  OUTSIDE THE READER SET, with the reason stated in the file itself: `gh-close-gate.sh`,
  `plan-sign-gate.sh`, `inject-expertise.sh` — **zero** occurrences of a features path, measured by
  grep over each file; T-07 must assert that absence as a property so a later corpus read reddens.
  T-07's "Do NOT classify them" instruction is gone; REQ-09's "three further hook-registered gate
  scripts … were never classified" clause is replaced by the classification. The ledger still stays
  OPEN — as an artifact, for the honest reason (no instrument proves completeness over
  inspection-cleared readers), not because those six are unclassified. No count asserted anywhere.
- **G-5 (re-opened) — APPLIED, and it had NOT been before.** Both SC-03 and T-08 case (c) now name
  the command and the ref: `git -C <corpus_root> grep -l <needle> <ref> --
  .harness/harness/features/`, leading `<ref>:` stripped, `<ref>` = the owner root's default branch
  resolved once as `git -C <owner_root> rev-parse <default-branch>`, `<needle>` a fixed literal the
  fixture commits into **more than one** feature directory so a single hit cannot pass by accident,
  compared as a set against the same command run at the owner root. Never a substring check over
  concatenated output.
- **G-8 (low, advisory) — APPLIED, set not widened.** D-05's `because` now states the bound as part
  of the claim: T-13 walks git-index tracked files under `.claude/skills/harness/bin/` **only** and
  T-07's discovery scan reuses that enumeration, so "aimed at exactly that bypass" is true inside
  that directory and nowhere else; a bypassing reader in `tests/`, `.claude/commands/` or elsewhere
  is caught by neither. The enumerated set is explicitly **not** widened, with the reason. T-07's
  intent carries the same bound so the two do not drift.
- **Record honesty — stated, not smoothed.** An earlier disposition table claimed cycle-1's G-1 and
  G-5 were applied. **They were not.** T-07 still carried "Do NOT classify them", REQ-09 still named
  three unclassified scripts, and SC-03 / T-08 (c) still said "a content search" with no command and
  no ref. Both are closed now, and every claim in this note was taken from a re-read of the written
  file (`harness_yaml.load_plan` over `plan.yaml`, a plain read of `BRIEF.md`), never from my own
  edit prose. Second correction, same class: the dispatch said the paste-ready wording lives in
  `notes/receipt-harness-backend-dev-denialtier-eng.md`. It does not — that file holds only
  BLUF + D1-D5. The wording is in `runs/denialtier-eng/digest.md:105-192`, which is what I
  transcribed. Nothing was invented; had it been absent I would have returned BLOCKED rather than
  author the ruling's words myself.

## Traceability, re-derived after the writes

| quantity | value |
|---|---|
| tasks | 16 (T-12 absent, T-17 present) |
| decisions | 15 (D-01…D-15) |
| REQ in BRIEF | 12 |
| SC in BRIEF | 15 |
| traces naming a nonexistent id | 0 |
| untraced REQ / untraced SC | 0 / 0 |
| dangling `depends_on` | 0 |
| `depends_on` cycles | none |
| `check-plan-routes.py` | **0 violations, exit 0**, 10 informational DEVIATION lines |

The c2 goal-check recorded 11 DEVIATION lines; I observe 10 at this state and report the observed
figure rather than the remembered one. Only VIOLATION lines gate, and there are none.

## Open questions

- **Q1 (non-blocking, harness defect, already filed at operator Q7).** `plan-merge.py amend
  --yaml-value` re-emitted `T-17.files` at 4-space indent where sibling tasks use 6. The file loads
  cleanly through `harness_yaml.load_plan`, so nothing is broken; it is cosmetic drift from the same
  defect the operator already accepted as its own ticket.
- **Q2 (non-blocking, for whoever files it).** The engineering ruling's Q1 residual — an
  unresolvable enumeration being indistinguishable from a legitimately empty one
  (`harness_boundary.py:171-174`, `:181-184`) — is stated in T-17 as a residual and in D-15 as
  deliberately out of scope. **It has no ticket yet that I can see.** Neither created nor closed by
  this widening, per the ruling.
