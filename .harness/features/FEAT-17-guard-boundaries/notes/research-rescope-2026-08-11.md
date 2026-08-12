# Re-scope — FEAT-17 — the rooted case is refused as a MISTAKE, not as a hole — 2026-08-11

**Path note.** The dispatch named `notes/rescope-2026-08-11.md`; `check-domain.sh` denied it at
exit 2 — `harness-pm`'s per-feature grant is `notes/research-*.md`. Guard wins (#216), so this is
that artifact under the granted name.

## BLUF

The plan is amended in place and still signature-ready; both approvals read `pending`. One thing was
CUT — REQ-02's no-PyYAML clause and the module-level hoist it existed to pin — and the root-side rule
itself SURVIVES, on new grounds. The task set did not move: still 7 tasks, 9 REQ, 10 SC, 15 literal
`files:` entries over an 11-path union. Decisions went 8 → 9: **D-09** records the chosen
bootstrap-grant divergence, reversible at signature.

## Counts, with the command each was counted by

| Figure | Command | Answers |
|---|---|---|
| 15 literal `files:` entries, 11-path union | `load_plan(...)`, then `len([f for t in p['tasks'] for f in t.get('files',[])])` and `len(set(...))` | handoff Trust "15 literal paths"; `BRIEF.md` "union of 11" |
| 9 REQ / 10 SC | `grep -c '^- REQ-' BRIEF.md` / `grep -c '^- SC-' BRIEF.md` | handoff Trust "9 REQ and 10 SC" |
| 9 decisions, 7 tasks | `load_plan(...)`, `[d['id'] for d in p['decisions']]` / `p['tasks']` | was 8 decisions |

**FEAT-16 intersection: the union did NOT change — 11 paths, same 11.** Re-measured anyway because
FEAT-16 is live: its union now reads 17 (was 18 in the BRIEF's snapshot), and the intersection is
still exactly 3 — `test-check-domain.py`, `DECISIONS.md`, `DECISIONS-INDEX.md`. `BRIEF.md`'s
collision paragraph is updated to the 17 figure.

## The call on the hoist — CUT, reversible at signature

T-02's root-side check moves from module level (above `check-domain.sh:675`, independent of
`_no_parser`) to the START of `domain_check`. Grounds, from `plan.yaml:296-304`'s own text: the
module-level placement was justified on TWO separable things, and only the parser-contingent one
died. A check inside `domain_check` runs normally with the parser present.

Why cutting is safe: under the bootstrap grant the domain check is skipped in the REAL checkout too,
so the grant opens the same escape everywhere; and the TARGET-SIDE #103 refusal is already
parser-contingent on the Write route, because it is wired into `classify` and only `domain_check`
calls `classify` (`plan.yaml:282-288`). Matching the root-side check to it is consistent with what
this plan had already accepted.

**The consequence is recorded in four places, not hidden.** In a bootstrap-grant session the two
routes now diverge: Write does not apply the root-side check, Bash does. It is written as **D-09** in
`plan.yaml`'s `decisions:` — the operator's signature surface, and the reversible-at-signature record
— plus `BRIEF.md`'s `## What the root-side rule deliberately does NOT cover` for the human read,
T-02's intent for the doer, and T-07's "what did NOT converge" list for the DECISIONS entry. The Bash
route is NOT weakened to match.

## Cut / kept

| | |
|---|---|
| CUT | T-02's bootstrap-grant pair; T-03's bootstrap-grant pair; SC-03's parser-missing cluster; REQ-02's bootstrap clause; both placement rationales that rested on them |
| KEPT, new grounds | The root-side RULE — refuses the LOCATION on the standing "a stray worktree is a MISTAKE" ruling and the lost-work risk, never on FEAT-09 |
| KEPT, unchanged grounds | SC-03's wording assertions (`git worktree remove` from inside the tree deletes its own cwd — measured); SC-06's mutation proof; T-03's `git status --porcelain` case |

REQ-02 is **rewritten**, not re-justified. Old clause (b) "instead of being governed as though it
were the main checkout" is FALSE at `a29ad06` and is gone. New breadth: writes that are **in-domain
relative to the stray root's OWN manifest** are refused. Both-routes rests on **SC-06** (the mutation
must flip on both or a second copy exists), not on REQ-05 — REQ-05 commits to one implementation,
not identical verdicts, and after this cut the routes visibly diverge on parser-absent.

## Un-mutated refusal of the root-side rule, per route

**SC-03 only, on both routes** — Write: `<sibling>/.harness/allowed/x.txt` with `CLAUDE_PROJECT_DIR`
at the sibling, exit 2. Bash: `echo hi > <sibling>/.harness/allowed/x.txt`, same root, exit 2. SC-03
now says so in its own text, so a later cut cannot remove it silently. SC-06 is a mutation criterion
and cannot stand in for it.

## Superseded

`handoff-plan.md` Trust line **"FIX 1 LANDED: T-02's intent names the insertion point as module level
inside `if _run_domain:`, above line 675 and independent of `_no_parser`"** is **SUPERSEDED by this
re-scope.** It was true at `a29ad06`; the hoist it verified is deliberately gone. Every other Trust
line stands.

