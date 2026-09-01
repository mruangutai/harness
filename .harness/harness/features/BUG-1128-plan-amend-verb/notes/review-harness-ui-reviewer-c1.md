# UI/operator-surface review — BUG-1128 panel c1

## Verdict: PASS, advisory findings only

## Census (measured, not predicted)

`git diff --stat fe5c5b57^..fe5c5b57`: 2 files, +510/-0 — `plan-merge.py` (+206),
`test-plan-merge.py` (+304). Extension census across the full diff for
`html|css|scss|tsx|jsx|vue|svelte|less` and `md`: **zero matches** (`grep -c` returns nothing).
`glob` of `.harness/…/BUG-1128-plan-amend-verb/**`: `plan.yaml`, `review_sha`, `feature.json`,
`notes/{handoff-build,handoff-plan}.md` — **no `DESIGN.md`, no mockups/, no prototypes/**. There
is no rendered UI and no design contract in this diff. Confirmed by looking, not inferred from
the diff's shape.

The one operator surface in scope per dispatch: `plan-merge.py`'s CLI — `--help` text
(`_register_amend`, plan-merge.py:1127-1152) and the refusal messages at exits 2/3/4/6/8
(`cmd_amend`, plan-merge.py:1017-1091). I ran the actual binary against three fixtures rather
than reading the strings in isolation (see Evidence).

## Scope on items 1-7 (from the shared panel contract)

- **In scope, answered here:** item 6 (reachability in practice — I ran the decisive real
  REPLACE nobody else had run) and the message-quality slice of item 1/2 (does the hash
  refusal actually help an operator recover).
- **Scoped out, to the named peer lens:** item 1's mechanism question (is pre-lock/under-lock
  correct as a compare-and-swap) and item 2's renderer/test-discrimination question →
  `CodeRev`. Item 3's exhaustive field-block-bounding sweep of the *whole* real file → `CodeRev`
  (I only spot-checked a reconstructed subset, see Open Questions). Item 4 (is `approval:`
  actually unreachable) → `SecRev`. Item 5 (is `_register_amend`'s own-registration read of the
  VERBS table's instruction correct) → `CodeRev`, a design-convention call outside this lens.
  Item 7 (staged blocks correctly NOT applied) → confirmed clean, see below.

## Findings

**F1 — med, advisory.** The exit-2 "needs BOTH --expect-sha256 and --value-file" refusal
(plan-merge.py ~1063) says "Run --show first." but does not reconstruct the actual next command
(`--file <resolved> --key <key> --id <id> --field <field> --show`). Measured against the
precedent the dispatch names — `check-state.sh:327-330`'s own rule that a recovery command must
NAME THE FILE, not print something the operator has to hand-assemble — this message falls short
of that bar, though less severely: the operator already typed `--key/--id/--field` in the same
breath, so nothing here is *unrecoverable*, only more retyping than necessary.

**F2 — med, advisory, the sharper one.** Exit 6 has **two different messages for the same
condition**, and the informative one is not the load-bearing one. The pre-lock check
(plan-merge.py ~1072) names both hashes: `"expected {X} actual sha256: {Y}. Re-run --show and
re-derive your replacement."` The **under-lock** re-check — which the code's own comment calls
"the check that is actually load-bearing" — fires a bare
`"{id}.{field} changed between the read and the lock."` with **no hash, no remedy sentence**
(plan-merge.py, inside `cmd_amend.transform`). Concrete occurrence scenario: an operator runs
`--show`, pauses to compose `--value-file` (or a second writer beats them to the lock), then
runs the replace — the outer pre-check can still pass on a since-changed field if the change
lands in the narrow window between the two reads, so the ONLY message they see is the
minimal one. This is the one place in the diff where the "which exit code fires" analysis in
the shared contract undersells the gap — same code, worse message, on the path that matters
more.

**F3 — med, advisory, demonstrated on the real motivating field.** Confirmed by running a real
`amend` replace, not by reading source: `_render_field` → `_field_lines` → `yaml.safe_dump`
rewrites a multi-line `verify: |` **literal block** into a single-quoted folded scalar with
embedded blank lines (e.g. `verify: 'step one\n\n  step two\n\n  step three'`). SPEC.md:1813
requires `verify: |`, "literal, never folded `>` — a byte-exact contract." **The byte-exact
*content* held** — I compared `yaml.safe_load` before/after and the string round-trips exactly
— but the *form* the operator sees, in the plan.yaml itself and in a subsequent `--show`, no
longer matches the repo's own documented authoring convention, and does so on every multi-line
`amend`. Grepped `harness_yaml.py` and `check-plan-routes.py`/`check-state.sh`: nothing enforces
the scalar *style* textually, only the parsed value — so nothing gates on this, which is why it
stays advisory. But it is not hypothetical: I reproduced it against a faithful reconstruction of
FEAT-46's actual `T-23.verify` field (see Evidence) — the exact field the shared contract names
as the decisive real-world case, and it renders into a wall of doubled single-quotes
(`''.harness/…''`) for every embedded `'`.

**Positive findings.** `--help` at both levels is concrete and complete — every flag names what
it holds and, where relevant, the recovery action (`--expect-sha256`: "the sha256 --show
reported; a replace is refused without it"). `amend` registers correctly and appears in the
top-level `--help` subcommand list beside its four siblings. The exit-3 (unknown id) and exit-4
(no such field) refusals both name concrete, real data — the actual ids present, a stated design
reason for refusing to grow the schema — never a placeholder. `--key approval` is refused with
the exact alternative route named (`sign-approval`) and the citing decision (DEC-120).

## Evidence (item 6's decisive experiment)

The dispatch's cited path, `.harness/harness/features/FEAT-46-*/plan.yaml` in the **main**
checkout, **does not exist** — `find .harness -iname 'FEAT-46*'` is empty there. FEAT-46 lives
in its own worktree,
`.claude/worktrees/harness/FEAT-46-decision-standard/.harness/harness/features/FEAT-46-decision-standard/plan.yaml`
(confirmed via `git log --all --oneline | grep FEAT-46` and a direct `find`). Flagging as an
open question — the dispatch's path claim was wrong, not the underlying instruction.

I built a faithful `/tmp` fixture (`/tmp/uirev-feat46/…/plan.yaml`) using the **exact, real**
`D-01`..`D-15`, `T-01`, `T-23`, `T-08` blocks copied byte-for-byte from that real file (not a
synthetic approximation) and ran the amend binary from the worktree against it:

- `--show` against `D-05.because`, `D-14.because`, `T-23.verify` all matched the build's claim
  — correct field, correct sha256, complete output.
- **The real REPLACE nobody had run:** `amend --key tasks --id T-23 --field verify` with the
  correct pre-read hash. Result: `AMENDED tasks:T-23.verify`, exit 0. Semantic check via
  `yaml.safe_load`: new value matches byte-for-byte (F3's "content held" claim). Sibling checks:
  `T-01.verify`, `T-08.verify` (which sits right after T-23 and whose `depends_on:` line
  contains the literal substring `T-23`) were untouched — `_item_range`'s `- id:`-anchored regex
  did not confuse that substring with an item boundary. `D-05.because`/`D-14.because` untouched.
  This is real evidence for item 3's bounding question, though only over this reconstructed
  subset, not the full 2491-line file (see Open Questions).
- The **real** FEAT-46 worktree file was never touched — `git status --porcelain` on it is
  empty after this review. Item 7's "not half-applied" holds: nothing from FEAT-46's eight
  staged blocks was applied anywhere, including by this review's own probing.

## Open questions

- Q1 (non-blocking): does `CodeRev` want to run `_field_block`'s bounding sweep against the
  FULL real FEAT-46 plan.yaml (2491 lines, ~30 tasks/decisions) rather than my reconstructed
  9-item subset? My subset found no mis-binding, but item 3's specific worry — an `intent: |`
  body containing a colon-prefixed line that could be mistaken for a sibling key — is only
  disproven for the blocks I copied, not the ones I trimmed out.
- Q2 (non-blocking): the dispatch's cited main-checkout path for FEAT-46's plan.yaml does not
  exist; FEAT-46 is a separate worktree. Worth fixing in future dispatches so the next reviewer
  doesn't lose a cycle re-discovering this.

## Files touched
None in the reviewed worktree — read-only. Scratch fixtures live under `/tmp/uirev-bug1128/`
and `/tmp/uirev-feat46/`, outside any tracked tree.
