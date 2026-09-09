# sigfix-c2 — the six operator rulings applied to FEAT-104's planning artifacts

**Five of six applied; OD-5 is blocked on a tool gap and T-02 is left exactly as it stands.**
Nothing was implemented: only `BRIEF.md`, `plan.yaml` (through `plan-merge.py` verbs) and this note
changed. `approval:` is `{status: pending}` in `plan.yaml` and `status: pending` in `BRIEF.md`,
byte-untouched — `sign-approval` was never invoked and `amend` cannot reach the block
(`plan-merge.py:1230-1232`).

## OD-1 — hermetic inert fixture (PF-4bd91290deaf98062943319ff3ea5641)

**Applied.** The precedent I matched rather than reinvented: `test-validate-digest.py:30-33` names
`FIXTURE_DIR = tests/integration/fixtures/` and `check_prior_validator` at `:2862-2884` writes
`prior-validate-digest.py.fixture` into a temp dir under the module's real filename — "no `git show`,
no repository history", because a `--depth 1` clone resolves no pinned id (`:3554-3558`).

Changed:

- `BRIEF.md` SC-06 — rewritten. T-01 vendors its own post-PART-2/pre-T-04 validator bytes as
  `tests/integration/fixtures/pre-t04-validate-digest.py.fixture`; the case writes them beside their
  real siblings and asserts the unknown-key payloads exit 0 there and 2 against the current file.
- `plan.yaml` T-01 `files:` — `notes/base-revision-pre-T-04.txt` removed, the fixture path added.
- `plan.yaml` T-01 PART 6 — the second commit and the `git rev-parse HEAD` write are **deleted**;
  PARTS 1–6 are now ONE commit, because a fixture can carry its own bytes.
- `plan.yaml` T-01 `verify:` — two new clauses assert the fixture's content at T-01 time, so a
  mis-taken revision is caught there instead of at T-08 (this is only possible now; a commit id
  could not be checked by the commit that wrote it).
- `plan.yaml` T-08 `intent:`/`verify:` — the 40-hex/`cat-file`/`git show` re-derivation is replaced
  by the same two-sided proof **against the fixture bytes**.

**How the revision is proven right without a commit id** — by content, asserted in the case and in
two `verify:` blocks: the bytes CONTAIN `DOCUMENTED_OPTIONAL` (T-01 is in them) and do NOT contain
`undeclared digest key` (T-04 is not). The absence check is preceded by the presence check, which is
its positive control — a grep over a missing file prints nothing and would otherwise pass.
SC-06 stays falsifiable on behaviour: the rejection half must still exit 0 against the vendored
validator, and either content assertion failing is a red case, not a skip.

Residual risk: the fixture is ~55 KB of committed duplicate source (the existing precedent costs the
same). Deliberate — it is inert data, never selected by `code_grade._changed_python_files` because of
the non-`.py` suffix, which T-01 PART 6 states explicitly.

Sweep: `base-revision-pre-T-04`, `git show`, `git rev-parse`, `cat-file` — **zero** occurrences left
in `BRIEF.md` and in every non-`panel` key of `plan.yaml`. They survive only inside `panel.findings`
and `panel.dismissed`, where the reader's own words are transcribed verbatim and an id is a content
hash of the summary; rewording one would forge a new id.

## OD-2 — three passthroughs struck (PF-d2cefa75a1931540efa60d3561f7df6b)

**Applied.** `PASSTHROUGH["lead"]` is **5 rows**: `sc_status`, `needs_approval`, `severity_max`,
`matrix_ok`, `coverage_gaps`. `failures`, `suite`, `kinds` are gone from T-01 PART 1's code block and
prose, PART 3's documented line, PART 5's per-key assertions, T-08's legitimate-key replay, and
`BRIEF.md` SC-05 (now enumerating the five). T-03's arithmetic reads "minus the ONE row" —
`coverage_gaps`.

**The repaired bar (D-02, amended `choice` + `because`):** a field earns a row only when a
**documented output block instructs a LEAD to carry it**. Observed traffic decides nothing, which is
what REQ-04 already said and what the old "seen riding up a roll-up" clause contradicted.

**Row-movement report — re-checked every survivor against the repaired bar:**

| row | ground | moves? |
|---|---|---|
| `sc_status` | canonical lead block, `harness-team/SKILL.md:255` | no |
| `needs_approval` | `.omp/agents/harness-product-lead.md:90` | no |
| `severity_max` | `.omp/agents/harness-validator-lead.md:135` | no |
| `matrix_ok` | **no lead block names it today** | no — see below |
| `coverage_gaps` | **no lead block names it today**; retained by goal-check F5 | no — see below |
| `failures`/`suite`/`kinds` | no lead-facing block; 1, 1 and 4 observed runs | **struck** |

`matrix_ok` and `coverage_gaps` are the honest edge. A strict field-literal reading of the repaired
bar excludes them too, since neither appears in any lead block. **I closed the gap rather than
reporting it as residual:** T-01 PART 3 already had to add a passthrough line to the canonical lead
block, and it now names exactly those five — so the documentation the bar requires is created by this
plan. Until PART 3 lands they rest on `.omp/agents/harness-validator-lead.md:83`, which documents a
lead's duty to judge adequacy rather than pass/fail (the judgement is over the matrix and its gaps).
PART 3 specifies that line as a **commented** line: the D-12 reverse parser collects `^  <ident>:`,
so an uncommented one would demand a declaration and re-import the problem.

