# FEAT-47 — cycle-2 panel fixes: both censuses derived, both verifies proven

**BLUF.** The `critical` (T-07 repaired 2 of 5 falsified Expertise files) and the `high`
(`DEC-207` already taken, T-06's presence-grep vacuous) are closed by the same move, recorded as
**D-19**: no literal a sibling can invalidate is load-bearing anywhere in this plan. T-07's scope
is now a derived sweep over `.harness/expertise/*.md` and `.harness/*/expertise/*.md`; T-06 takes
its DEC number at authoring time and its verify locates the entry by title fragment and required
content. Both shipped verify strings were extracted from `plan.yaml` and run verbatim: red on the
tree today, green only on the work the task mandates. `check-plan-routes.py` exits 0, 0 violations.

## What changed

| Site | Change |
|---|---|
| `lanes.rows` | two rows added: the expertise globs (each path resolves to its own persona, no shared seat — `--resolve` over all 28 at `1c9c384`) and this plan file (T-06's bookkeeping write) |
| `D-19` (new) | derivation over enumeration, both censuses, with D-14's guards named. `dec: pending-T-06` |
| `D-17` | de-counted: "every falsified Expertise entry", lane argument re-stated over the whole class |
| nine `dec: DEC-207` | now `dec: pending-T-06` (ten fields incl. D-19); no verify reads the field |
| `T-01` step 4, `T-03`/`T-05` prose | DEC number unpinned; the team-config comment names the FEATURE, since T-01 runs before T-06 takes a number |
| `T-06` | `files:` gains this plan file; `grep -q "^## DEC-207 "` replaced by the content block; intent mandates re-derivation and marks the plan backfill explicitly NOT load-bearing |
| `T-07` | title, `files:` (two globs), verify (derived sweep) and intent (derivation command first, the five known entries as ORIENTATION ONLY) |
| `BRIEF.md` SC-07 | "the two falsified entries" → the set T-07 derives |
| `panel:` (new) | the plan carried NO panel block at all; cycle 2's digest is now transcribed — three readers (scope/`harness-code-reviewer` ran, should-not-exist/`fable-advisor` ran, goalcheck skipped with the lead's reason), six findings, ids from `panel_findings.py`, severities verbatim. The `critical` and `high` are `resolved` by T-07 and T-06; the two `med`, the `low` and the `info` stay `open` |

Untouched, as directed: D-14, D-16's census/refusal design, every floor, T-02's rename provenance,
the re-derived 58/38/19 arithmetic, DEC-174 modes, both `## Approval` / `approval:` blocks (pending).

## Evidence — measured at `1c9c384`, `origin/main` = `75daa3b`

- **Five files, five entry ids, derived not listed:** `code-reviewer G-04`, `dev-ops G-10`,
  `eng-lead G-02` (2 lines), `pm P-01`, `qa G-05` — six token lines. 28 tracked expertise `.md`
  files; `git log -S UNIT_SCRIPTS` puts all three newly-found entries' current text at `e798b08`
  (FEAT-45's own post-merge distillation on this branch's base ref).
- **T-07's sweep, eight tree shapes** (synthetic repo, real `check-expertise.sh` copy, base ref
  planted as `refs/remotes/origin/main`): unrepaired → 1; all five repaired → **0**; only the old
  two → 1; ids renumbered → 1; neither directory named → 1; glob matches nothing → 1 (`files 0`,
  floor, explicit message not a traceback); positive control empty → 1; **a sixth file appears,
  unrepaired → 1**.
- **T-06's DEC block, six shapes** (real `DECISIONS.md` copy): tree today → 1 (`headings []`, the
  pre-existing unrelated `DEC-207` does not satisfy it); faithful `DEC-208` → **0**; reusing 207 →
  1 (`dupes ['207']`); four tokens absent → 1; stub body → 1 (`words 31`); no title fragment → 1.
- **Verbatim, not a local copy:** both bodies extracted through `harness_yaml.load_plan` and
  compared byte-identical to the proven scripts before being run. Machine-field lines: T-07 47,
  T-06 37 (budget 50).
- `check-plan-routes.py <plan>` → `0 violation(s) across 1 plan(s)`, exit 0. T-07's two globs print
  `UNRESOLVED-GLOB` (non-gating, same as T-02/T-03 today); T-06's `DEVIATION` is the DEC-174
  carve-out shape.

Probe harnesses were ephemeral (`/tmp/feat47-sweep/`, not shipped). To reproduce, extract each
`verify:` from `plan.yaml` and run it in a tree of the shape named above.

## The three questions, on both blocks I touched

|Block|What reddens it|A tree where it passes|Action vs inaction|
|---|---|---|---|
|T-07|any token line under either glob, a dropped pre-image id, a vanished file, a repair naming neither directory, `check-expertise.sh`, a glob under its floor, an empty control|yes — the repaired synthetic tree, exit 0|yes — exit 1 today, on all five files|
|T-06|no entry with the title fragment, a missing mandated token, a stub body, a reused number|yes — faithful `DEC-208`, exit 0|yes — exit 1 today, where the old grep was already true|

## If a sixth Expertise file appears

The sweep's `pre` set grows from the base ref, so the new file is in scope automatically: unrepaired
it is exit 1 (demonstrated), repaired it is exit 0, and no exemption can silence it (D-16 refuses any
exemption pair under an expertise directory). The floors (`>= 28` files, `>= 5` token-bearing at the
base) only ever weaken in a sibling's favour; a result BELOW either is exit 1 naming the shortfall,
and the instruction is to re-derive the census, never to lower the floor.

## Open

- **Q1 (non-blocking).** c2's two `med` findings are untouched by this pass and out of this
  dispatch's scope: `suite-census.py` has no dedicated test of its own four subcommands
  (`residue`'s self-refusal rules in particular), and T-07's verify still cannot enforce the
  WHEN/DO *shape* — a gutted-but-plausible entry that names a directory and keeps its id passes.
  T-07's `not-restated` clause narrows the second but does not close it.
- **Q2 (non-blocking).** `lanes.resolved_at` stays `ea6f51f`; `team-config.yaml` is byte-identical
  between `ea6f51f` and `1c9c384` (`git diff --stat` empty), and the two new rows carry their own
  `1c9c384` provenance in their `reason:`.
