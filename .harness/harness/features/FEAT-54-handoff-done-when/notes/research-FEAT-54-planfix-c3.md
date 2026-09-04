# Plan fix c3 — the two accepted rulings applied, the grammar ruling recorded

**Both ACCEPTED rulings are in the plan and the REJECTED grammar ruling is recorded in D-10's
`because`.** Four fields changed through `plan-merge.py amend --expect-sha256` (five amends: T-09's
intent took a second pass to re-wrap a 110-col line), plus SC-04's verification method in `BRIEF.md`.
Task ids stay T-01..T-12, decision ids D-01..D-08 + D-10, `panel:` untouched (3 readers, 7 findings),
both approval blocks `pending`. `check-plan-routes.py <plan>` → **0 violation(s), exit 0** (the 8
DEVIATION lines are the pre-existing DEC-174 carve-outs). No conflict with the grilling: it demands
no automated real-corpus verification — its only nearby settled line is "making the exploratory model
benchmark a permanent automated release gate" as OUT OF SCOPE, which this change moves *towards*, not
against.

## The (g) choice: reuse the slot, do not rename

Case (g) keeps its letter. Renaming it to a named fixture case would have renumbered nothing but would
have broken every existing citation of "T-06 case (g)" — the panel finding's own summary, the c2
reviewer's note, and the product lead's observations log all name it by letter. The expected-state
paragraph is therefore **byte-unchanged**: (g) is still in the GREEN-before-and-after list, and the
new fixture case genuinely is green before the change (the fixture notes carry all five sections, so
the pre-change four-section pass reports nothing, and the pass mutates nothing). What did change is
the neighbouring sentence, which asserted the opposite of the ruling.

## Grep sweep — every real-tree / mtime / byte scan in `plan.yaml` + `BRIEF.md`

Patterns swept: `real (repo|tree|project|corpus)`, `actual project root`, `project root`, `unmodified`,
`mtime`, `byte-identical`, `corpus`.

| Site | Verdict |
|---|---|
| **T-06 case (g)** — real root scan + mtime/byte audit, permanent `INTEGRATION_SCRIPTS` case | **VIOLATES the rule — replaced** (see below) |
| **T-06 tail paragraph** — "Case (g) reads the real tree read-only" | **VIOLATES — rewritten** to assert no case reads the real tree |
| **T-07 `verify:`** — runs `bash check-state.sh` over the real repo | **clean.** A task-time verify, run once at build; not a permanent suite case, and it compares no mtime or bytes |
| **T-07 intent, expected end state** — "check-state.sh over this repository reports no line mentioning Done when, with all 141 baselined notes unmodified" | **clean.** Prose describing that same task-time verify. The untouched-corpus half is carried by SC-11 (`inspection`, a git-diff comparison), not by any byte/mtime comparison in a test |
| **T-11 `verify:`** — reads this feature's own notes on the real tree | **clean.** Task-time sweep proof; no gate run over the corpus, no mtime/byte comparison, and it is inherently scoped to notes this build wrote |
| **T-12 `verify:`** — `test-run-unit-tests-kinds.py` | **clean.** Reads config and script arrays only |
| **T-01 / T-03 cases** | **clean.** Every fixture is built under `<tmp>/.harness/harness/features/FEAT-90-fixture/`; no real-tree read |
| **T-09 `verify:`** | **clean.** Reads `.harness/harness.json` and greps one script; no corpus, no mtime |
| **SC-04** | **was `automated`/`integration` over the real corpus — re-expressed as review-time `inspection`** |
| **SC-11** | **clean.** `inspection`, `git diff`/`git ls-tree` at `review_sha` with a `comm -23` positive control — review-time, no permanent case, no mtime |
| **SC-08 "left byte-identical"** | **clean.** About comment text in gate scripts, not about note files |
| **T-09 intent "byte-identical"** | **clean.** About two JSON keys the task must not perturb |
| **`panel.findings[1]` summary** | **left byte-identical.** A finding's summary is never edited; its disposition is a later run's write |

## Post-write read-back (all quoted from disk via `amend --show` / `read`)

