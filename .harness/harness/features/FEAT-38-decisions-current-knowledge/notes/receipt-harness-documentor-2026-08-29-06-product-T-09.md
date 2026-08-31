# Receipt — T-09 — fold DEC-181's partial strike, correct two false claims

**DEC-181 now reads as one live rule with no strike paragraph, and both false claims are gone.**
Verify block exits **0**. Zero `^**STRUCK` lines remain in `DECISIONS.md`; the `## DEC-181` heading
survives.

## What changed — one file, one contiguous span

`.harness/harness/docs/DECISIONS.md`, DEC-181 only. The eight-line span from
`**STRUCK IN PART, 2026-08-10.**` through the peer-budget sentence was replaced in a single
content-anchored substitution (uniqueness asserted, `count == 1`). Nothing else in the file was
touched, so T-08's fold is undisturbed.

The new opening states, present tense, no dates, no attribution:

- the 80-line `CLAUDE.md` budget, enforced on **all four write routes** by `check-domain.sh:1335`;
- that `CLAUDE.md` **is in no propagation checker's scan roots: no propagation checker exists
  (DEC-188)**. Present tense, so it reads as current truth and not as history — that clause is what
  stops the removed half being re-proposed.

Retained unchanged: the 80-derivation from the file's own history (that the history **starts at a
cleanup** — 208-214 lines to 2026-07-27, DEC-135 cut to 50 — and that the evidence **constrains the
number to roughly 75-83 rather than fixing it at one**), the shrink-exemption residuals, the
subdirectory-`CLAUDE.md` residual, and the INV-23 backstop paragraph.

## The two false claims, re-derived against the code (not echoed from the dispatch)

| Claim as written | Truth at this tree | Site |
|---|---|---|
| enforced at `check-domain.sh:779-780` | **line 1335**: `out.append(_head(f"CLAUDE.md is {len(lines)} lines — budget is 80 (DEC-181)."))`, guarded by `if len(lines) > 80:` at 1334 | `check-domain.sh:1334-1335` |
| peers: `` `feature.yaml` 200/20 `` | `feature.json`, budget **300** — `if len(lines) > 300:` / `"feature.json is {…} lines — budget is 300"` | `check-domain.sh:1102-1103` |

`779-780` at this tree is a comment block inside the manifest-does-not-parse branch, citing
`DEC-171 am.1`, with nothing to do with any budget — confirmed by reading `check-domain.sh:775-780`.
All four peer budgets kept and each confirmed in code: expertise 150 · `feature.json` 300
(`check-domain.sh:1103`) · handoff notes 60 (`check-domain.sh:1287`, cap 60 per DEC-160) ·
STATE.md 120 (`check-domain.sh:1343`).

The code's own comment at `check-domain.sh:1303` states the same corrected list —
"expertise 150, feature.json 300, handoff 60, STATE.md 120" — so the entry and the code now agree
verbatim. "No propagation checker" confirmed at `check-domain.sh:523`, `check-state.sh:1786`,
`gen-decisions-index.py:285`. "All four routes" confirmed at `check-domain.sh:1333`.

## Stale prose found and deliberately NOT edited (out of my bounds)

- **`DECISIONS.md:5111`, inside DEC-188's body:** "The propagation checker and the invariant that
  enforced it are struck, and **DEC-181 is struck in part**." That clause is false the moment this
  fold lands — DEC-181 is wholly live. My bounds forbid touching another decision's body, so it is
  raised as `Q1` rather than fixed. One clause, one sentence.
- `feature.yaml` survives in ~10 other entries (DEC-47, DEC-49, …) post-DEC-191 rename. Historical
  entries, other tasks' scope; recorded here only so nobody thinks T-09 swept the file for it.

## Verification

Task `verify:` block cross-checked against `plan.yaml:736-745` — **identical**, character for
character. Run from the worktree (`git rev-parse --show-toplevel` resolved to the worktree):
baseline before my edit **exit 1**, after **exit 0**.

Note on what the block does and does not prove: the `feature.yaml 200/20` negative clause could never
fire — the file spelled it `` `feature.yaml` 200/20 `` with backticks, so that grep was already green
at baseline. The clauses that carried real signal are the `^**STRUCK` absence, the
`check-domain.sh:779` absence within the DEC-181 span, and the `feature.json` 300 presence. Nothing
in the block tests the no-propagation-checker clause, the present tense, or the retained
80-derivation; those rest on my reading and on the section quoted above.

## Host defect hit (non-blocking, same as T-08)

The `Edit` tool refused the hunk: `read` returned tag `#34D3` with `## DEC-181` at 4776, `edit`
insisted the file hashed to `#7669` and echoed *a different decision's body* for those line numbers.
`md5sum` and `wc -l` were identical before and after the rejection (`ae5dc443…`, 6291 lines) and grep
still put DEC-181 at 4776, so the tool's snapshot was wrong, not the file. Worked around with the
content-anchored substitution described above. I could not file it to `xd://report_issue` — the
domain gate denies that path to this role — hence `Q2`.