**Both guards held.** (a) `SCHEMAS["qa"]` (`validate-digest.py:193`) is untouched — no plan text
instructs otherwise, and T-01 PART 1, T-03 and T-08 now each say explicitly that `failures`/`suite`
stay required qa members and are illegitimate only on a **lead** roll-up. (b) SC-05 still asserts
one key at a time over the surviving set; no count anywhere.

## OD-3 — the field-loop sentence (PF-4d84bb7e52beff3ee62eb98a7115ae9e)

**Applied**, in T-01 PART 1. It now names `validate-digest.py:1190` (`all_fields = {**schema,
**UNIVERSAL}`) and `:1197` (every member required-when-absent, no optional branch), and states that
an optional field — PASSTHROUGH and DOCUMENTED_OPTIONAL alike — is validated **only when present**
and is **never reported absent**; the reuse is of the type/enum checking, not of the sweep. It also
names the failure the wrong reading produces: all 21 optional fields mandatory. PART 5's omission
assertions are cited as what holds the implementer to it. No residual risk.

## OD-4 — SC-11's qualifier (PF-7469688fee994f7ec08ad85dea1d1f8b)

**Applied.** SC-11's accept case reads "on a run already carrying `schema_version: 1` — an update to
an already-existing version-1 file, which is what D-11's creation floor leaves writable". No residual
risk.

## OD-5 — strike T-02: **BLOCKED, no legal route exists**

I confirmed this at source rather than on my lead's word, and **I agree with the finding.**

- `VERBS` — `plan-merge.py:1669-1680` — is exactly `apply`, `add-tasks`, `set-task-station`,
  `set-feature-station`, `set-panel`. `apply`'s own help string is "adds, never deletes"
  (`:1670`), and `:1666-1668` states add-only is a promise `apply`/`add-tasks` make.
- `sign-approval` (`:1683-1692`) writes only the approval mapping.
- `amend` (`:1695-1719`) takes `--key` restricted to `AMENDABLE_KEYS = ("tasks", "decisions")`
  (`:1232`) and **replaces ONE FIELD of ONE named item** under compare-and-swap. It cannot remove an
  item; `:1230-1231` records that it deliberately cannot reach `approval:` either.

So no verb deletes a task entry, and `abandoned` is the terminal station marker T-02 already carries
(`status: abandoned`). **T-02 is left exactly as it stands. Nothing was hand-edited.**

Options for the operator, neither taken here:

1. **Record the strike in place** — `amend` T-02's `title` and/or `intent` to say the operator struck
   it at signature. Legal today, one command, but the entry remains in the file and still counts in
   any naive task tally.
2. **Add a delete verb to `plan-merge.py`** — a separate feature, and a real design question: a
   delete verb weakens the add-only promise `:1666-1668` makes, so it would need its own guard
   (approval-pending only? id-must-be-`abandoned`? a tombstone rather than a removal?).

## OD-6 — DEC-126's falsified clause

**Verified, and nothing changed — T-09 already carries it correctly.** T-09 `files:` lists
`.harness/harness/docs/DECISIONS.md` (and the index, which its `verify:` regenerates); its `intent:`
WRITE 2 is scoped "ONE CLAUSE ONLY", names `DECISIONS.md` lines 2612–2613, and instructs the
correction that the validator lead's per-role extra is `severity_max` while `adequacy_notes` is
required of all three leads in the canonical block. I read `DECISIONS.md:2607-2617` at source: line
2612–2613 is the `needs_approval`; `severity_max` + `adequacy_notes` clause, and the reviewers' clause
at 2614–2617 that T-09 tells the doer to leave alone is indeed the one that stays true.

## Backlog B-1..B-6

**All six struck.** No task, decision, issue or note section derives from them, and they are not
recorded as deferred work anywhere.

## Traceability — re-checked after every edit

- **9 REQs, 15 SCs.** Every SC carries exactly one `verify:` (checked mechanically).
- **Every active task traces ≥1 REQ**, and every traced id exists in the brief. T-02 is excluded as
  `abandoned`, per its own intent.
- **Every REQ has ≥1 active task**: computed set difference is empty.
- **Every REQ has ≥1 SC**: REQ-01 → SC-01/02/03; REQ-02 → SC-03/11/15; REQ-03 → SC-04; REQ-04 →
  SC-05/16; REQ-05 → SC-07/08; REQ-06 → SC-09; REQ-07 → SC-10; REQ-08 → SC-11/12; REQ-09 → SC-16.

## Gate state

`check-plan-routes.py` on this plan: the four `DEC-174` carve-out DEVIATIONs plus T-10's, all
expected, and `1 violation(s)`. **That count is pre-existing and environmental, not mine** — running
the same checker against `HEAD`'s copy of this plan reports the identical `1 violation(s)`, and the
only non-task line is `DEVIATION .../FEAT-104.../.harness/team-config.yaml differs from the owner
manifest`. Nothing I changed moved it.

## Open question for the operator

**Q1 (non-blocking):** OD-5 has no legal route. Which of the two options above do you want — amend
T-02's text to record the strike in place, or leave the record as it is and treat a `plan-merge.py`
delete verb as its own feature?
