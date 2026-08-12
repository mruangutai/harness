# Goal-check — FEAT-14 feature.json schema — at `cf15660`, branch `feat/204-feature-json-schema`

**BLUF. The goal is substantially met and the feature is NOT shippable yet.** **12 of 18** criteria
are met in their declared mode (SC-01, 02, 03, 06, 07, 08, 09, 12, 13, 14, 17, 18);
**SC-04, SC-05 and SC-16 are `unmet`** — they declare `verify: automated`
and no automated assertion exists anywhere, so the write-time schema gate this feature exists to add
is **true today and protected never**; **SC-10, SC-11 and SC-15 await the operator** (one of them,
SC-11, with a residual I found). REQ coverage is complete: all nine REQs are cited by `traces:` in
`plan.yaml`; nothing was dropped.

I did not re-run qa's suites. Where a judgment of mine turned on qa's evidence I opened the cited
artifact; where qa's evidence class could not reach — the three inspection/uat criteria — I did the
legwork myself and it is recorded below.

## The three unmet criteria — carried, not attempted

SC-04, SC-05 and SC-16 rest entirely on one-off live probes recorded in
`notes/qa-final-coverage.md` §Phase 2. `test-check-domain.py` carries **zero** schema-rejection
fixtures. The remedy lands in `check-domain.sh`'s test file, a DEC-174 carve-out surface, so it is
the main session's — **not a fix cycle's**. I confirmed the classification and did not touch it.

The sharpest thing in qa's artifact is not the gap but the reason nobody saw it: BRIEF
§Verification gaps lines 513-516 **asserts** that SC-04/05/16's assertions "live in
`test-check-state.py` and `test-check-domain.py`". That sentence is measurably false, and it is the
sentence a reader would use to decide the coverage question. A brief that names where its coverage
lives is only as good as someone checking that it is there.

## SC-10 — I did the legwork; the operator answers yes/no

Both halves hold on my read. **First half, all 17 features, not just the spot-check one:** for every
feature I diffed the pre-migration `feature.yaml` at `acd5d2f^` against today's `feature.json` and
matched the dropped keys against that feature's `notes/receipt-feature-key-drop.md` — **zero dropped
keys unrecorded, zero value mismatches** across the corpus, with `phase`, the old `status` and the
`pr: 'none' -> null` normalization each recorded in the receipt prose. **Second half:** 17
`feature.json`, 17 receipts, **none left over**.

The spot-check as SC-10 frames it, FEAT-11: 32 keys before, 10 after, **22 dropped** — 21 recorded
verbatim in the receipt's YAML block with byte-identical values, and the 22nd, `phase: ship`,
recorded in the receipt's status-collapse section. **SC-10's parenthetical is wrong on both numbers:
FEAT-11 lost 22, not 20, and it is not the feature that lost the most — FEAT-12 and FEAT-13 each lost
23.** That is a stale-BRIEF correction in the Q3 class, not a failure to meet the criterion.

## SC-11 — evidence assembled, and one residual only the operator can rule on

- **No `notes:` field, and no `notes` token at all**, anywhere in `bin/feature-schema.json` (grep,
  zero matches).
- `additionalProperties: false` at `/`, `/runs[]`, `/github`, `/factory`, `/factory/edges`.
- The rejection message names all four destinations from BRIEF's redirection table
  (`BRIEF.md:286-291`) verbatim in substance — `feature_schema.py:57-63`.

**The residual.** Three nodes are open string-keyed maps with no value constraint:
`factory.issues`, `factory.items`, `factory.edges.blocked_by` (each bare `{"type": "object"}`).
Their sibling `github.issues` is constrained to `{"type": "integer"}`. They are bookkeeping maps
whose keys are runtime ids and cannot be enumerated, so their openness is justified — **but they
would accept a prose string today**, which is the thing REQ-04 forbids. My recommendation:
**SC-11 met, with a one-line follow-up** — give `factory.issues` an integer value constraint
mirroring `github.issues`. Not a fix for this feature.

## SC-15 — script is written and ready

`notes/uat-FEAT-14-sc15-readability.md`. File named, pick justified, one question, one screen.
One thing surfaced writing it: **no file in the corpus carries eleven keys** — `factory` is present
in zero of seventeen, so ten is the maximum instance. SC-15's "eleven-key file" is a wording gap,
not a defect; SC-01 requires no key *outside* the eleven and that holds.

## Plan authorship — one judgment, not eight fixes

**Every one of the eight defects is in a `verify:` clause, and every one of them was writable only
because the clause was authored as prose and never executed against the tree before the plan was
signed.** Two failure shapes, one root:

- **Non-discriminating** — T-09's two dead assertions were already satisfied at authoring time (a
  regex matching a prose cross-reference at `SPEC.md:1604`; `'Building' not in d` already false via
  unrelated prose at `DECISIONS.md:1159`). Both would have passed *before* the change they existed
  to prove.
- **Self-contradicting** — T-05 item 5's fixture prohibition, T-09's rename, the T-02/T-04 pair.
  The `verify:` forbids or counts a literal that the **same task's own `intent:`** instructs the
  doer to write. Invisible on reading, because the author wrote both halves in one sitting.

