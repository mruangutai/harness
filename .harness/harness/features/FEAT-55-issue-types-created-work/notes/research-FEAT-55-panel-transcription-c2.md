# Panel transcription — FEAT-55 cycle 2

**All four cycle-2 findings of run `2026-09-04-14-validator` plus the five unruled cycle-1 findings —
nine in total — are now in `plan.yaml`'s `panel:` key, verbatim, with machine-computed ids. One `high`
finding is `awaiting_user`; the other eight are `batched_to_signature_review`. Nothing was adjudicated,
softened, merged, renumbered or re-severitied. F1 and F3 were NOT fixed: F1 is `high`, so its risk
cannot be discharged below the operator (DEC-176), and F3 rides in the same signature pass.**
The only two findings that dropped are the two the operator already ruled on — which is what closes
goal-check C3-02, the stale `awaiting_user` on `PF-f1031f76…`.

`plan.yaml` sha256: `d8f98dfc4491782da85ef17366650792247c5ba47d45147c5a5d927f691c59dc` before →
`b807feca113a653af83208c8bea7b8d29a849274e364fd452cd6cbe5832978f4` after.
`BRIEF.md` sha256: `ab2d6de2537799f88fbc15f3e08563a5eb340d6dc85a03a059d930509546b99b` before and after —
byte-unchanged.

## The ids — computed, never typed

Every id came from `panel_findings.py id --reader <r> --summary <s>`, invoked by
`/tmp/feat55-panel-c2/build_panel.py` over the `yaml.safe_load` of the digest's own fenced YAML block
(`runs/2026-09-04-14-validator/digest.md`) and over `yaml.safe_load` of the current `plan.yaml` for the
carried five. No summary string passed through a human edit. Order: the four new in the lead's ref
order, then the five carried in their cycle-1 order.

| # | ref | id | reader | severity | disposition |
|---|---|---|---|---|---|
| 1 | F1 | `PF-60f3544bd486fe9d3541a26658e5fa9f` | scope | **high** | `awaiting_user` |
| 2 | F2 | `PF-08da208931348b8cb200b34e8e7a1d31` | should-not-exist | med | `batched_to_signature_review` |
| 3 | F3 | `PF-8b5853220e5f2768339090bdbc44b1a5` | scope + should-not-exist (compound) | low | `batched_to_signature_review` |
| 4 | F4 | `PF-56a2ce7a053111a3aff62a4b97c5902e` | should-not-exist | low | `batched_to_signature_review` |
| 5 | c1 | `PF-1286544c197d1b0eb4a9b0dc8e1234dc` | should-not-exist | med | `batched_to_signature_review` |
| 6 | c1 | `PF-452948136bf467869d223e027191ae49` | scope | med | `batched_to_signature_review` |
| 7 | c1 | `PF-e27f1c3018b6b8477547a1b028607f96` | should-not-exist | low | `batched_to_signature_review` |
| 8 | c1 | `PF-0c12a033f69bb6bc60b8f96134f94fd0` | should-not-exist | low | `batched_to_signature_review` |
| 9 | c1 | `PF-9a71cb9a0c590b06b890ff1517b80385` | should-not-exist | info | `batched_to_signature_review` |

Dropped: `PF-f1031f76b4537f1cd9b60ddc0559b7d1` (fix directed and landed) and
`PF-610431f7d96408d23666cc4e60071501` (T-10 probe kept). Only an `approval.rulings` entry written by
the main session records the operator's acceptance of finding 1's risk; no lead and no pm tier may.

## F3's `reader` — the compound string was stored verbatim

**Written as the lead recorded it:** `scope + should-not-exist (one defect, two reporters, both low -
no reconciliation needed)`. Two reasons, and the second is decisive:

1. **The panel shape does not constrain a finding's `reader`.** `plan-merge.py::_load_panel_value`
   validates only `last_run` (str), `cycle` (int), `readers` (list), `findings` (list); check-state.sh
   INV-32 reads a finding's `id`, `severity` and `disposition` only, and matches its
   `expected_readers` set against `panel.readers[]`, never against `findings[].reader`. So the
   conditional in the dispatch ("if the shape constrains it") does not fire.
2. **The acceptance requires `reader` to compare `==` to the lead's digest.** Recording the primary
   reporter would have required editing the summary to carry the corroboration — a text change to a
   finding I am forbidden to adjudicate.

