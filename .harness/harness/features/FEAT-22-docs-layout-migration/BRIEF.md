# BRIEF — FEAT-22 docs layout migration

Map #336, **unit 4**. Its own atomic unit, no ordering tie to unit 3
(`.harness/notes/map-336-phase1-handoff-2026-08-14.md:295`). Unit 3 shipped as FEAT-21.

**Base: `0f12f14`.** Every figure in this brief was measured at that SHA. The dispatch's pin
reconciles with `git rev-parse HEAD`; the `cf3af8f` in the originating session snapshot was two
commits stale.

## Problem

`docs/harness/` is the last surface still speaking the legacy, single-repository layout language.
Three programs resolve that path from three different spellings, and none of them can be corrected
alone: `factory_config._PROBE` decides which checkout every factory script believes it is standing
in, `harness_boundary.HARNESS_CONTROL_PLANE` decides which paths the two write guards will grant,
and `gen-decisions-index.DOCS_DIR` decides where the decisions authority and its index are read and
written. Change one and root resolution silently picks a different checkout than the classifier is
judging against — a wrong answer nothing reports.

The cost today is concrete, not theoretical. The layout detector deliberately holds
`gen-decisions-index.py` and `harness_boundary.py` MIXED — an accepted, signed price recorded in
`layout_migration.py`'s own docstring — and that debt is assigned to this unit by name. The
committed `docs/harness/DECISIONS-INDEX.md` carries a slash-shaped legacy path in its generated
header, so the file every agent is told to open as its entry point advertises the old location.
And until the docs move, harness's own documentation cannot live in a repository segment, which is
the whole point of the multi-repo control plane.

## Goal

Move the harness design docs from `docs/harness/` to `.harness/harness/docs/`, and move every
reader that resolves that location with them, in **one commit**, so that no landed state exists
where the tree and its readers disagree. Historical records that mention the old path stay exactly
as they are — they are records of what was true, not claims about what is. When it is done the
detector reads `docs: CLEAN — evidence migrated`, the documentor can still write the docs, and the
generated index no longer advertises a dead path.

## What the dispatch got wrong, corrected here before anything is planned

**The CI Layout gate has nothing to flip.** The upstream premise was that
`.github/workflows/tests.yml` asserts `docs: CLEAN — evidence migrated` and must be updated. It does
not. Read directly at `:183-233`, the step asserts exactly four things: the shape of the
`layout: N surface(s) clean, …` summary line (`:202`), the shape of the `examined …` line (`:209`),
that the feature-dir, doc-root and reader-file counts are all **non-zero** (`:219-230`), and the
checker's own exit code (`:233`). **No per-surface string is asserted anywhere in the file.** The
two real CI constraints are therefore: `doc_roots` must stay `>= 1` after the move, and any MIXED
state that reds the checker reds CI. `tests.yml` is in scope only as a possible no-op, and the plan
treats it as such.

**Two other corrections, both measured.** `harness_boundary.py` has **three** sites matching the
detector row's legacy pattern, not two — `:84` (a comment), `:90` (the code entry) and `:221` (a
docstring). And the per-file audit set is **35 files, not ~30**, because the `docs/harness` slash
grep misses the `os.path.join("docs", "harness")` spelling entirely; the five files only that
second spelling finds are precisely the ones that break at runtime.

## The partition rule — stated, then audited, never swept

There are **753 occurrences of `docs/harness` across 191 tracked files** at `0f12f14`
(`git grep -o` / `git grep -l`; the 755/192 in the dispatch is the working tree, which additionally
holds eight untracked review notes — both numbers are correct under their own definition). Sweeping
that surface would rewrite the factory's history.

**The rule: a mention is rewritten only if it is a present-tense claim in live instruction or live
code. Everything else is a knowing survivor and is left standing.**

| Partition | Files | Disposition |
|---|---|---|
| `.harness/harness/**` — shipped feature records | 158 | survivors |
| `.harness/logs/**` — dated log entries | 3 | survivors |
| `.claude/**` | **22** | per-file audit |
| `.harness/notes/**` | 7 | per-file audit (6 dated grillings/handoffs are survivors; `audit-decisions.py` is live) |
| `.harness/expertise/**` | 2 | per-file audit, and a lane decision |
| `docs/harness/**` | 3 | self-references, move with the files |
| `CLAUDE.md` | 1 | instruction-side, takes the new literal |

