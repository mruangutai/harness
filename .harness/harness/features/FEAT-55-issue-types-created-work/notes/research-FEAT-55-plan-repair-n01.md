# Plan repair c2 — N-01 closed by positive provenance, N-02 folded in, BRIEF given its two lines

**N-01 (high) is repaired in the direction R9 fixes: provenance is recorded POSITIVELY at
creation, and an absent entry is unknown provenance that is never typed — on any route, on any
rerun.** The key-presence reading that made all 41 pre-existing receipts backfill candidates is
gone from both routes and is now explicitly prohibited where it used to be mandated. Two new
fixture cases prove the bound (T-03 **case J**, T-07 **case H**); the two existing cases that
asserted the overturned ordering (T-03 **case G**, T-07 **case E**) are corrected in the same edit.
R9 is recorded as **D-20** and the one decision that carried the old ordering, **D-10**, is amended.

## What changed, by id and field

| id | field | change |
|---|---|---|
| D-20 | new decision | provenance positive at creation; `"created"` in the same receipt write as the number, promoted to `True` after the apply, `"adopted"` for a number Harness took over, **absent = unknown = never typed**; only `"created"` is ever backfilled. `dec: DEC-138` |
| D-10 | `choice` | ordering rewritten: number **and** `"created"` in one write, promote to `True` after the apply; a rerun retries only against a number whose recorded provenance says Harness created it |
| T-04 | `intent` | §4 gains the backfill set in `missing_types` (N-02); §6 rewritten — the four readings, the one-act write, the backfill bounded to `"created"`, absent never typed and never promoted; §7 re-justified (the marker records adoption positively; it no longer rests on the overturned reading) |
| T-03 | `intent` | case G corrected (`github.typed` holds `"created"`, not absent, after a failed apply; `True` after the rerun); **case J added** |
| T-08 | `intent` | §6 gains the backfill set in `missing_types` (N-02); §8 rewritten with the same four readings, one-act writes on both branches (`:421-425`, `:433-437`), the `:404-407` adopted branch, and the bounded backfill |
| T-07 | `intent` | case E corrected (`factory.yaml` records `"created"`, not "no typed flag"; `True` after the rerun); **case H added** |

Nothing else was touched: `approval:` (`status: pending`), the feature `status: plan`, and the
absence of `panel:` are byte-unchanged; no REQ, no SC but SC-10, no other task, no `verify:`, no
`files:`, no severity, no `traces:`.

## The two new fixture cases (the proof, not the assertion)

- **T-03 case J** — a `feature.json` that already carries `github.parent` and one task's number with
  **no** `github.typed` at all (the shape of all 41 legacy receipts). `FAKE_TYPES=available`: zero
  `updateIssue` for either recorded number, no entry written for either key, **and the same again on
  a rerun**; the run still exits 0 and still types the unrecorded tasks, so the case proves the bound
  rather than a dead run.
- **T-07 case H** — the identical shape on a legacy `factory.yaml`, first run and rerun.

## Acceptance evidence

- `yaml.safe_load` on the plan: **loads**, 12 tasks, 20 decisions. `approval` = `{'status':
  'pending'}`, `status` = `plan`, `panel` **absent**.
- `check-plan-routes.py <plan>`: `0 violation(s)`, exit 0 (T-12's DEC-174 deviation line is the
  expected carve-out output).
- F-03 pinned wording: re-derived from the loaded document — T-11 §3 and T-12 §1 are **byte-identical,
  511 chars, sha256 `7f065a7a5225…`**, unchanged by this edit.
- plan.yaml sha256 after the edit: `4e70d07440d2682af77651f8dca36a1d092f7fa2f1ae9f8dad70a30530c93481`
  (was `eb9b9f03…`). Every write went through `plan-merge.py apply` / `amend --expect-sha256`.
- BRIEF: 11 REQ, 11 SC, `status: pending` — re-counted after the edit.

## The decision sweep — D-01..D-19 against D-20

Only **D-10** contradicted R9; it is amended. Checked and clear: D-01..D-06 and D-18 (mapping only),
D-07/D-08 (the record), D-09 (kind registration), D-11/D-12/D-14/D-15/D-16/D-17, D-19 (probe).

**D-13 is compatible, and deliberately not touched.** `backlog-issues.json` is a net-new file keyed
by the item string, and T-06 §5 writes `number` and `typed: false` in one act, so an entry exists
only where cmd_backlog created the issue and absence means "not created yet, create it" — there is
no legacy population to misread. Residue, advisory only: that route spells the pre-apply state
`false` where the other two now spell it `"created"`. One vocabulary would be tidier; the safety
argument does not depend on it, and unifying it was outside this dispatch.

## BRIEF — the two authorised additions

- **SC-10 (R10):** the three verdicts and the sentence naming SC-10 the carrier of #1289's
  enabled-repository acceptance are both intact; the criterion now states that an environmental
  skip — no `gh`, `github.sync` false, an unpinned repo, a failed capability query, a create opt-in
  naming another repository — is outside the three verdicts, is never read as a pass, and leaves
  SC-10 **unmet** until one of the three is recorded (`BRIEF.md:146-153`).
- **`## Verification gaps` (R11):** one new bullet (`BRIEF.md:173-177`) — the default invocation the
  registered kind runs creates nothing (D-19), and the live pass is reachable only under the explicit
  create opt-in, which **creates a real issue in the repository the flag names** and then reports what
  it created and the command that removes it.

## Open questions

- **Q1 (non-blocking, for the panel not the operator):** D-20 accepts a cost — a genuine
  Harness-created issue recorded *before* this ships is never typed by any rerun. That is the
  fail-safe side of R9 and is stated in D-20's `because`. If the operator ever wants those typed, it
  is a separate, opt-in, one-shot backfill with a human-supplied provenance list — not this feature.
