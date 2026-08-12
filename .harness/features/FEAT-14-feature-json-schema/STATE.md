# STATE

## Current

- feature: FEAT-14-feature-json-schema · phase **validate** · status Review
- branch `feat/204-feature-json-schema` · HEAD `3082840` · `review_sha` pinned `3abaedd`
- cycles_used **4** of 10 · runs **19 of an informational 20**
- **All twelve tasks done. Validate is COMPLETE. The feature is NOT shippable.**
- briefing: `notes/ship-review-2026-08-12-validate.md` (+ rendered `.html`)

| gate | result |
|---|---|
| qa gate (`test_matrix`) | **FAIL** — `matrix_ok: true`, 15/18 proven, 3 unmet in declared mode |
| review panel | **FAIL** — three HIGH; security clean on injection/traversal/exposure |
| goal-check | **FAIL** — 12/18 met, 3 unmet, 3 operator-owed |
| four project gates | green: validator rc 0 · routes 0/10 · check-state rc 0 · unit rc 0 |

### Four fixes stand between here and shippable — two are the main session's

1. **HIGH, carve-out (main session).** `check-domain.sh:891-897` catches only `except ImportError:`;
   `SyntaxError` is not one, so a syntax-broken `feature_schema.py` escapes and `:14` makes exit 1
   non-blocking — the unvalidated write lands. Its own comment at `:873-877` names "a syntax error"
   among three cases it must cover and states this consequence; `:529-532` already fixed the class
   with `except Exception:`. The call sits inside the same `try`, so *any* exception escapes. Widen,
   **and give the runtime-crash case its own message** ("not importable" is wrong for a crash).
2. **HIGH, carve-out (main session).** SC-04/05/16 declare `verify: automated`;
   `test-check-domain.py` has **zero** schema-rejection fixtures. **Fix 1 BEFORE 2** — fixtures
   written first would pin the fail-open as expected behaviour.
3. **HIGH, ordinary fix cycle.** `gh-sync.py` can re-file GitHub issues that already exist — the only
   defect here that mutates state outside the repo. `save_recorded:308`'s `open(p,"w")` truncates at
   OPEN, so the zero-byte window is **guaranteed on every call** (measured: 28 bytes → 0 immediately
   after `open`), and `:394` sits inside the per-issue create loop. `load_recorded:274-276` then
   reads a zero-byte file as the **empty** record (measured: loads as `None`, guard fails), so the
   next sync re-creates milestone, parent and every task issue. Remedy is two-part: same-dir
   `mkstemp`+`fsync`+`os.replace`, and make empty-or-non-mapping an error — scoped so a *missing*
   `github` key still means legitimate first sync.
4. **Fix-cycle companions** — B-5 and B-14, cheapest in the same `gh-sync.py` pass.

**Fixes 1 and 2 compound:** a fail-open shipped in the enforcement path, and that path is the one
surface with no standing assertion.

### Operator-owed — legwork done, none may be marked met by any agent

**SC-10** (5 min, `FEAT-11/notes/receipt-feature-key-drop.md`; pm swept all 17, zero unrecorded) ·
**SC-11** (pm recommends MET; residual `factory.issues`/`factory.items` unconstrained at
`feature-schema.json:96-97`) · **SC-15** (script at `notes/uat-FEAT-14-sc15-readability.md`; note no
corpus file carries eleven keys — `factory` is in zero of 17).

### Decided rather than escalated, per the standing instruction

Accepted the panel's MED→HIGH promotion of the `gh-sync` defect on evidence I measured myself ·
restored the orphaned `MUTANT-PROBE` in `DECISIONS-INDEX.md` via `git checkout` and byte-verified ·
retried the panel exactly once after permission rejections · adopted the interrupted qa run's Phase 1
blind derivation · sequenced the panel after qa because live mutants on shared files produce phantom
findings · corrected `cycles_used` 5→4, keeping only the traceable increment · ran the mirror
(`close-task` ×12) after confirming it never calls `save_recorded` · pruned two dead worktree
registrations.

### Corrections to my own record, kept rather than deleted

I ranked fix 3 MED on "a crash mid-write is not routine" — truncation-at-open defeats that. I also
claimed it falsifies `factory_decompose.py`'s docstring; that docstring is `write_factory`'s own
function contract and the finding never needed it. Both withdrawals are in the briefing.

The first panel's own framing is inverted and I did not adopt it: it reads its HIGH as "re-found by
the next panel, so routing failed". It was dispatched FIRST, interrupted, and ran on as an orphan;
panel2 was my retry. Effectively concurrent, found independently — corroboration, not a routing gap.

### Three runs were interrupted and every one ran on anyway (B-13)

The first qa attempt left a live mutant in a shipped document while its digest reported nothing
changed. The first panel reported both substantive reviewers "never started" — both had run, and
returned ~40 minutes later with the stronger version of fix 3. Each lead reported honestly what it
could see; the orphan is invisible from that tier.

### Deliberate non-actions

No distillation or ship-refresh — feature-close steps, and the SCs have not passed. No
`handoff-validate.md` — validate's exit predicate is panel PASS with `must_fix` resolved, which is
unmet, so that seam is not crossed. No `gh-sync ship`, no push, no PR, no merge.

## Open Questions

- Q1 **BLOCKING, main session only**: fixes 1 then 2, in that order. Both DEC-174 carve-outs, so no
  agent tier can perform them.
- Q2 non-blocking: fix 3 (+ B-5, B-14) is an ordinary fix cycle and is the only one a team can start.
- Q3 non-blocking: B-2, the plan-authorship remedy — `verify_red_at` plus an intent cross-grep in
  `check-plan-routes.py`. Not a carve-out. The grep half needs no runner and catches three of eight.
- Q4 non-blocking: SC-10, SC-11, SC-15 — about 9 minutes of operator time.
- Q5 non-blocking: B-16 — reviewers cannot falsify enforcement-path findings, because the write guard
  denies them the fixture creation needed to break a checker deliberately. Neither HIGH was confirmed
  end-to-end for that reason; both rest on reading both code paths plus Python semantics.
- Q6 non-blocking: B-15 — `write_factory` starts from `doc = {}` and can write a document missing all
  eight required keys. The exact mirror of fix 3: each writer holds the property the other lacks.
- Q7 non-blocking: B-3, B-4, B-6..B-12 — seven further residuals, each strikeable by ID.
- Q8 non-blocking: unconfirmed whether `gh-sync.py` and `factory_decompose.py` ever run concurrently
  for one feature (a lost-update risk distinct from fix 3), and whether `factory_decompose` ever runs
  before a `feature.json` exists, which decides whether B-15 is reachable at all.
