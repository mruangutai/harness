# Goal-check — FEAT-55 amended plan (cycle 8) — graded against operator intent

**BLUF.** The amended `plan.yaml` delivers the operator's stated intent. All five FIX rulings of
`notes/answers-plan-panel-20260905-c4.md` are observable at source, all four ACCEPT surfaces are
intact and their dispositions read `operator_accepted`, the other seven findings are untouched,
`check-plan-routes.py` returns **0 violations, exit 0** (my own run), and `approval:` is
`{status: pending}` with BRIEF.md unmodified. One low-severity residual, advisory only, below.

## Does this plan deliver the operator's stated intent?

**Yes.**

Graded against `.harness/notes/grilling-issue-types-2026-09-04.md` `## Settled` and the four answer
records, not against BRIEF.md. Each settled clause maps to plan content:

| Operator's settled clause | Where it lands |
|---|---|
| repo-specific type-name overrides; defaults Bug / Feature / Task | D-12 `exactly four legal keys ... Bug, Feature, Task, and the literal key parent`; T-01 §6 `returns {} for cfg={"github": {"issue_types": {"bugfix": "Defect"}}}` |
| feature and factory parents default Feature, same mechanism | D-18 `the gh-sync feature parent and the factory parent type as Feature through type_for_parent` |
| types unavailable → labels preserved exactly, one diagnostic per invocation | T-03 case C/D, T-05 case C, T-07 case C — `EXACTLY ONE stdout line matching "^gh-sync: issue types "` |
| native active → no competing bug/chore labels | SC-07's cases; T-03 case B, T-05 case B, T-07 case B |
| create-succeeds-then-type-fails → rerun classifies, never deletes or duplicates | D-10 `crash recovery is receipt-only`; T-03 case G, T-05 case E, T-07 case E |
| out of scope: adopted/source issues; no bootstrapping | D-10 `a number whose provenance is absent or adopted is never typed`; T-04 §7 |
| five creation routes (#1289) | T-04 (parent+task), T-06 (backlog), T-08 (factory parent+task) |
| DEC-138/DEC-203 authority amended with the implementation | T-11 / T-12 |

Earlier rulings (20260904, -c2, -c3) all still hold: REQ-10 present on T-07/T-08 traces, atomic
receipt write (D-13 `harness_merge.locked_update`), opt-in exempt from the configured-repository
gate (T-10 §6 `THE EXPLICIT OPT-IN IS EXEMPT`), override keys limited to four.

## Per-SC grading — PLAN phase

**What "met" means here:** nothing is built. `met` = the plan contains a task whose deliverable, when
built, produces exactly the evidence the SC's declared method demands, and that task's own gate can
go red if it does not. It is *not* a passing gate; no test in this table exists yet.

| SC | method | verdict | evidence pointer (content string → file) |
|---|---|---|---|
| SC-01 | automated/integration | met | `for c in A B C D E F G H H2 I J K` (T-03 verify) + `for c in A B C D E F G H` (T-05 verify) — plan.yaml |
| SC-02 | automated/integration | met | `for c in A B C D E F G H I J` (T-07 verify) — plan.yaml |
| SC-03 | automated/integration | met | `The null-returning fake is the case SC-03 names; the "available" fake is its positive control` (T-03 intent) — plan.yaml |
| SC-04 | inspection | met | `apply_type_args(node_id, type_id)` fed from the declared map; T-01 §10 `contains "updateIssue" and "issueTypeId"` — plan.yaml |
| SC-05 | automated/unit | met | `for w in bugfix feature logic api cross_module frontend ai_behavior docs config scaffolding infra ci bug chore enhancement` + `UNEXPECTED PASS: this test must be RED before T-02` (T-01 verify) — plan.yaml |
| SC-06 | automated/integration | met | `Defect Story Epic Maintenance` (T-01 verify loop) + `IT_defect IT_epic IT_maintenance` (T-03 verify loop) — plan.yaml |
| SC-07 | automated/integration | met | T-03 case C `label lists are exactly today's - harness plus chore ... harness plus bug` — plan.yaml |
| SC-08 | automated/integration | met | T-03 case F/K, T-05 case G/H, T-07 case I/J, each in that command's own test file — plan.yaml |
| SC-09 | automated/integration | met | T-03 case G `FAKE_TYPES=available FAKE_TYPE_APPLY=fail on the first run` + `no "issue delete" and no "issue close" argv anywhere` — plan.yaml |
| SC-10 | automated/issue_types_live | **partial** | standing record: T-09 registers the kind, T-10 writes the probe; only a live operator verdict closes it. Not re-litigated. |
| SC-11 | inspection | met | T-11 verify `grep -q "EIGHT purposes" .harness/harness/docs/DECISIONS.md` + `gen-decisions-index.py --stdout \| diff -` — plan.yaml |
| SC-12 | automated/integration | met | T-03 case H2 `the rerun backfill must skip an adopted parent forever, not once`; T-03 case J and T-07 case F for absent provenance — plan.yaml |

## The five FIX rulings — confirmed at source

| Finding | Observed content string in plan.yaml |
|---|---|
| PF-1f968f2cd73a799708e4be589d48e61b | T-03 `K. THE BACKFILL IS THE SOLE SOURCE OF A MISSING TYPE` with `FAKE_TYPES=nobug` + `github.typed["<that task id>"] = "created"`; T-05 `H. ...on this route` with `backlog-issues.json ALREADY records ... number 602 and typed false`; T-07 `J. ...on the factory route` with `factory["typed"] for that task id set to exactly the string "created"`. Each states `EVERY ISSUE THIS RUN WOULD CREATE HAS A DECLARED TYPE` / `BOTH HAVE A DECLARED TYPE`, so the creation-side refusal cannot fire; the sole undeclared type is Bug. Letters K/H/J are in each `for c in` loop and `nobug` is in each `for s in` loop. **Three distinct route shapes, not one copied.** |
| PF-e02dcbdf60fdf5eede40feb6066e8a08 | D-14 `because`: `A GraphQL createIssue with issueTypeId IS possible ... and it is DELIBERATELY UNUSED`. `so the CLI cannot set a native type at all` survives only inside the panel finding's own `summary`. D-14 `choice` unchanged (`the type is applied AFTER creation through gh api graphql updateIssue with issueTypeId`). |
| PF-452948136bf467869d223e027191ae49 | T-06 verify: `python3 tests/integration/test-gh-issue-types.py \|\| exit 1`; intent: `BOTH ARE IN YOUR VERIFY, which runs test-gh-issue-types.py itself` … `Do not rely on running it by hand.` |
| PF-62b2b8ae0acc3509b474b744469137dc | T-10 §6 carries exactly two bullets; the `query_failed` one reads `THAT ONE WORDING COVERS EVERY NON-ANSWER, and there is no second one: an authorisation error, a NOT_FOUND, and gh being unable to reach the TARGET's host at all ... ALL classify query_failed`, plus `do not add a per-host gh auth status pre-probe`. `SKIP gh cannot reach` occurs nowhere. §7 still `LIVE PASS, CAPABILITY PRESENT, CAPABILITY ABSENT or SKIP` and `add no fifth token`. |
| PF-383a1a92195cf2cdfba9828bda854195 + PF-9a71cb9a0c590b06b890ff1517b80385 | Pinned row shrank to **394 chars** and is byte-identical in T-11 §3 and T-12 §1 (I extracted both and compared sha256 — identical; the only third regex hit is T-12's own 80-char pattern literal). Durable guard: `tests/unit/test-issue-types-pin.py` in T-01 `files:`, under `tests/unit/` so `run-unit-tests.sh` runs it forever; it reports missing and drifted **separately** (`report DRIFTED PIN with both strings`, and `A single comparison of two extractions is NOT enough: with the row missing from both files, two absent values compare equal`). T-11's three greps are true of the new row (`which native issue types a repository declares`, `the native type assigned to an issue Harness created`, `EIGHT purposes`). T-01 `traces: [REQ-02, REQ-03, REQ-04, REQ-09]` — REQ-09 is truthful, the guard permanently asserts the record states the new authority. |

## The four ACCEPT rulings — surfaces unchanged

`adopted` marker intact at D-10, D-20, T-04 §7 (`records rec["typed"]["parent"] = "adopted"`), T-08 §8
(`factory.setdefault("typed", {})["parent"] = "adopted"`) and the pinning cases (T-03 H/H2/J,
T-07 D/F). T-05 case F intact: `Assert the second run makes three MORE "issue create" argv - today's
duplicate behaviour`. T-10 §6 residue intact: `gh_issue_types.type_for_parent(overrides) read from
the same harness.json`, with the TARGET-vs-configured note preserved.

Dispositions: PF-56a2ce7a…, PF-0c12a033…, PF-e27f1c30…, PF-d8a7b516… all read
`operator_accepted`; the other seven all still read `batched_to_signature_review`. The c8 diff
removes exactly four `disposition:` lines and no finding text (`git diff -U0`).

## Route checker — my own run

`python3 .claude/skills/harness/bin/check-plan-routes.py <plan path>` from the worktree root:
**0 violation(s) across 1 plan(s), exit 0.** T-01…T-11 `OK`; T-12 the expected DEC-174 line
(`declared main-session-direct (.claude/skills/harness/references/github-mirror.md ungranted)`).

## Non-goals held

`approval: {status: pending}` (loaded with `safe_load`). `git status --porcelain` shows only
`plan.yaml` and `observations/harness-pm.md` modified plus two untracked notes — BRIEF.md, every test
file and every production file untouched by the c8 pass, and untouched by me.

## Residual concerns

- **LOW, advisory, no fix cycle.** T-02's intent still reads `updateIssue is used because gh 2.92.0
  has no --type flag on issue create or issue edit, so the type can only be applied after the
  create.` That is the same overclaim the operator ruled out of D-14, and T-02's intent is the
  literal builder dispatch. It is self-correcting in place — the immediately preceding sentence says
  `issueTypeId is a measured input field of both CreateIssueInput and UpdateIssueInput` — so the
  builder cannot be misled into believing the create route impossible. Outside the ruling's letter
  (which named D-14); flagging it for the signature reader, not routing it.
- **LOW, note-only.** `notes/research-FEAT-55-planrepair-c8.md` claims the four accepted findings
  carry `authority: notes/answers-plan-panel-20260905-c4.md`. No `authority` key exists on any
  finding; only `disposition` changed. The ruling landed; the note overstates how.
