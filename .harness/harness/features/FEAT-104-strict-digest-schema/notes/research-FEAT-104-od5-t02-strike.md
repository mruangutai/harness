# OD-5 — T-02's strike recorded, and the premise behind it is now false

**Correction, 2026-09-09 — superseded by removal. There is no T-02 in `plan.yaml` any more.** This
note recorded an IN-PLACE strike, written on a premise that was TRUE at this worktree's HEAD
`25918bd2`: no verb in the worktree's `plan-merge.py` could remove a task, so recording the strike
in T-02's `title` and `intent` was the fullest compliance then available. That premise was closed by
human commit `11541475` on 2026-09-09, which added `plan-merge.py delete-items` at the control
plane. Under operator ruling OD-5, T-02 has now been **removed outright** by that verb — see
`## Cycle 3` at the foot of this note for the receipt and the read-back. The strike text this note
describes below no longer exists on disk; it went with the entry, and that is intended, not a loss.
Everything below is left as written so the correction is auditable.

**Both amends landed through `plan-merge.py amend`; nothing else in the worktree moved. But the
reason OD-5 was routed as an in-place strike no longer holds: the operator landed a delete verb
today.** `delete-items` is on `main` at commit `11541475` ("[harness:human] plan-merge.py: add
delete-items, the verb that removes whole tasks and decisions", Mike Ruangutai, 2026-09-09 13:11
-0700). This worktree's HEAD is `25918bd2` and does **not** contain it
(`git merge-base --is-ancestor` → no), which is why the worktree's copy of the script still offers
only seven verbs. The control-plane copy the harness instructs every agent to invoke
(`<HARNESS_CONTROL_PLANE_ROOT>/.claude/skills/harness/bin/plan-merge.py`) offers eight.

That commit is the operator taking **option (2)** of the two put to them in
`notes/research-FEAT-104-sigfix-c2.md:113-118` and `notes/ship-review-plan-signature-c2.md:35-38`.

## What was written

Two `amend` invocations against `tasks`, item `T-02`, each under compare-and-swap:

| Field | pre-sha256 | result |
|---|---|---|
| `title` | `da19daaa…b28bc` | `AMENDED tasks:T-02.title` |
| `intent` | `509ca698…5544` | `AMENDED tasks:T-02.intent` |

New `title`, exact:

```
STRUCK BY THE OPERATOR at the plan signature review 2026-09-09 (OD-5) - never to be dispatched; work already subsumed by T-01
```

New `intent`, one line: the strike first (operator, signature review, 2026-09-09, OD-5, never
dispatched); then why the entry survives — no delete verb at this worktree's HEAD, `apply` adds and
never deletes, `amend` replaces one field, **and that the gap has since closed via `delete-items` on
`main`, so a real removal is legal now and is the operator's ruling to make**; then where the work
went (T-01 PART 3 and PART 4, verbatim).

## The one deliberate deviation from the dispatch

The dispatch specified intent point 2 as "the entry cannot be removed by any legal route". **That is
false as of `11541475` and I did not write it.** A plan awaiting signature is the record the
goal-check and every later reader trust; asserting a tool gap the operator has already closed
falsifies it (PRINCIPLES rule 15). The same three points are recorded, point 2 stating the true
state including the new verb. Everything else in the dispatch was followed exactly.

## Verification read-back — done, not trusted from the verb's output

`plan.yaml` re-read after the writes (`:266-292`) and diffed structurally against `HEAD:` with
`yaml.safe_load`:

- `T-02` changed fields: **`title`, `intent` only.** `status: abandoned`, `traces: [REQ-07]`,
  `depends_on: [T-01]`, `change_type`, `execution_mode`, `execution_reason`, the 3-path `files:`
  list and `verify:` all compare equal to `HEAD`.
- T-01 and T-03..T-10: **every field equal.** Task id order unchanged.
- `schema`, `feature`, `approval`, `status`, `source_issues`, `lanes`, `decisions`, `panel`: all
  compare equal. `approval: {status: pending}`; `BRIEF.md:189` still `status: pending`.
- `git diff --stat` over the whole worktree: `plan.yaml` alone, 11 insertions / 12 deletions.
- `check-plan-routes.py` on this plan: **0 violations**; the DEVIATION lines are the expected
  DEC-174 carve-out shape.
- No claim refusal. Both writes returned `APPLIED` at exit 0 — the
  `harness-product-lead holds worktree claim(s)` refusal that hit the lead's run-dir write did not
  hit `plan.yaml`.

No gate script, validator or test file was touched; nothing was implemented; no Edit, Write or
redirect reached `plan.yaml`.

## Open — for the tier above, then the operator

1. **Does the strike now mean removal?** `delete-items --task T-02 --reason "<OD-5>"` would run
   clean: no surviving task's `depends_on` names T-02 (checked all ten) and no `panel` finding has
   `resolved_by: T-02`. It needs this branch to carry `11541475`, or the control-plane script run
   against this file. It is a task-set change on a plan pending signature, so it is not mine to take.
