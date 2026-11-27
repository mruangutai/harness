# BUG-2451 · c3 code review

**FAIL — MF-2R's original probes now pass, and A-3 is resolved, but the new section lookup can still let a changed DEC-257 claim through (ruling L2).** No production defect found in the pinned text or code; this is a T-01 verification failure. Return it to the operator, not to another fix round.

### 1. Spec compliance

Reviewed `bda4a7eb..a97dbc6a` from the assigned worktree; `055a7d0d` is the only human-marked commit (signoff, no product changes). `b7e1f26e..c9596b9a` changes only the unit test among product paths. Merge `6e8c8c58` resolved only the index conflict; its other decision-document changes are upstream. Against `origin/main`, the five paths still carry the same feature content: pruner and ship blobs match c2; DECISIONS has only the DEC-238 bullet edit; the regenerated index delta is anchor shifts. DEC-257 and the other four keep decisions have identical section bodies to base.

- **SC-03/D-01 inspection:** `DECISIONS.md:8137` and `harness-ship.md:47` each match the `5e51124e` literal plus the one signed refusal sentence; pruner docstring agrees (`prune-run-evidence.py:19–29`); index regenerates byte-identically.
- **SC-04 inspection:** `harness-ship.md:36–56` preserves position, both calls and commit name; the pruner diff leaves CLI, retention and UI-only/symlink deletion intact (`prune-run-evidence.py:130–156,202–216`). SC-01/02 candidate checks pass; overriding with the `47d6c54d` pruner gives exit 1, 40 PASS / 12 assertion FAIL, including no-git, index immutability and the five-file check.

### 2. Scratch mutations and code quality

Ran the full unit file for each case from a pin archive, with root/agent/subject overrides unset except for the explicit old-pruner comparison. Old = `b7e1f26e` test against the same product bytes. GREEN = exit 0, 52 PASS / 0 FAIL; RED = exit 1, 51 PASS / 1 named five-file FAIL unless stated.

| Ruling | Scratch change | Pin / old |
|---|---|---|
| L1 | Separate ship-intro and pruner-docstring probes: `Force-stage retained records.` and `Force` + newline + `stage retained records.` | RED / GREEN for all four. Ship also RED for a break after `Force-stage`. |
| L2 | Separate DEC-257 `no` → `No` and added broad-ignore claim | RED / GREEN both. |
| L3 | None | GREEN / GREEN; signed verify exits 0, with 55 printed PASS lines because it reprints three of the 52. |
| L4 / A-3 | Separate same-line unrelated DEC-100 `git add` and broad-ignore phrase | GREEN / RED both; index fresh. **Resolved.** |

**Gating substance · med · T-01 verification / ruling L1–L2:** `test-prune-run-evidence.py:653–657,693–701` treats a missing literal heading as an empty scan. Add one space between `##` and the decision ID (still a valid heading to the index generator, `gen-decisions-index.py:28,114`), then append a forbidden claim within that section without adding a line. For DEC-238, the ordinary-heading probe correctly fails but the spaced-heading probe goes GREEN, because the exact ship-bullet check searches globally and that bullet is untouched. For DEC-257, adding the broad-ignore claim plus the same valid heading spacing goes GREEN instead of failing L2. Both mutants are confined to `DECISIONS.md`, and the signed index diff passes; the old test goes RED for both. These are fail-open on live decision text, not unrelated A-3 text. A title-only change carrying a claim stays RED; renumbering DEC-238 to DEC-938 without updating its index row fails closed as an orphan.

**Other scope probes:** DEC-238's ship bullet, another bullet, and the last line *before* the next heading all fail on an injected claim. A ship-pruner claim just inside DEC-250 and the same claim in its hand-written index ruling both go GREEN (old RED), with exact index regeneration. Out-of-scope unrelated decision prose is exempt under A-3; newly added prose explicitly directing the current ship pruner is not unrelated under T-01's signed five-file intent. These are further fail-open examples of the same scope defect. DEC-238's index ruling goes RED; loose prose appended outside any row also goes RED as stale, because the generator reads and preserves ruling text after ` :: ` but drops loose prose.

**Exception probes:** A claim in an ordinary test comment goes RED. The test excludes both `FORBIDDEN` and `DEC_257` assignments (`test-prune-run-evidence.py:679–686`), not just its own denylist. Adding the claim to DEC-257 and mirroring it in `DEC_257` goes GREEN with the index fresh; adding it only to the constant goes RED. This is fail-open under the unchanged-history-only guard promise, but co-editing DEC-257 itself is outside the authorized patch; not a separate gate from the single-file reproduction. A CRLF-only rewrite of the section goes GREEN with no new claim: `read_text` normalizes newlines, so this is not literal byte equality. `Force-` + newline + `stage` goes GREEN on both tests: inherited split-token miss, distinct from the measured ordinary line wraps and not a separate gate.

**Red-first receipt:** All tabulated `## c2 fix` probes, hashes, c1 preservation mutations and PASS counts reproduced. The census at `notes/red-first-T-01.md:174` saying only `FORBIDDEN` contains matches is inaccurate: the raw `DEC_257` constant also matches `force-stag` and `git add`; the filtered test text has no hits. Form/low, non-gating. Mechanical Python grade: **pass**, 23 passing functions.

Prior advisories still present (pruner unchanged from c2):
- A-1 — listable but non-searchable recorded `ui/` leaf may allow partial prune before deletion errors.
- A-2 — unreadable `ui/` in an unrecorded run is not pre-walked; SC-02 covers recorded runs.
- SEC — directory names reach stderr unescaped; clause still refuses before mutation.

No new review question; the must-fix routes to the operator under the existing ruling.