**This is load-bearing because the id hashes over the stored reader string.** Had the primary-reporter
form been stored, the id would be `PF-5ac9194207536d394931574afe59efee`. If a later cycle rewrites the
reader to a bare step id, F3 gets a NEW id and any ruling recorded against `PF-8b58532…` goes stale —
which check-state.sh reports, by design.

## Field mapping — `why` is the digest's `consequence`

The panel finding shape is six keys (`id`, `reader`, `severity`, `summary`, `why`, `disposition`); the
lead's digest findings carry `summary`, `consequence` and `lead_check`. `why` := `consequence`, verbatim.
`lead_check` has no home in the shape and was not carried — it stays in
`runs/2026-09-04-14-validator/digest.md`, which the operator reads alongside the plan.

## Verification, all from the file on disk after the write

`/tmp/feat55-panel-c2/verify.py` — 48 checks, 48 passed, exit 0:

- `set-panel` printed `PANEL cycle 2 -> <plan.yaml>` and `APPLIED <plan.yaml>`, exit 0. It was the only
  write route — no Edit, no Write, no redirect.
- 9 findings; `panel.cycle == 2` and is an `int`; `last_run == "2026-09-04-14-validator"`;
  `severity_max: high`; 2 readers (`fable-advisor`/`should-not-exist` and
  `harness-code-reviewer`/`scope`), both `status: ran`, `reason: none`, neither skipped.
- **Re-derivation:** all nine stored ids re-compute from their OWN stored `reader` + `summary` and
  match, each 35 chars — the carried five included.
- Every new finding's `summary`/`why`/`severity`/`reader` compares `==` to the lead's digest object;
  every carried finding's `id`/`reader`/`severity`/`summary`/`why` compares `==` to its cycle-1 text;
  `must_fix` (1) and `fix_order` (4) compare `==` to the lead's lists.
- Dispositions: 1 `awaiting_user` (F1, high) + 8 `batched_to_signature_review`, no third value, none
  `dismissed`. The lead's three recorded dismissals were not adjudicated into the findings list.
- Untouched: `approval: {status: pending}`, top-level `status: plan`, 12 tasks, 20 decisions, and no
  top-level key added or lost.
- **Nothing outside `panel:` moved, proven byte-exactly.** No pre-write copy was kept and `HEAD` is
  stale (the cycle-2 plan revision landed in the working tree after `c76da3b6`), so
  `/tmp/feat55-panel-c2/reconstruct.py` spliced HEAD's `panel:` region back into the current bytes: the
  result hashes to `d8f98dfc…c59dc`, the recorded pre-write sha256. That proves both that every byte
  outside `panel:` is unchanged by this run, and that the pre-write panel was byte-identical to the
  committed cycle-1 record.
- `check-plan-routes.py <plan.yaml>` → `0 violation(s) across 1 plan(s)`, exit 0 (the T-12 line is the
  expected DEC-174 main-session-direct deviation, not a failure).
- No formatter, linter or project suite was run. The panel value file lived at
  `/tmp/feat55-panel-c2/panel.yaml` (transient scaffolding; the durable record is the plan key).

## Open questions

- **Q1 (non-blocking, harness defect):** `panel.readers[]` entries are written with a `step:` key (the
  shape cycle 1 pinned and this cycle repeats), but check-state.sh INV-32 keys those entries by a
  `reader:` field (`check-state.sh:537-540`). Against an approved plan every expected reader would
  therefore read as "never ran or was not recorded" — a fail-closed violation on a correctly recorded
  panel. It does not fire today (INV-32 grades approved plans only, and this one is `pending`), but it
  fires the moment the main session signs. Either the writer or the invariant is wrong; that is the
  harness owner's call, not a FEAT-55 edit.
- **Q2 (non-blocking):** the lead's `lead_check` for each finding — its independent re-measurement at
  source — has no key in the panel shape and so is not carried into `plan.yaml`. The operator sees it
  only by opening the run digest. Worth deciding as a schema question.
- **Q3 (non-blocking, carried from cycle 1):** a `panel.transcription_rule` key would let a later
  reader tell whether a summary was normalized before hashing. Not written: the dispatch pins the panel
  shape, and every summary here compares byte-equal to its source.
