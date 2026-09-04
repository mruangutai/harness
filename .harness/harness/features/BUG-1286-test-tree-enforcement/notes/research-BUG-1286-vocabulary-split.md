# BUG-1286 — plan amendment: T-03 output contract + the two-group vocabulary

**BLUF.** Both operator-selected fixes are applied and carried through every inheriting site.
The `unit.detect` residual is CLOSED from the guard's side, not disclosed, and the widening is
**inert on the present tree — measured, not inferred: zero tracked paths outside `tests/**` match
`*_test.*` or `*.test.*` at `c040c319`.** No new violation is created anywhere in the tracked tree,
so no `DOCUMENTED_EXCEPTIONS` entry was needed and none was added. `panel:` is byte-unchanged, both
approvals stay `pending`, no implementation, test or decision file was touched. All five mechanical
checks pass.

## The two-group vocabulary, in one line

Repository-wide clause: **`test-*`, `test_*`, `probe-*` refused only at `.py .sh .ts .tsx .js .mjs
.cjs`; `*_test.*` and `*.test.*` refused at ANY extension**, mirroring `harness.json`
`test_kinds.unit.detect` (harness.json:269).

## What changed, by artifact and id

| id | field | change |
|---|---|---|
| D-01 | `choice` | vocabulary restated as two groups with different extension policies. Scoping of the policy to the repository-wide clause, and the unwidened bin / under-`tests/` clauses, kept intact |
| D-01 | `because` | justifies the split shape by shape: `probe-*` restricted (8 of 9 outside matches are Markdown/JSONL probe records, and no `detect` glob matches `probe-*`); `test_*` restricted (`detect` reaches it only as `**/test_*.py`, strictly contained by the source-extension form); `test-*` restricted (runner selection shape, no `detect` glob); agnostic pair widened because the guard must be at least as wide as discovery |
| T-01 | `intent` | `NAME_PATTERNS` replaced by `RESTRICTED_NAME_PATTERNS` + `AGNOSTIC_NAME_PATTERNS`, `SOURCE_EXTENSIONS` applying to the first only; exact boolean predicate given; all three named as the authority T-03 imports. New **case 10** (agnostic mirror). Case 8 relabelled "extension-restricted boundary", otherwise unchanged |
| T-03 | `intent` | **Fix 1**: unconditional output contract — fenced row block + `TOTAL … OUTSIDE … VIOLATIONS …` print on every invocation, BEFORE any comparison output; `--against` MISSING/EXTRA is additive; exit status under `--against` is non-zero on a row difference **and** non-zero on any violation row. Disposition vocabulary restated; expected measurement replaced with the re-measurement below |
| T-05 | `intent` | bullet 1 describes the two groups and names the three constants as the authority without enumerating them; the false general consequence sentence is now stated per group |
| BRIEF.md | `## Verification gaps` | residual bullet DELETED; replaced by a closure bullet plus the measurement bullet |
| BRIEF.md | SC-18 (new) | falsifiable criterion for the split, both directions, one method |
| BRIEF.md | Traceability | row for SC-18 |

`verify:` command strings: **none changed.** T-03's and T-04's blocks are byte-identical to
`c040c319`; the ordering fix was written into T-03's intent prose, which is what the panel finding
asked for, and the intent now names T-04's `--against` grep as the mechanical reason the row block
must print in comparison mode.

**Untouched, as instructed:** D-05 in full, the FEAT-44 `probe-session-accessors.ts` path and its
disclosed archival coupling, T-01's seeded registry entry (same exact path, same reason), `panel:`,
`approval:`, the station, `harness.json`.

**Case 1's fixture left alone (lead's constraint, confirmed not restated).** Checked with `fnmatch`
against `*_test.*` and `*.test.*`: all six of its basenames match neither, `test_rogue.py` included
(it matches `test_*`, a group-one shape). SC-06's exact-equality list therefore stays a one-element
list without amendment. The mirror files live in case 10 only.

## The census re-measurement

Command, run from the worktree root at `c040c319` (`git status --porcelain` empty):

```
git ls-files | python3 -c '<basename fnmatch filter over the five shapes>'
```

Result: **TOTAL 85, OUTSIDE `tests/**` 9, VIOLATIONS 0.** Of the 9 — 1 FEAT-44
`probe-session-accessors.ts` (documented exception), 8 `probe-*` Markdown/JSONL records.
**Agnostic-pair matches outside `tests/**`: 0.**
Cross-checked via `git ls-tree -r --name-only HEAD`: identical (TOTAL 85, OUTSIDE 9, AGNOSTIC 0).
No file changes disposition under the new rule; nothing to report to the operator as a new violation.

## Final SC numbering and AC mapping

SC-01 … SC-17 unchanged in number and meaning. **SC-18 added** → REQ-01, REQ-04 → AC-01 (rejected at
any extension for the agnostic shapes) + AC-06 (legitimate non-test probe records remain accepted),
`verify: automated`, `evidence: unit`, graded by T-01 cases 8 and 10.
All **eleven** ACs still map (AC-01 … AC-11 each covered); 18 SCs, each with exactly one `verify:`
and a valid `evidence:` kind where automated; all 8 REQs traced by at least one task and no task
tracing a non-existent REQ.

## The five mechanical checks

1. `yaml.safe_load` OK; `status: plan`; `approval: {status: pending}`, no `rulings`; `panel:` region
   **byte-identical** to `git show c040c319:…/plan.yaml`.
2. `check-plan-routes.py` → `0 violation(s) across 1 plan(s)`; all 5 tasks `OK`; every task carries
   exactly the 11 required keys.
3. `check-state.sh` → **no `INV-35` line at all**; for this feature only
   `VIOLATION … BRIEF.md is NOT approved` (expected) and two `note` lines.
4. Traceability verified programmatically: 18/18 SCs well-formed, 11/11 ACs mapped, 0 untraced REQs.
5. Grep `(?i)SOURCE_EXTENSIONS|source extension|restrict|extension-agnostic|whatever its
   extension|any extension` over the whole of `plan.yaml` and `BRIEF.md`: every hit is explicitly
   scoped to group one, the bin clause, or the agnostic pair. **No surviving blanket claim.**

## Open questions

- **Q1 (non-blocking, harness/state):** `check-state.sh` reports `run dir 2026-09-04-11-product
  exists on disk but feature.json does not record it — orphaned work`. Pre-existing at dispatch and
  not mine (I wrote nothing under `runs/`); it needs reconciling before the next resume.
- **Q2 (non-blocking, for the fresh panel):** the amendment invalidates the cycle-3 panel by
  construction — PF-b1381e1d1016bfebf6d3364eddb5ef59 is addressed in T-03's intent and
  PF-093f4650a55ddd59ad77f704d7101d5f / PF-43252b3fa6f8521818b37a4681924e4a are now moot rather than
  disclosed. `panel:` was deliberately left byte-unchanged; a separate dispatch transcribes the new
  cycle.