`.harness/notes/grilling-guard-boundaries-2026-08-11.md` is untouched by design; the re-measurement
is cited from `notes/answers-2026-08-11-rescope.md` directly.

## Gates, at the amended files

- `python3 .claude/skills/harness/bin/check-plan-routes.py .harness/features/FEAT-17-guard-boundaries/plan.yaml`
  → `0 violation(s) across 1 plan(s)`, exit 0. DEVIATION on T-01..T-06, OK on T-07.
- `harness_yaml.load_plan(<plan>)` → real dict, keys `schema feature approval lanes decisions tasks`,
  7 tasks, 9 decisions (`D-01`..`D-09`), `approval {'status': 'pending', 'approved_by': 'none',
  'date': 'none'}`. Ran after the final edit, not asserted.
- `check-domain.sh --resolve` on all 11 union paths: each resolves, each matches its declared lane.

## AMENDMENT — REQ-02 and the Goal scoped to a parser-present session (same day)

**One shape was left behind by the cut and is now closed: REQ-02 committed to a both-routes refusal
with no scope, while D-09 and `## What the root-side rule deliberately does NOT cover` record that
under the PyYAML bootstrap grant the Write route does NOT apply the root-side check and the Bash
route does.** A reader opening REQ-02 alone got a commitment the build will not meet — a requirement
falsified in place, the DEC-188 shape this re-scope existed to remove. Only `BRIEF.md` changed;
`plan.yaml` was NOT touched, so `check-plan-routes.py` and `load_plan` were not re-run (the dispatch
conditioned both on a `plan.yaml` edit). No bullet was added or removed: `^- REQ-` = 9, `^- SC-` = 10,
re-counted from the file after the edit. `BRIEF.md` `status: pending` (line 305) and `plan.yaml`
`approval.status: pending` both still read pending.

Three sites changed, all inline in existing prose:

1. **REQ-02's head clause** now reads "on both write routes **in a parser-present session.** That
   scope is chosen and recorded, not an omission: under the PyYAML bootstrap grant the Bash route
   still refuses and the Write route does not, for the reasons set out below under
   `## What the root-side rule deliberately does NOT cover`." Cited by HEADING, not by line range —
   `BRIEF.md` is rewritten often and the range would rot (P-10).
2. **REQ-02's trailing sentence**, which also committed unqualified: "The refusal is required on both
   routes — **within that same parser-present scope** — because SC-06's mutation proof…". Both sites
   in one edit, or the contradiction survives inside a single REQ (G-13).
3. **`## Goal`**: the third clause only — "and — in a parser-present session, the scope recorded
   under `## What the root-side rule deliberately does NOT cover` — cannot host a session that thinks
   it is the main tree". The one-shared-implementation clause is REQ-05, untouched by the cut and
   deliberately NOT weakened.

**Deliberately left alone, with the check that settled it.** REQ-01/REQ-04/REQ-06 also go dark under
the bootstrap grant, but on BOTH routes together, so that is a document-level precondition of the
sanctioned escape rather than a route asymmetry this feature chose. The discriminator, read at
`a29ad06`: T-03 places the Bash ROOT-side check above `bash-write-guard.sh`'s own `_no_parser` exit
(near line 340) while the TARGET-side `classify` call sits in the findings loop below it — so the
root-side rule survives the escape on Bash and the target-side rule does not. Scoping those three
would have re-broadened the document with a qualifier none of them needs. REQ-03 is single-route by
its own wording. REQ-09's fail-closed import sits at `bash-write-guard.sh:73`, above `_no_parser`,
and on the Write route is gated on `_run_domain` rather than on the parser, so it is unaffected.

**Flagged, not fixed — needs the operator's call.** `## What the root-side rule deliberately does NOT
cover` cites `check-domain.sh:676` for `if _run_domain and not _no_parser`; at `a29ad06` that line is
**675** (`sed -n '673,678p'`). T-02's intent carries the same `676`. The dispatch forbade touching
that section, and a line-anchor edit is still an edit there. One character, or better a re-anchor on
the condition text.

**The two `676` sites are NOT the same call.** `BRIEF.md`'s section is off-limits by dispatch — an
operator decision. T-02's intent is MINE to fix and is deferred only because editing `plan.yaml`
would re-arm `check-plan-routes.py` and `load_plan`, both scoped out of this amendment. It matters
more there: the intent is the literal dispatch prompt, and it hands the doer two anchors one line
apart for the same line ("called at line 676" beside "do not hoist above line 675"). One edit plus
two gate re-runs, on the operator's word.

## Open for the operator

Both non-blocking; the plan ships on ONE call, reversible at signature.

- **Q1 — does SC-03's no-PyYAML half become its own criterion?** MOOTED by this cut. There is no
  no-PyYAML half left to split.
- **Q2 — does SC-03 survive?** YES, narrowed. Removing it would leave only SC-06 asserting the
  root-side rule, and SC-06 proves one-implementation, not correct refusal.
