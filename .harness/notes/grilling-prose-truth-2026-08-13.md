# Grilling — prose truth has no gate (issue #247) — 2026-08-13

## Destination

A claim of the `only`/`never`/`all`/`no` shape in `BRIEF.md` or `plan.yaml` carries the runnable
command that proves it, and `check-state.sh` fails when one does not. The rule buys **one shape of
falsehood, not truth** — that limit is accepted, not overlooked.

## Settled

- **What reaching the end looks like** → citation, chosen because it leaves an artifact. "Do not
  write fiction" asks for a state of mind and nothing can observe whether it was obeyed. "Show the
  command that proves this" asks for an output, and its absence is visible. That is the only reason
  one of them is a mechanism.
- **Can precise instructions solve this instead?** → No. The instruction was already live and the
  agent already held the disproof. See `## Facts` items 1 and 2. Adding instruction text targets
  neither failure.
- **Complete coverage of arbitrary prose is not reachable** → deciding whether a sentence is true
  requires already knowing the fact, which is the original problem restated. Every candidate was a
  proxy. The operator named this and the framing was corrected rather than defended.
- **Scope** → `BRIEF.md` and `plan.yaml` only. Two of the three FEAT-12 falsehoods were born in
  `BRIEF.md`; the third entered through an approved plan `intent:`. Source docstrings, `docs/` and
  review notes are OUT for now — see `## Out of scope`.
- **What a citation is** → a runnable command in backticks. Not a `file:line`, which cannot be
  re-run and goes stale silently when lines move.
- **Where it is enforced** → a new invariant in `check-state.sh`, alongside the other 26, so one
  place reports everything.
- **The carve-out cost was named before the choice, and taken anyway** → `check-state.sh` is a
  DEC-174 carve-out. This invariant is main-session-direct: ordinary edits, tests run explicitly, a
  human reading the diff. It can never be dispatched to a team run, because the gates such a run
  would pass are the thing being changed.
- **Generation was considered and dropped** → the operator first chose "generate the sentences that
  describe the code". It was withdrawn after `## Facts` item 4 showed the sole precedent is
  unenforced. That is not a rejection of generation; it is a refusal to build on an example that has
  never actually held.
- **Enforcement is a requirement, not a question** → whatever is built, a mechanism nobody runs is a
  guarantee only while someone remembers.
- **The live falsehood is fixed after FEAT-18 merges** → `factory_config.py:1`, see `## Facts` item 3.
  Kept out of the FEAT-18 branch, which must stay source-clean since its pin.

## Not yet specified

- The exemption path for prose that quotes a historical absolute on purpose. `DECISIONS.md` and the
  struck-decision records are full of them, and `BRIEF.md` can legitimately quote a prior ruling.
  Exemption paths are also how gates rot, so the shape of this one decides whether the invariant
  survives a year.
- Which words trigger the rule. `only`/`never`/`all`/`no` is a starting guess taken from the three
  FEAT-12 instances, not a measurement over the live corpus.
- What the invariant does about a claim that IS false but carries no absolute — "`factory_config.py`
  reads the fleet declaration" is falsifiable and passes clean. The gap is known and unaddressed.
- Whether a citation is only checked for presence, or eventually re-run. Presence is cheap and
  weak; re-running is the real guarantee and a much larger build.

## Out of scope

- **Source docstrings and comments** — where the surviving falsehood actually lives. Ruled out of
  this effort to keep the first invariant narrow. `factory_config.py:1` is fixed by hand instead.
- **`docs/` and review notes** — largest volume and the most quoted history to exempt. Revisit once
  the exemption path is settled.
- **A truth-focused review role** — the only option with a demonstrated hit rate, since a reader
  caught all three FEAT-12 falsehoods. Not chosen, because it depends on attention rather than
  producing an artifact.
- **A plan-time-only gate** — measured to catch one of three. Subsumed by the chosen scope, which
  covers `plan.yaml` anyway.
- **Re-opening DEC-188's ruling** that a contradicted decision is struck rather than marked. The
  citation rule sits beside it and does not disturb it.

## Facts I verified (so pm does not re-derive them)

1. **The instruction already exists and did not work.** `CLAUDE.md:74` reads "Every claim in prose
   that a command can check gets checked before it is written." `harness-principles` carries "an
   honest record" and is preloaded into all 16 agents at every spawn. All three FEAT-12 falsehoods
   were written with both live. At `6303683`.
2. **The agent was not ignorant.** `runs/t12-product/digest.md:42-49` records that the member proved
   in its own Q1 that `factory_config.py` is not the only reader, wrote the true narrower claim into
   `SPEC.md`, and then wrote the false stronger form into `README.md:79`. Same agent, same run,
   correct fact in hand, both sentences authored. **`notes/research-FEAT-12-distill-pm.md:58` says
   the member "refused" — that account is wrong and the digest is the one to trust.**
3. **The original falsehood is still in the tree.** `factory_config.py:1` reads "the only reader of
   `.harness/factory/fleet.yaml` (SC-08)". `git grep -ln "fleet.yaml"` over
   `.claude/skills/harness/bin` returns six non-test readers, including `check-state.sh`,
   `factory_decompose.py`, `factory_land.py`, `factory_workspace.py` and `harness_boundary.py`.
   FEAT-12's code reviewer flagged this exact docstring. `README.md` was fixed and the docstring was
   not.
4. **The one generation precedent is unenforced.** `gen-decisions-index.py` writes all of
   `DECISIONS-INDEX.md` in place, with no markers and no partial regions. `git grep -ln
   "gen-decisions-index"` over `.claude` and `.harness/harness.json` finds only the script, its own
   test, and the test runner. No `check-state.sh` invariant, no `harness.json` entry. The index can
   drift while every gate stays green — the unclosed residue of issue #148.
5. **`check-docs.sh` is deleted, not disabled.** Commit `835b297`, struck under DEC-188 with DEC-103
   and DEC-104; INV-10's number is retired. There is nothing to build on and nothing to restore.
6. **The last invariant number in use is INV-26**, added by FEAT-18. A new one takes INV-27.
7. **`.harness/codebase/glossary.md` does not exist**, so "the tree" — used throughout `CLAUDE.md`
   and `DECISIONS.md` — has no definition anywhere in the project. `check-state.sh` INV-19 exists to
   require a glossary once a codebase is mapped.

## Note on how this grilling went

The operator rejected three question rounds and redirected twice. Both redirections were correct and
both changed the destination: the first named that every option on the table was a probability
rather than a fix, and the second asked whether instructions would do the job — which forced the
check that produced facts 1 and 2 and settled the whole question.

**One error of mine belongs in the record.** I recommended generation on the strength of
`DECISIONS-INDEX.md` and said a generated sentence cannot be false. That claim was unbacked; I had
not checked enforcement. It is an unqualified "cannot", stated without the command that would prove
it — the exact shape of the three falsehoods this effort exists to stop, committed while designing
the fix for them. Fact 4 is what the check returned.