**35 files audited, 161 survivors.** The 22 `.claude` files are classified by *mechanism*, not by
path spelling, because the spelling is not what breaks: some **break at runtime** (a real-file read
that 404s), some **flip semantics** (the path string may not change at all, but the expected verdict
inverts once the docs stop being a control-plane target), some are **knowing code survivors** whose
legacy string is the point (the detector's own fixtures and reader patterns — deleting them blinds
the detector to the pre-state), and some are **instruction-side literals**. The full classification
with line anchors is in `notes/research-FEAT-22-docs-boundary.md`.

## Requirements

- REQ-01: The harness design docs are reachable at the repository-segment location the multi-repo
  control plane uses, and no tracked file remains at the legacy location.
- REQ-02: Every program that resolves the docs location resolves the new one, and the move and those
  readers land together, so no landed commit shows a half-moved tree.
- REQ-03: The layout detector reports the docs surface clean on migrated evidence, and the features
  surface is unaffected from start to finish.
- REQ-04: Whoever could write the harness design docs before the move can still write them after it.
- REQ-05: Present-tense claims about where the docs live are true after the move wherever they are
  live instruction or live code; historical records are left standing.
- REQ-06: No committed artifact advertises the legacy location, including the generated decisions
  index.
- REQ-07: Sites that state the docs location without matching the detector's pattern are found and
  corrected, because the detector cannot see them and says so itself.

## Success Criteria

**Which runner produces each `evidence:` kind was measured, not inferred.** `run-unit-tests.sh:17-18`
holds two explicit arrays, and the array — not `harness.json`'s `detect` glob — decides what actually
executes. `test-layout-migration.py` is in `UNIT_SCRIPTS`; `test-check-domain.py` and
`test-gen-decisions-index.py` are both in `INTEGRATION_SCRIPTS`, even though both also match the
`unit` kind's `test-*.py` detect glob. Every criterion below names the kind whose runner will really
produce its passing test. This is FEAT-21 ship-review drift B-12 #2, avoided by measurement.

- SC-01: No tracked file remains under `docs/harness/`, and all five that were there — `SPEC.md`,
  `DECISIONS.md`, `DECISIONS-INDEX.md`, `BUILD.md` and `org.html` — are under `.harness/harness/docs/`.
  verify: inspection
- SC-02: The layout detector reports the docs surface clean with migrated evidence when scanning the
  real repository root, and a standing test case asserts it.
  verify: automated      evidence: unit
- SC-03: The features surface reads clean with migrated evidence at both boundaries — captured before
  the first edit, and again after the cluster lands.
  verify: inspection
- SC-04: The coupled cluster — the physical move, the three resolvers, the comment, docstring and
  header rewrites, the grant, and the regenerated index — lands in exactly one commit, and that
  commit's tree contains no tracked file under `docs/harness/`.
  verify: inspection
- SC-05: `check-domain.sh --resolve` names `harness-documentor` for a file under
  `.harness/harness/docs/`, and a standing test case pins it.
  verify: automated      evidence: integration
- SC-06: The committed decisions index is byte-identical to what its generator produces, and its
  header advertises the new location.
  verify: automated      evidence: integration
- SC-07: The unit suite passes after the cluster lands.
  verify: automated      evidence: unit
- SC-08: The integration suite passes after the cluster lands.
  verify: automated      evidence: integration
- SC-09: The CI Layout gate's two real constraints hold after the move — the checker exits 0 and
  reports a non-zero doc-root count.
  verify: automated      evidence: unit
- SC-10: A depth sweep, run with a resolver rather than a literal, finds no live instruction or code
  file carrying a present-tense claim that the docs live at `docs/harness/`, and every remaining
  mention is named as a survivor by the partition rule.
  verify: inspection
- SC-11: A boundary-capture note records the detector's verbatim output before the first edit and
  after the cluster lands, each with the SHA it was taken at, and the note is committed.
  verify: inspection
