# FEAT-48 — cycle-3 advisories applied, plan signable and unsigned

## BLUF

All three c3 advisory items are in, as three hunks and nothing else. `check-plan-routes.py` on this
plan exits **0** (`0 violation(s) across 1 plan(s)`; six `DEVIATION` lines, all the expected DEC-174
carve-outs, byte-for-byte the pre-edit set). `approval.status` is still `pending`, `approved_by`
null. No id renumbered, no `verify:` block touched. **Nothing here reopens design.**

## What changed — three hunks, `git diff -U0` verifiable

| item | where | edit |
|---|---|---|
| **F2** (med) | `plan.yaml` D-11 `because:` (now `:184-194`) | new paragraph `THERE IS A FOURTH UNCOVERED CLASS`, sibling to the third: taint does not propagate through a file's CONTENT, so a write to a target read out of a manifest/config/fixture is unflagged even inside the live checkout. States that the runtime half still grades it inside DIR, that outside DIR neither half sees it, that it is unexploited at `d5c23a0`, and that the exclusion stays because `SC-03`'s live-tree zero is otherwise unreachable in any tree. The pre-existing closer ("not complete and no criterion here claims they are") is preserved as the closer. |
| **F2** | `plan.yaml` T-05 `intent:` (now `:1006-1013`) | the mandated DECISIONS entry must "name a fourth alongside it", with the same content rule plus the reason the exclusion exists, and must claim no more coverage than the two mechanisms deliver. **The `need:` phrase list at `:930-933` is untouched** — the entry grows, the word floor only gets easier, and no counted token was added. |
| **F1** (low) | `BRIEF.md` `REQ-02` | "anywhere in the test tree" replaced with the coverage the mechanisms actually deliver (target derived from the test's own path, or target inside the watched shared code directory), citing D-11 for the classes neither sees. Grepped the whole BRIEF: **zero** remaining occurrences of `anywhere` or `test tree`, so the narrowed claim has no surviving twin. |
| **SNE-01** (low) | `plan.yaml` D-03 `because:` (now `:61-69`) | **ADOPTED**, recorded as `ACCEPTED CONSEQUENCE`. |

## SNE-01 — the reasoning, since a future reader will ask

Accepted, not dismissed. D-03 prunes exactly four directories and does walk `.harness/**`
(`plan.yaml:52-56`); with D-04 refusing an escape hatch, any `test-*.py`/`test_*.py` anywhere under
the root becomes a gate subject the moment it is written — a repro script saved beside the thing it
reproduces reddens every open PR's unit step until renamed. Taken deliberately because the failure
is **loud**, names file and line, and is recovered by a rename. The alternative — a curated
directory list — stops seeing a test file the moment someone moves it, which fails **silently** and
is the exact failure mode this invariant exists to prevent. Trading a noisy recoverable false alarm
for a quiet blind spot is the wrong direction for this feature.

## How "cycle-3 state otherwise undisturbed" was confirmed

`git diff -U0` over the worktree shows **exactly three hunks in `plan.yaml`** (at `+61`, `+184`,
`+1006`) and **one in `BRIEF.md`** (`REQ-02`), and no other tracked file modified
(`git status --porcelain`: two `M`, plus the untracked c3 review note). No `verify:` block, no
`id:`, no `execution_mode:`, no `traces:`, no `depends_on:`, no `panel:` entry, no approval field
appears in the diff. `yaml.safe_load` reloads clean: 11 decisions, 6 tasks, every edited scalar's
tail intact (D-03 ends `...this invariant exists to prevent.`, D-11 still ends on the `ccf674a`
bin-count sentence).

## Open

- Nothing blocking. The operator signs next; both `## Approval` and `approval:` remain pending, as
  they must.
