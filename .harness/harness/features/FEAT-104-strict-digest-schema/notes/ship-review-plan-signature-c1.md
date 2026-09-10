# FEAT-104 — plan signature packet

**Recommendation: sign, after ruling on PF-4bd91290 (high, gating).** The plan is complete,
traced and measured. One panel finding gates the signature and cannot be accepted by any agent —
it is yours to accept, remedy, or overrule. Four further items are genuinely your call rather than
pm's; the rest is decided and recorded.

Nothing was implemented. No gate script was edited. No test suite was run.

## How this briefing was assembled

No report round was spawned. I read the run digests from disk. The paths:

- `runs/plan-product/digest.md` — BRIEF + plan drafting
- `runs/goalcheck-plan-product/digest.md` — panel segment 1, pm's goal-check of the draft
- `runs/planfix-c1-product/digest.md` — the repair of that goal-check's six findings
- `runs/planpanel-c1-validator/digest.md` — panel segment 2, the two adversarial readers
- `runs/paneltranscribe-c1-product/digest.md` and `runs/paneltranscribe-c1b-product/digest.md` —
  panel segment 3, the record written into `plan.yaml`

All relative to `.harness/harness/features/FEAT-104-strict-digest-schema/`.

## What you are signing

`BRIEF.md` — 9 requirements, 15 success criteria, every one carrying a verification method:
**13 `automated`** (all resolving to the `integration` runner, which exists and runs),
**1 `inspection`** (SC-12, the historical-artifact manifest), **1 `uat`** (SC-13, you read the
carve-out diff — DEC-174 requires a human there and no automated gate substitutes).

`plan.yaml` — 12 decisions (D-01..D-12), 10 tasks (T-02 is `abandoned`, subsumed into T-01),
a `lanes:` table resolving every literal path through `check-domain.sh --resolve`, and the
`panel:` record with all three readers and four findings.

The substance: unknown keys on a new digest return get rejected instead of ignored; the same
for keys inside a run `state.yaml` `steps[]` entry, which nothing governs today; a declared
free-form-inside `evidence:` container so per-step evidence keeps a legal home; and issue **#37
resolved in-feature** — `adequacy_notes` becomes a required lead field rather than a load-bearing
signal nothing enforces.

## The measurement that changed the shape of the work

Issue #104's tables were five weeks stale. Re-measured on 2026-09-09:

| | #104 said (2026-08-05) | measured now |
|---|---|---|
| distinct out-of-schema digest keys | 8 | **65**, across 220 of 319 readable digests (69%) |
| distinct `steps[]` keys | 95 | **202**, across 356 runs |
| invented once and never reused | 72 | **132** — including 7 prose sentences used as mapping keys |

## Your decisions

**OD-1 — PF-4bd91290deaf98062943319ff3ea5641 · high · gating.** SC-06, T-01 PART 6 and T-08 pin
the "prove the suite reddens against the pre-change validator" control on a `git show` of an
absolute commit id. `tests/integration/test-validate-digest.py:30-33` records this repository's
own ruling that this exact mechanism was removed and replaced with vendored inert fixture bytes,
because it "needs no `git show` and no repository history to be hermetic in a shallow CI checkout";
`:4008-4010` records the shallow-clone proof. I confirmed all of that verbatim at source.
**And CI does clone shallow today** — `.github/workflows/tests.yml:50` is a bare
`actions/checkout@v4` with no `fetch-depth`, which defaults to depth 1. So the spurious red is
immediate, not latent.
The panel's remedy: T-01 vendors its own pre-T-04 validator bytes as an inert non-`.py` fixture,
which deletes PART 6's second commit, `base-revision-pre-T-04.txt` and T-08's two-sided grep, and
takes the F4 ordering hazard with it. SC-06's substance survives intact.
**Neither I nor pm may accept this risk** (DEC-176). Either the remedy enters your signature review
as a change request, or you record `sign-approval --overrule PF-4bd91290deaf98062943319ff3ea5641:<reason>`.
Signing with neither leaves `check-state.sh` INV-32 red the moment approval flips to `approved`.

**OD-2 — PF-d2cefa75a1931540efa60d3561f7df6b · med.** D-02's repaired bar admits three lead
`PASSTHROUGH` rows (`failures`, `suite`, `kinds`) on observed-traffic grounds, while REQ-04 defines
legitimate use as documented-block-only. The plan's own requirement and its own decision disagree,
at the tier that is nearly all of the measured corpus. Drop the three rows, or record why D-02
overrides REQ-04's sentence.

**OD-3 — PF-4d84bb7e52beff3ee62eb98a7115ae9e · low.** T-01 PART 1 says "reuse the existing field
loop", but that loop (`validate-digest.py:1190`, `:1197`) makes every field required when absent —
a literal reading would make all 24 optional fields mandatory and reproduce the critical defect the
repair just closed. I confirmed the loop's shape. One clarifying sentence saves an implementer a
cycle; T-01's own omission assertions make the wrong reading unlandable either way.