- SC-12: `DEC-189`'s ruling, which enumerates `docs/harness/**` as one of four named control-plane
  paths, carries a recorded amendment stating the new spelling.
  verify: inspection

## Verification gaps

- `component`, `ui`, `eval` and `typecheck` all have `cmd: null` in `.harness/harness.json`. None of
  them covers any surface this feature touches — there is no UI, no LLM behaviour and no TypeScript
  here — so no criterion above rests on a null kind. `functional` is `excluded` under DEC-187.
- **Six of the twelve criteria are inspection-only: SC-01, SC-03, SC-04, SC-10, SC-11 and SC-12.**
  A reviewer reading an artifact is the whole control on half this feature. That is not a comfortable
  number and it is not padding — each of the six asks something no test kind in this repository can
  answer. SC-01 is a `git ls-files` fact, SC-03's before-half cannot be re-observed once the tree
  moves, SC-04 is a property of a commit, and SC-10 through SC-12 are judgements about prose. The
  reason to say it out loud: FEAT-21's ship review records this exact control failing once, on a
  signed decision that shipped half-built with its task marked done and every gate green.
- **Nothing anywhere stages two repository segments** (FEAT-21 ship review B-1). Every fixture in
  the tree builds one. This feature is therefore not proof that the segment machinery generalises —
  only that it works for the one segment declared here.

## Backlog intake

- **B-1 (two-segment fixture pinning D-08 and segment readability) — DECLINED, with reason.** Its
  one fixture change lands in `test-check-state.py` and `test-check-plan-routes.py` against the
  **features** surface, and it pins D-08, a FEAT-21 decision. Folding it would put a features-surface
  test change inside a docs-surface atomic commit — the exact coupling map #336 exists to prevent,
  and it would restore the enormous-PR review problem this sequence was split to avoid. It stands
  as its own item and loses nothing by waiting.
- **B-10's docs analogue — FOLDED,** into SC-05: the manual `--resolve` pair becomes a standing case
  in `test-check-domain.py`, so the criterion carries automated evidence instead of a measurement
  taken once by hand.
- The `tests.yml` Layout-gate row — **declined as written**, because its premise is false. See the
  correction above. `tests.yml` needs no change unless the checker's own output shape changes, which
  this feature does not do.

## Constraints

- **One atomic commit** for the coupled cluster. `factory_config._PROBE`,
  `harness_boundary.HARNESS_CONTROL_PLANE` and `gen-decisions-index.DOCS_DIR` must move together or
  root resolution silently picks a different checkout than the classifier is judging against
  (map #336, `:295`).
- **The detector gates every boundary**, and the red states between them are named in the plan
  rather than discovered.
- **`docs/PRINCIPLES.md` stays global.** It is not under `docs/harness/` and it does not move.
- **The detector's reader table needs no row edit.** Every docs row already carries its `migrated`
  pattern (`layout_migration.py:93-101`), pre-written for this migration. Confirmed by reading, and
  left alone. Those `migrated` regexes constrain the shape of the edits and are pinned in the plan.
- **`gh-sync.py`, `branch-create-gate.sh`, `validate-feature-json.py`, `factory_claim.py`, the
  gitignore snippet and prose are unit 9**, not this feature.
- **The detector's own legacy patterns and fixtures are not touched.** They are how it recognises
  the pre-state; removing them would blind it.
- **The destination is currently ungranted** — `check-domain.sh --resolve .harness/harness/docs/SPEC.md`
  returns `NOBODY`. The grant lands in the same commit, or the documentor loses the ability to write
  the docs it owns.

## Approval

status: approved
approved_by: operator (Mike Ruangutai), via main session
date: 2026-08-16
notes: Signed on plan r10 under the last-round ruling (sign on eng-lead PASS with no new
  failure — met, must_fix empty, cycle 9/10). History: r7 signature withdrawn when the text
  changed; r8 declined pending the Q5 clause; r9 failed its own purpose (substring match);
  r10 anchors the corrective span and the false-PASS fixture now reds. Q2 confirmed both
  halves earlier; accepted residuals per runs/2026-08-16-11-archreview-eng/digest.md.