**T-06 intent, new (g)** (excerpt) — `sha256: c059a775e199cbde…`
> (g) A CLEAN CORPUS AND NO MUTATION, ON A FIXTURE ROOT: build a fixture corpus under
> tempfile.TemporaryDirectory holding TWO compliant notes — one whose repo-relative path IS in that
> fixture's harness.json handoff_done_when_baseline and one that is NOT, each carrying a well formed,
> fully resolving "## Done when" block — record every fixture note's bytes and mtime, run
> check-state.sh against that fixture root, and assert BOTH that no reported line mentions "Done
> when" AND that each fixture note is byte-identical and mtime-identical afterwards. … The real
> corpus at review_sha is carried by SC-04 as a recorded review-time run, not by this permanent suite;

and the rewritten tail:
> Every case, (g) included, builds its own fixture root under tempfile.TemporaryDirectory, including
> a fixture .harness/harness.json. No case in this file runs a gate over the real repository tree, and
> none compares the mtime or bytes of a real feature note.

Expected-state paragraph re-read and **unchanged**: "Cases (b), (d), (e1), (g) and (h) are expected
GREEN both before and after".

**T-09 intent** (excerpt) — `sha256` after re-wrap read back at `plan.yaml:718-722`
> contract. The entry also carries "exclude": ".claude/worktrees/**", exactly the value
> omp_session_accessor carries: all 8 existing kinds declare exclude, and a kind without it is the
> odd one out in the mapping. Do NOT add it to test_matrix and do NOT add the probe to UNIT_SCRIPTS
> or INTEGRATION_SCRIPTS: run-unit-tests.sh's probe-drift check requires exactly this shape and exits
> 2 on any other.

Re-verified at source, not taken on trust: `.harness/harness.json` holds **8** kinds, every one
carrying `exclude`; `omp_session_accessor.exclude == ".claude/worktrees/**"`.

**T-09 verify** — still a literal `|` block (`plan.yaml:669`), one line added at `:688`, every other
clause byte-identical including the trailing
`! grep -q 'probe-handoff-comprehension' .claude/skills/harness/bin/run-unit-tests.sh`:
> assert k['status']=='locally_run' and k['detect']==p and k['cmd']==p, k
> **assert k['exclude']=='.claude/worktrees/\*\*', k**
> assert 'handoff_comprehension' not in json.dumps(d.get('test_matrix')), 'kind leaked into test_matrix'

**D-10 `because` tail** — `sha256: f1c09cca7ddf438a…`, `choice` and `dec: DEC-179` untouched
> … The operator ruled at the same batched signature review of 2026-09-02, on finding PF-bd92960a,
> that the typed pointer grammar — the four authority types and the id format of each — is a STABLE
> CONTRACT: the persisted pass validates grammar only and never target existence, and any future
> rename or narrowing of an authority type or of an id format is an explicit versioned contract change
> made by the feature that makes it, not machinery this feature builds. The operator also confirmed
> (Q3) that grammar validation IS part of the persisted shape validation. This clause is a record of
> the ruling and adds no mechanism, no task, no criterion and no grammar-versioning machinery, which
> stays out of scope

**SC-04, `BRIEF.md:89-99`** — the claim's three lines are byte-identical; only the method changed:
> Verified at REVIEW TIME, not by a permanent suite case: at `review_sha`, from the repository root,
> the reviewer runs `bash .claude/skills/harness/bin/check-state.sh` and records in the review record
> its exit status and that no reported line names `Done when`. Falsified by any such line, including
> one naming a note this feature wrote. … the deterministic half of the claim — a clean corpus and no
> note mutated by the scan — is T-06 case (g) over a fixture corpus.
> **verify: inspection**

No other artifact declared SC-04's method (`grep SC-04` returns only the criterion itself, the new
T-06 cross-reference, REQ-05's `brief-sc:SC-04` example, and two fixture-content lines in T-01/T-03).

## Open

- **Ruling 3 (PF-d0ea19ff, rejected):** nothing done, by instruction. SC-14, T-03(h), T-06(h)
  byte-unchanged; no commentary added anywhere.
- The panel dispositions for PF-570b9c87 and PF-91832661 are still `open` — they are a later run's
  write, and `panel:` was deliberately not touched here.