**OD-4 — PF-7469688fee994f7ec08ad85dea1d1f8b · low.** SC-11 read standalone is falsified by D-11's
creation floor: its accept case is necessarily an update to an already-existing version-1 file.
Add "on a run already carrying `schema_version: 1`".

**OD-5 — T-02.** It is retained at `status: abandoned` rather than deleted, because `plan-merge.py`
adds and never deletes and the merge is worth seeing in the record. Keep it, or strike the id.
Note this is not free: see B-1.

**OD-6 — the decision record.** T-09 corrects one falsified clause in DEC-126's Applied record
(`DECISIONS.md:2612-2613` names `adequacy_notes` as the validator-lead's per-role extra, which D-03
falsifies). Correcting a clause to current truth is what DEC-205 requires; it is still a write to
the decision log and you should see it named.

## What the panel did

Both readers ran; neither was skipped.

| reader | persona | status | outcome |
|---|---|---|---|
| `goalcheck` | `harness-pm` | ran | FAIL, 6 must_fix — **all six closed** in `planfix-c1`, plus 2 accepted/deleted criteria and 2 bonus fixes |
| `should-not-exist` | `fable-advisor` | ran | 2 findings (1 high, 1 med) |
| `scope` | `harness-code-reviewer` | ran | 2 findings (both low); `reviewed: plan:<path>`, `code_grade: n_a`, no `review_sha` invented |

Two findings were assessed and dismissed with reasons, both recorded in `panel.dismissed`. One is
worth your eye: the code-reviewer independently cleared the base-revision pin as *non-vacuous*, and
that clearance is true — it answers discrimination, not hermeticity, so it does not rebut
PF-4bd91290. Each reader was individually correct; only the union of their scopes gates.

The goal-check's own critical finding is the one worth knowing about, because it is what the panel
exists for: the first draft derived its legal key set from observed digests, which were lead-only.
Under it, **every conforming non-lead return would have exited 2** — 16 fields that seven personas'
own documented output blocks instruct them to emit had no declaration. I verified four of those at
source before spending the cycle. The repair re-derives the set from the documented blocks and adds
a mechanical two-direction agreement assertion, so a documented field with no declaration becomes a
test failure rather than the next reader's discovery.

## Proposed backlog — strike any row by ID; unlisted items die silently

| ID | Nature | Item |
|---|---|---|
| B-1 | bug | `check-state.sh` INV-26's not-started skip requires `all(status == "ready")`, so one task legitimately recorded `abandoned` on an **unsigned** plan trips a false "the mirror never ran — run `gh-sync.py open`" violation. I measured this directly: with T-02 removed the skip fires; with it present it does not. The instruction is also wrong to follow — the mirror reference puts `gh-sync.py open` *after* signed approval. Remedy: treat `abandoned` as not-started in that skip |
| B-2 | chore | This worktree's `.harness/team-config.yaml` is behind the owner root by `4d81e460` (the pm `receipt-*.md` grant, #46/#71). It is why `check-plan-routes.py` exits 1 — one violation, the manifest header, no task. The hook reads the owner copy, so nothing executes wrongly; the gate is simply red at signature time and needs an owner |
| B-3 | bug | 44 of 370 run digests carry no yaml fence and 7 fail `safe_load` — pre-DEC-172 artifacts no validator can read. Out of scope here by your own ruling (nothing is rewritten), but nothing else is tracking them |
| B-4 | enhancement | Closing the `stop_hook_active` re-prompt passthrough (`validate-digest.py:1744`). D-07 deliberately leaves it open and compensates with a one-shot-sufficient message; DEC-208 records it as intentional. Closing it is its own ruling, not this feature's |
| B-5 | enhancement | SC-16 asserts documentation/declaration agreement over **keys** only. One value-level disagreement already surfaced — `harness-validator-lead.md:135` documents `severity_max` including `info`, not a member of `SEV`. T-01 pins that one case; widening the check to compare documented enums against declared sets is unbuilt |
| B-6 | bug | Harness transport defect, seen twice this run: a subagent's job row returned `failed (exit 1) — Subagent called yield with null data` while its fenced digest and its artifact were both intact and well-formed. A PASSing reviewer looks failed to a router |

## Budget

`cycles_used: 2` of 10 — one pm send-back inside the drafting run, one goal-check FAIL routed back
as the repair cycle. `runs: 6` of an informational 20. Both healthy; every run resolved findings
and advanced the criteria.

## Artifacts

All under
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/`:

- `BRIEF.md` — approval `pending`
- `plan.yaml` — approval `pending`, feature station `plan`, `panel:` recorded
- `notes/research-FEAT-104-triage-c0.md` — the measurement and the per-key triage
- `notes/research-FEAT-104-goalcheck-plan-c0.md` — panel segment 1
- `notes/research-FEAT-104-planfix-c1.md` — how each goal-check finding was closed
- `notes/review-harness-code-reviewer-planpanel-c1.md` — the `scope` reader's own note
- `notes/research-FEAT-104-strict-digest-schema-panel-transcription-c1.md` — the transcription record
- `notes/research-FEAT-104-panel-goalcheck-reader-c1b.md` — the third reader entry
