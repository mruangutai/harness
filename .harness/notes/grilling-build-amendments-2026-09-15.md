# Grilling — build-phase amendments: the eng-lead proceeds and records a signed task's changed how (#1716) — 2026-09-15

## Destination
An eng-lead that finds a signed task's `intent`, `files` or `verify` text incomplete or worse than
what the code needs — while every SC and the task set stay untouched and every recorded decision
is honored — makes the change, carries it as `amendments:` in its digest, and the orchestrator
transcribes it into `plan.yaml` and the judgement ledger with one command. No `BLOCKED`, no
operator round-trip, no product amend run. The operator overrules at ship; the overrule rate is
the trust KPI.

## Mission
mission: plan
reason: new schema surface (a digest field, a sixth judgement kind, a plan-merge verb, per-task text hashes) and a new INV-40 trigger — fails rule 3 of the patch test; cause and files are known.
confirmed-by: operator (blanket ruling in session 2026-09-15: "do all of them from plan (or patch) to ship"; flow shape chosen: intake + direct build + validate panel + ship)

## Settled
- Priority → the definition of done and the SCs. An amendment to a task's how that meets them while
  being more code-efficient or more reliable, by virtue of what the build team learned, is honored —
  recorded, not asked. (operator, verbatim in substance)
- No re-dispatch → the eng-lead makes the change in the same run. The orchestrator never
  re-dispatches a task to apply an amendment; it transcribes. (operator: "i don't know why an
  orchestrator needs to dispatch again")
- Eligibility, three conditions, all required → (a) changes only a signed task's `intent`, `files`
  or `verify` text; (b) no SC added, removed or reworded, no task added or deleted; (c) conforms to
  every recorded `plan.yaml` `decisions:` entry. Anything else stays `BLOCKED` with `open_questions`
  + recommendation (DEC-230).
- Digest field → `amendments: [{task, field, was, now, reason}]` on the eng-lead digest;
  `validate-digest.py` declares it (DEC-223 closed contract) and refuses an entry naming an SC id
  or a `decisions:` id.
- Transcription → `plan-merge.py record-amendments --digest <digest.md>`: orchestrator-runnable,
  byte-preserving from the digest, writes task fields only, appends the `amendment` judgement in
  the same act. Shape precedent: `record-panel --digest` (DEC-229).
- Judgement kind → `amendment` becomes the sixth `JUDGEMENT_KINDS` entry
  (`feature-record.py:59`); DEC-230's "five kinds are exhaustive" is amended to six.
- Signature survives → DEC-229 resets approval on task-set change only; a text amendment leaves
  `approval.status: approved`. DEC-23's "approval-gated" now reads: approved at signature, amended
  under ledger.
- Enforcement → `sign-approval` records a sha256 of each task's text (`intent`+`files`+`verify`)
  in `feature.json`; a new INV-40 trigger: a task whose current text hash differs from the signed
  hash with no `amendment` judgement naming that task is a violation, with the remedy named.
- Overrule → the ship review may mark an amendment `overruled: true` on its ledger entry (one
  `feature-record.py` route); the overrule rate is derivable from `judgements[]`.
- Cross-checks that make builder-side `verify` amendments safe, to be stated in the DEC → qa derives
  coverage from the BRIEF with no source access; code-review Stage 1 reads `BRIEF.md` +
  `decisions:` and never task text (`harness-code-review/SKILL.md:17-20`); Stage 2 + `code-grade.py`
  is recomputed by `validate-digest.py` over the diff range. Record that validate must never be
  re-anchored on task text.
- Code-review Stage 1 reads `amendments:` as "where the build departed from the signed how" and
  checks each against the SC and decision it serves; a departure that serves them passes, one that
  does not is a `substance` finding.
- Cycle accounting → an amended task's continuation is a run, not a cycle (no gate failed). State
  it in the DEC explicitly under DEC-157.
- Build execution → every script surface is DEC-174 carve-out: `validate-digest.py`,
  `plan-merge.py`, `feature-record.py`, `check-state.py` and their tests → `main-session-direct`.
  Prose (DEC-230/32/23 text, `harness-eng-lead.md` both adapters, playbook build phase,
  `harness-code-review` skill) is dispatchable but small; pm may fold it into the direct task or
  give it a documentor task.

## Not yet specified
- none

## Out of scope
- The advisor (`fable-advisor`) taking any seat in build — deliberately removed from the discussion.
- "A ruling generalizes" (precedent application of `answers-*.md`) — subsumed: a lead that
  proceeds has no repeated question.
- Letting the lead change a `decisions:` entry or an SC — those remain DEC-23/DEC-32 asks.
- #1683 (general top-level write route) — this verb is task-scoped and does not depend on it.

## Facts I verified (so pm does not re-derive them)
- Specimen: BUG-285-canonical-reader T-03 blocked three times; each `notes/ship-review-2026-09-1{4,5}-t03*.md` recommendation matches the operator's `notes/answers-2026-09-1{4,5}-t03*.md` in substance (keyword-only text source, no second accessor, no exemption; `parse_gh_json` any JSON value; `manifest_domains(agent=None)`). Loop 2's return says "the same mode already approved for `load_harness_json`". Cost: 3 blocked eng runs, 3 product amend runs, 2 of 10 cycles, ~$17 (#1713 Findings 2, 7).
- `JUDGEMENT_KINDS = ("mission", "finding_kind", "regate", "continue", "succession")` at `feature-record.py:59`; `--kind` is `choices=JUDGEMENT_KINDS` at :420.
- INV-40 lives at `check-state.py:2869-3000`, three independent triggers each naming its remedy.
- `validate-digest.py` field tables: `PASSTHROUGH` (:243), `DOCUMENTED_OPTIONAL` (:344); `harness-eng-lead` maps to persona `lead` (:392); an undeclared key is refused with the routing message at :1544-1549.
- `plan-merge.py` verbs today: `apply`, `amend` (one field of one task/decision, CAS on sha256), `delete-items`, `record-panel --digest`, `sign-approval`, `set-lanes`, `set-task-station`, `set-feature-station`, `check`. `amend` is the write primitive `record-amendments` can compose.
- `harness-code-review/SKILL.md:17-20`: Stage 1 reads `BRIEF.md` and `plan.yaml` `decisions:`, then the diff.
- Base: `origin/main` at 82c9d074.