2. **It is not cosmetic.** B-1's INV-26 false positive — `all(status == "ready")` — is tripped by
   T-02's `abandoned` value alone. The operator struck B-1, so the in-place strike leaves
   `check-state.sh` red at signature; **removing the entry is what clears it**
   (`notes/ship-review-plan-signature-c2.md:69-73`).
3. **Three shipped artifacts now assert the false premise** and will mislead whoever reads them
   next: `STATE.md:17-27`, `notes/research-FEAT-104-sigfix-c2.md:98-118`,
   `notes/ship-review-plan-signature-c2.md:15,33-38` (plus the `.html` twin) all say no delete verb
   exists. `STATE.md` is not my write grant. Correcting them is one edit each once OD-5's
   disposition is settled — doing it before that would just have to be redone.

## Cycle 3 — T-02 removed outright, by `delete-items`, under OD-5

**The open question above is answered: the strike means removal.** The operator's own act — landing
the delete verb the same day this was escalated — is what made removal legal, so this is compliance
with OD-5 rather than a squad-initiated task-set change. The removal used the CONTROL-PLANE script
by absolute path against this worktree's plan file, because this branch does not carry `11541475`;
that is the intended route, not a workaround. Nothing was hand-edited, nothing was implemented, and
`approval:` stayed `{status: pending}` — nobody signed.

Receipt, verbatim:

```
DELETED tasks:T-02
DELETED-ITEMS 1 from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/plan.yaml — reason: operator ruling OD-5 at the plan signature review, 2026-09-09: struck; work already subsumed by T-01 PART 3 and PART 4
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/plan.yaml
```

The `--reason` is printed on the receipt and is deliberately NOT written into the plan; this note is
where it survives.

### Pre-flight, re-derived from the file as it stood, not from cycle 2's notes

- **No `depends_on` dangles.** Loaded the plan and printed every task's `depends_on`: `T-01←[T-10]`,
  `T-03←[T-01]`, `T-04←[T-01,T-03]`, `T-05←[T-03]`, `T-06←[T-05]`, `T-07←[T-05]`,
  `T-08←[T-04,T-06]`, `T-09←[T-04,T-06,T-07,T-08]`, `T-10←[]`. T-02 appeared in none of them; the
  only edge touching it was its own `depends_on: [T-01]`, which left with it.
- **No `panel:` reference.** Serialised the whole `panel:` mapping and searched it for `T-02`: zero
  hits across 3 readers, 4 findings and 2 dismissals. No finding carries `resolved_by:` at all.
- **REQ-07 keeps live tasks.** After removal, `REQ-07` is traced by **T-01** (which absorbed the
  work, PART 3 and PART 4) and by **T-09**. Its criterion is SC-10, untouched.
- **Textual occurrences, every one classified.** Two existed in `plan.yaml` besides the entry:
  `T-01.intent:125` ("This task subsumes the former T-02, which is abandoned") — **historical
  prose, harmless**, a broken reference to nothing since it points at an id deliberately gone, and
  out of this run's grant; and T-02's own `verify:` comment — **structural**, removed with the
  entry. Post-removal re-grep of `plan.yaml` returns exactly one hit: `T-01.intent:125`.
  Reported, not amended: touching T-01 would be a change to a task this run was told not to touch.

### Read-back, measured on disk after the write

- Acceptance command output: `['T-01', 'T-03', 'T-04', 'T-05', 'T-06', 'T-07', 'T-08', 'T-09',
  'T-10']`, then `{'status': 'pending'}`, then `4`.
- **Byte-identity of the nine survivors is measured, not asserted:** the file was copied to
  `/tmp/feat104-plan-before.yaml` before the write; `diff -u` after reports **one hunk, 0
  insertions / 28 deletions**, the T-02 block alone. Every other byte in the file is unchanged.
- `panel:` still holds 3 readers, 4 findings, 2 dismissals. Decisions `D-01..D-12` all present.
- Traceability closed both ways over the nine tasks: every one of the 9 REQs has ≥1 task (set
  difference empty), no task traces a REQ absent from `BRIEF.md` (set difference empty), and every
  REQ has ≥1 SC (`research-FEAT-104-sigfix-c2.md:143-144`, unaffected by a task removal).
- **Expected B-1 side effect, not re-measured here:** `check-state.sh` INV-26's not-started skip
  requires `all(status == "ready")`, which T-02's `abandoned` value alone defeated. Cycle 2
  measured the counterfactual directly — with T-02 dropped the skip fires, with it present it does
  not (`notes/ship-review-plan-signature-c2.md:69-73`) — so the removal is expected to clear that
  false positive. I did not run the gate: it is the orchestrator's to observe at signature.
- Three artifacts asserted the now-false premise. Two are mine and are corrected in place:
  this note and `notes/research-FEAT-104-sigfix-c2.md`. **`STATE.md:17-27` and
  `notes/ship-review-plan-signature-c2.md` (plus its `.html` twin) are NOT my write grant** and
  still say no delete route exists — the orchestrator's to correct.
