# FEAT-14 — feature.json with an enforced schema — ship review

**Recommendation: SHIPPABLE once you spend ~9 minutes on three checks only you can do.** Every
blocking defect is fixed and confirmed closed **by execution**, not by reading. `must_fix` is empty
and `severity_max` is `med`, so by the standing definition this is no longer critical. What remains
is your inspection of SC-10, SC-11 and SC-15, and a backlog you can strike by ID.

## What changed since the last draft of this document

Three of the four fixes landed and were independently confirmed. I re-ran every proof myself rather
than accepting a report, because the confirming lead holds no shell.

| Fix | State |
|---|---|
| Schema gate failed open (`check-domain.sh`) | **CLOSED** — `0b33188`, main session, DEC-174 carve-out |
| Gate had no standing test | **CLOSED** — same commit, four fixtures |
| `gh-sync.py` could re-file GitHub issues | **CLOSED** — `1c5fd67`, ordinary fix cycle |
| B-5 (reader convergence), B-14 (grep) | landed / answered |

## The evidence, measured rather than asserted

**The schema gate now denies when its own checker breaks.** Same syntax-broken `feature_schema.py`,
same illegal payload, only the handler differs:

| | Result |
|---|---|
| Before (`c9cd6bb`) | **exit 1**, raw traceback — exit 1 is non-blocking, so the bad write lands |
| After (`0b33188`) | **exit 2**, message naming the crash and distinguishing it from a missing dependency |

The new fixtures discriminate: run against the pre-fix handler, **exactly one** case fails — "a
CRASHING schema module DENIES the write". All three routes (Write-pre, Write/Edit-post, Bash sweep)
converge on one function, and the message dedup suppresses redundant *text* for files 2..N but never
the exit-2 *outcome* — the caller accumulates and decides once, with no per-file exit path.

**`gh-sync.py` can no longer re-file issues.** Crashing the write at `os.fsync` and at `os.replace`
both leave `feature.json` **byte-identical with no temp residue**. Six reader states behave
correctly — absent and no-`github`-key both proceed (first sync intact, the regression this fix could
most easily have caused), while zero-byte, non-mapping and a non-mapping `github` all refuse loudly.
Post-fix tests against pre-fix source fail **exactly 6** assertions, all of them the new ones.

## The one nuance worth your attention

**A green suite here is load-bearing for the hazard and not for the reader.** Swap the reader back to
YAML and the suite stays **74/74 green** — B-5's contract is unpinned — but a zero-byte file *still*
refuses, via a second guard. Two independent guards close the irreversible outcome and the mutant
removes only one. So the gap is real and it is **laxity, not the external damage** that made this
HIGH. That is why it is advisory (B-17) rather than a gate, and I verified both halves myself.

## What only you can do (~9 minutes)

- **SC-10** (5 min) — open `FEAT-11-graphql-field-resolve/notes/receipt-feature-key-drop.md`. pm swept
  all 17 pre/post: zero unrecorded drops, 17 receipts, none left over. *BRIEF's parenthetical is
  wrong twice — FEAT-11 lost 22 keys not 20, and FEAT-12/13 each lost 23.*
- **SC-11** (2 min) — pm recommends MET. Residual: `factory.issues` / `factory.items` are bare
  `{type: object}` (`feature-schema.json:96-97`) where sibling `github.issues` constrains to integer.
- **SC-15** (2 min) — script at `notes/uat-FEAT-14-sc15-readability.md`. *No corpus file carries
  eleven keys; `factory` is in zero of 17, so ten is the real maximum.*

**12 of 18 met, 3 now closed by the fixes above, 3 yours.** No agent may mark the last three met.

## The finding worth more than the feature

**All eight plan defects lived in a `verify:` clause, and every one was writable because the clause
was authored as prose and never executed against the tree before signature.** Two shapes:
*non-discriminating* — already satisfied before the change it existed to prove — and
*self-contradicting* — the `verify` forbids a literal the same task's own `intent` tells the doer to
write. The remedy lands in `check-plan-routes.py`, which already runs at plan time and is **not** a
carve-out: record `verify_red_at` and fail any verify already green at signature, plus grep every
literal a verify forbids against that task's own intent. **The grep half needs no runner and catches
three of the eight alone.**

This feature produced **seven** instances of the assertion-that-cannot-fail class. That is the
pattern, not seven accidents.

## Proposed backlog

