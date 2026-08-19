# FEAT-24 — the config responsibility split. Ship decision.

## The recommendation

**Ship it, and take two rulings.** The feature does what it was built to do: pm's goal-check found
**no success criterion broken in the code**. Every board now lives in its own repository, one shared
validator raises on every malformed shape, and an unusable board is a loud, named error instead of a
silent nothing. I confirmed the central path live rather than from the suite: `board_for` returns
kaya's board, read from `master`, with a checkout sitting on disk unused.

What is *not* finished is **evidence durability**. Five of thirteen criteria rest partly on
assertions that provably cannot fail. That is a real gap and it is the same gap this feature exists
to close — one level up, in the tests rather than the code.

## Criterion status — pm's goal-check, all thirteen

**7 met · 5 partial · 1 split.** Partial always means *behaviour met, evidence weak* — never broken.

| | |
|---|---|
| **Met** | SC-02 (five keys, all five mutants run by pm at HEAD), SC-03, SC-04 (16/16 cells), SC-08, SC-09 (pm's own live `gh api` read), SC-11, SC-12 |
| **Partial** | SC-01 · SC-05 · SC-06 · SC-07 · SC-10 |
| **Split** | SC-13 — clause 1 met (28/28 scripts, none removed); clause 2 requires the suite green **at the merge commit** and nothing pre-merge can clear it |

The partials, concretely: SC-01's "declares only four keys" is true by reading but pinned by nothing
— appending a fifth key to `fleet.yaml` reddens zero tests. SC-07 has 1 of 3 consumers
discriminating, because `DEFAULT_BRANCH` is `"main"` in all three test files, so a hardcoded `"main"`
is invisible. SC-10 is 11 of 12. SC-06's behaviour is met on all three named failure modes, but
`gh` unauthenticated shares one code branch with missing-file and no committed test names it.

## Two rulings only you can make

**1. SC-05's scope — and I measured the thing that prices it.** The clause reads "an explicit null
is accepted, writes no station, and **is the only non-error path**". The product lead named an unrun
check that would settle it, so I ran it rather than sending you a question a measurement could close.

`gh_board.load_board` has **six** non-error paths, and **five** of them mean "no board":

| shape | outcome |
|---|---|
| a valid board declared | returns the board |
| **explicit `null` board** | returns `None` — the declared no-board path |
| `github` present, no `board` key | **RAISES** — the only cell that does |
| no `github` key at all | returns `None` |
| `github` not a mapping | returns `None` |
| the whole file not a mapping | returns `None` |
| the file absent or unparseable | returns `None` |

So "the only non-error path" is false by a factor of five, not by one — and the one-line fix
discussed earlier would have closed exactly one of the four extra cells. Note the last row is
arguably *correct*: a project with no `harness.json` genuinely has no board. That is why this is a
design ruling and not a mechanical fix. Three ways to close it: re-scope the clause to "the only
**declared** no-board path", which is true today; make the middle three cells raise and leave
file-absent alone; or strike the clause. **pm's reading is that SC-05 is met 4/4 under the narrow
domain SC-04 and REQ-09 already use** — the tidiest answer, and pm declined to simply endorse it,
which I think is right.

**2. Whether to pin the unpinned cases.** Five cases now guard real defects — the two `file_at_ref`
bugs and the two `product_config` parse branches — and **no `verify:` block references any of them**,
so deleting them would be invisible to every gate. Fixing that edits an approved `verify:` after
signature, which is pm's and yours, not mine.

## A correction against myself, on the record

I reported that `gh_board.load_board` returns `None` for three cells and used it to argue SC-05 was
unsatisfiable. **It was a broken measurement:** `load_board` takes a repository *root* and I passed
it a file path, so every `None` I saw was the file-not-found branch, not the cell I claimed to test.
Measured correctly, a `github` block with no `board` key **raises**. pm's probe was right and mine
was wrong, and I had already carried the bad reading into two dispatches. The lesson is narrower than
"check your work": I verified the value returned and never verified that the *call shape* was the one
the function takes. A probe that exercises the wrong branch returns a real value and looks exactly
like evidence.

## What this feature cost, and whether it earned it

**Cycles 9 of 10** (rework only) — **one left**. Any further fix loop exhausts the budget, and exhaustion is a hard stop I must report as BLOCKED rather than push through. That is the strongest practical argument for taking the two rulings and shipping rather than opening another repair round. **Runs 21 against an informational budget of 20** — crossed, and
reported rather than apologised for. My read: they earned their place. The last eight runs each
closed something real — a criterion whose assertion could not fail, two live integration defects, a
gate slicing on markers that did not exist, an error message directing an operator to a destination
the same change deleted. Two leads escalated believing the run budget was a hard stop; it is
informational, and `max_total_cycles` is the counter with teeth.

**Two defects shipped past a 208-check green suite** before being caught, both in one function, both
invisible because the fake `gh` models argv but neither the HTTP method nor the real response shape.
That is the single most important thing this feature learned, and B-5 below is where it goes.

## How this briefing was assembled

**No report round was spawned.** It is drawn from the digests already on disk, each cited by path
under `runs/<id>/digest.md`: `2026-08-18-1-product`, `-1-eng`, `-2-product`, `-1-validator`,
`-2-eng`, `-3-product`, `-4-eng`, `-5-eng`, `-6-eng`, `-7-eng`, `2026-08-19-1-eng`, `-2-product`,
`-3-validator`, `-4-eng`, `-3-product`, `-5-validator`, `-7-eng`, `-8-eng`, `-9-validator`,
`-10-eng`, `-11-product`; plus `notes/qa-2026-08-19-matrix-gate.md`,
`notes/qa-2026-08-19-matrix-recheck.md`, the three `notes/review-harness-*-c0.md` reviewer artifacts,
and `notes/research-FEAT-24-goalcheck.md`. Ship-refresh was **skipped**: there is no map
(`INDEX.md`) in this repository, so nothing could go stale.

## Proposed backlog — none of these gate the ship

| ID | Item | Nature |
|---|---|---|
| B-1 | SC-01's "declares only four keys" is pinned by nothing — a fifth key in `fleet.yaml` reddens zero tests | chore |
| B-2 | SC-07: `factory_land` and `factory_workspace` `default_branch` assertions cannot fail; `DEFAULT_BRANCH` is `"main"` in all three fixtures | chore |
| B-3 | SC-10: `factory_land.py:95` reverted to `"Review"` gives zero FAILs | chore |
| B-4 | SC-06: `gh` unauthenticated shares one branch with missing-file; no committed test names it | chore |
| B-5 | The fake `gh` models argv but neither the HTTP method nor the real response shape — it shipped two live defects past a green suite | bug |
| B-6 | Five cases guarding real defects are referenced by no `verify:` block, so deleting them is invisible to every gate | chore |
| B-7 | No case-level deletion guard exists: SC-13's instrument counts FILES, and this diff deleted two named assertions while the count stayed 28/28 | bug |
| B-8 | T-10's verify checks that record amendments EXIST and sit in the right section, never that they are TRUE — how a false entry shipped green | bug |
| B-9 | `harness.json`'s `integration.detect` names 4 files while `INTEGRATION_SCRIPTS` runs 12 | chore |
| B-10 | `gh_board.load_board`'s docstring is wrong about three cells that return `None`; every caller guards, so nothing fails today | chore |
| B-11 | The kaya-ai/board-2 pairing has no ongoing regression check after `case5` dropped two assertions | chore |
| B-12 | `factory_land.py` does not commit — T-09 failed with `No commits between master and factory/issue-334` until you committed by hand | bug |
| B-13 | `gh-sync.py` has no un-start subcommand, so an abandoned dispatch strands cards on `Building` | enhancement |
| B-14 | `feature.json`'s schema declares no `phase` property while the orchestrator playbook instructs recording one there | bug |
| B-15 | `validate-digest.py` rejects read-only members' `suite: n/a` / `task: none` | bug |
| B-16 | Leads returning a verdict while their member is still in flight — #461, several more sightings here | bug |
| B-17 | Two leads escalated believing `max_total_runs` is a hard gate; it is informational, and the doctrine is not reaching leads | chore |
| B-18 | `test-factory-land.py`'s `review` fixture has the non-discriminating shape SC-02's `ready` had | chore |
| B-19 | `plan.yaml:657-658`'s T-03 prose is stale after the `ready` fixture moved to `Promoted` | chore |
| B-20 | Reported by security, DEC-174 flag-only and unverified: `bash-write-guard.sh` blocks `cp`/`rm` for a read-only role but not an equivalent `python3 shutil` write | bug |
| B-21 | `validate_board` does not bind `board.owner` to the repository's own owner or a fleet allow-list | enhancement |
| B-22 | **The orchestrator cannot apply handed-up Expertise ops.** The playbook says write-less members return ops and the orchestrator applies them verbatim; `check-domain.sh --resolve` grants every `.harness/expertise/<agent>.md` to that agent ALONE. Ten ops from three reviewers and two leads are unappliable by anyone who received them | bug |
| B-23 | Write-less reviewers cannot run `check-expertise.sh` — the guard blocks even a scratch write — so the one role that must hand ops up unapplied is the one that cannot validate them | bug |
| B-24 | The repository-tier Expertise path the distill skill describes is granted to nobody and does not exist; several durable repo-specific facts were judged, written nowhere, and reported | chore |
| B-25 | pm returned `expertise_full`: a durable uncovered rule was dropped on the Gotchas cap alone, not on merit. Raise that file's cap or record the loss as a cap decision | chore |
| B-26 | Two of four validator-squad members have never written an observations log, so their distillations reconstruct craft from review artifacts written for another purpose | chore |

## Also yours, and not FEAT-24's

The paused `FEAT-25`, `FEAT-26` and `FEAT-27` directories account for every remaining
`check-state.sh` violation. **FEAT-24 itself reports zero.** I have not touched them.

## What ships

Fourteen commits on `feat/FEAT-24-config-responsibility-split`, tip `2359f4f`, `review_sha` pinned at
`91884f9`. Full suite green, zero FAIL lines. No PR is open and nothing is merged — that is yours.