**The check that would have caught all eight, and where it lives.** Not a review, not a rule —
`.claude/skills/harness/bin/check-plan-routes.py`. It already parses `plan.yaml`, already runs at
plan time, and is already the required `integration` CI context. **It is not a DEC-174 carve-out
file**, so unlike the SC-04/05/16 remedy this one is dispatchable. Two additions:

1. **Red-before.** Each task records `verify_red_at: <sha>` — the exit status of its own `verify:`
   against the tree at plan time. **A `verify:` that is already green when the plan is signed proves
   nothing and fails the check.** Cheap form (today, no runner): the pm runs it and records the sha
   and the exit code. Strong form (costs a sandboxed runner): the checker executes it.
2. **Intent cross-grep.** Every quoted literal a `verify:` forbids or counts is grepped against that
   same task's `intent:`. A hit is a contradiction and fails the check. Pure text, no execution, no
   runner — this half is nearly free and catches three of the eight on its own.

The honest cost: (1) is not universally applicable — a `verify:` depending on a file the task
creates cannot run at plan time. Those tasks declare `verify_red_at: not-runnable` **with a reason**,
which is itself the signal a reviewer should read.

## SPEC.md:1612 — **KEEP**

Before T-09 the passage told the orchestrator that a feature's `status` stays `in_progress` and is
**not** set to `abandoned`. DEC-192 rejects both literals — the six legal values are
`Backlog|Plan|Ready|Building|Review|Done`. Leaving it would have left the spec instructing an agent
to write two values its own new schema refuses. The rewritten line
(`docs/harness/SPEC.md:1612-1614`) preserves the meaning exactly — the orchestrator does not close a
feature out — while naming no illegal value.

**This is an unnamed-but-CORRECT change, and a different finding from an unnamed-and-wrong one.**
The defect is not the edit; it is that **T-09's intent enumerated files to sweep and not semantic
sites to correct**, so a required change arrived unrecorded and could just as easily have been
missed. Same root as the plan-authorship judgment above. Optional polish, not a revert: "shipped or
abandoned" survives as English in the new sentence and a fast reader could take it for field values.

## Q1/Q2/Q3 — product-side recommendations

- **Q1 — record as a known limit of SC-14; do not commission a prose-integrity check now.** SC-14's
  wording is met; its assurance is narrower than it reads. A prose checksum over ruling clauses in
  `gen-decisions-index.py` is real work, and the corruption it guards against was found here by a
  human read. Write the limit into the SC-14 row of the record and **backlog** the checker. Revisit
  the moment a ruling clause is corrupted a second time.
- **Q2 — the cost is eight criteria losing their only mechanical runner, silently, to any PR.**
  T-03's `Unit suite` step is what gives SC-01/02/03/06/07/09/12/17 a runner on the one
  branch-protected context, and nothing asserts its presence. The `case 25` guard the same file
  claims for the routes step **does not exist** (zero grep matches in
  `test-check-plan-routes.py`; inherited, origin `eafc8ad`) — so *neither* step is guarded and the
  comment says one of them is, which is worse than silence. **Owner: the main session, as a
  standalone `tests.yml` item, not this feature.** One test asserting both steps present and
  unneutered closes both halves at once; it is the cheapest item in this whole report.
- **Q3 — operator-owed BRIEF corrections, three now, not two.** Line 421 (`check-state.sh` "exits 1
  today" — it exits 0 at HEAD with a zero-byte T-04 baseline); SC-13 lines 448-454 ("exactly two
  carve-outs" — five apply under R-01); and **SC-10's parenthetical** ("FEAT-11, 20 keys" — 22, and
  not the maximum). I did not edit `BRIEF.md`.

## Citation drift — reported, not touched

`plan.yaml:158` (`D-04`) cites `DEC-189`; `plan.yaml:261` (`D-08`) cites `DEC-190`. The numbers
actually taken, confirmed at `docs/harness/DECISIONS.md:5574 / :5605 / :5645`, are **DEC-190**
(jsonschema required), **DEC-191** (closed key set) and **DEC-192** (phase/status collapse).
`DEC-189` is the unrelated write-guard two-bases entry (`DECISIONS.md:5506`). The correction is
`D-04 -> DEC-190`, `D-08 -> DEC-191`; DEC-192 was deliberately not pre-committed
(`plan.yaml:1483-1486`). **Operator's edit to apply, per the standing ruling.**

## Emergent, and NOT adopted as a criterion

`factory` is absent from all 17 files, so the schema's optional block is unexercised by the live
corpus and SC-15's "eleven-key file" has no instance. **This is not a nineteenth criterion.** It is
**already covered** by SC-01, which binds only that no key falls outside the eleven. Recommend: note
it, change nothing. The eighteen stand.

## Tree

Read-only. I ran no mutation and restored nothing because I broke nothing. The only two files I
wrote are this artifact and `notes/uat-FEAT-14-sc15-readability.md`, both paths I own.