| ID | Finding | Nature |
|---|---|---|
| ~~B-1~~ | **FIXED** at `1c5fd67` — `gh-sync.py` truncate-at-open + empty-record read | — |
| B-2 | Plan-time `verify:` clause checker — red-before-signature + intent cross-grep | enhancement |
| B-3 | SC-14's index check is blind to a corrupted **ruling clause**: prose round-trips verbatim | bug |
| B-4 | `tests.yml`'s `Unit suite` step is the only runner for eight criteria and nothing asserts it; the `case 25` guard its comment claims does not exist (inherited, `eafc8ad`) | bug |
| ~~B-5~~ | **LANDED** with the fix — reader converged on `json.load` | — |
| B-6 | `factory.issues` / `factory.items` unconstrained where `github.issues` is integer-typed | chore |
| B-7 | Three stale BRIEF lines: `:421` "exits 1 today" (exits 0), SC-13's "exactly two carve-outs" (five), SC-10's key counts | chore |
| B-8 | SC-02 has no failing fixture for `factory` / `factory.edges` | chore |
| B-9 | `harness.json`'s integration `detect` glob names 2 of the 12 scripts its `cmd` runs | chore |
| B-10 | Write guard denies paths containing an unexpanded shell variable. **It bit me four times** | bug |
| B-11 | Citation drift — two edits: `plan.yaml:158` D-04 → DEC-190, `:261` D-08 → DEC-191 | chore |
| B-12 | `check-plan-routes.py:558` says FEAT-08 "is `awaiting_user`"; it reads `Review` | chore |
| B-13 | Interrupting a lead does not stop its children (DEC-131). Fired **three times** | bug |
| ~~B-14~~ | **ANSWERED** — `case_24` already has the discriminating shape; nothing built | — |
| B-15 | `write_factory` starts from `doc = {}` and can write a document missing required keys | bug |
| B-16 | Reviewers cannot falsify enforcement-path findings — the write guard denies them fixture creation. Splitting probing to qa is what fixed it this round | enhancement |
| B-17 | B-5's reader contract is unpinned: a yaml-swap mutant leaves the suite 74/74 green. Add the inverse comment-bearing fixture | bug |
| B-18 | `save_recorded`'s `doc = {}` on the absent-file path could write a schema-invalid document. **Reachability unknown — do not fix before answering it** | chore |
| B-19 | The schema-gate fix is test-verified on the Write route only; the `ImportError` branch and the crash-vs-import message distinction are unexercised. **Main session — carve-out** | bug |
| B-20 | **Introduced by the fix at `1c5fd67`**: `feature.json`'s mode narrows `0644` → `0600` on every `save_recorded`, because `os.replace` carries the `mkstemp` source's bits where the old `open(p,"w")` preserved the file's. Measured both sides. `write_factory` shares the shape, so the pattern is pre-existing, but this file's behaviour changed here. No `chmod` restore, no test asserts mode | bug |
| B-21 | `fix1`'s message predicates are decorative (`len(str(e)) > 0`; four-way ORs every message satisfies). The branch property they bind is real | chore |

## How this briefing was assembled

**No report round was spawned** — digests read from disk (DEC-69), all 22 runs' `digest.md` under
`.harness/features/FEAT-14-feature-json-schema/runs/`.

**Everything above I re-verified with my own commands**: the exit-1→exit-2 counterfactual in a
throwaway worktree; exactly one fixture failing pre-fix; six `fix1` failures and zero others;
byte-identity after crashes at `os.fsync` and `os.replace`; the six reader states; and the yaml-swap
mutant surviving while the hazard stays closed.

**One error of my own, recorded:** my first atomicity probe patched `json.dump` while the code calls
`json.dumps`, so no crash was injected and I briefly read a normal successful write as a failure. The
instrument was wrong, not the code. Re-probed at the real crash points.

**Three runs were interrupted and every one ran on anyway (B-13)** — one left a live mutant in a
shipped document, which I restored and byte-verified; another returned 40 minutes after its own
digest with the stronger version of the `gh-sync` finding this briefing now carries.

**Budget: 6 of 10 cycles, 21 runs against an informational 20 — over the bound.** My read: the
overrun is earned. Three runs went to interruptions rather than rework, and the last two produced the
fix and its execution-backed confirmation. Two cycles were traceable send-backs. Nothing here
suggests sprawl, and the counter is reported, never enforced.

**Housekeeping:** twelve sub-issues `#264`–`#275` closed on the mirror and verified; all probe
worktrees removed.
