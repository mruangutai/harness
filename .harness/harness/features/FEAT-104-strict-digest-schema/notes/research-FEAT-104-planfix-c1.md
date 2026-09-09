# Plan fix — FEAT-104 — cycle 1

**BLUF. All six must_fix findings plus F8 and F9 are closed, and F7 and F10 with them.** The legal
digest key set is now derived from the **documented** persona blocks, not from observed traffic: the
re-derivation found **16** documented-but-undeclared fields, one more than the goal-check's 15
(`a11y`, `.omp/agents/harness-ui-reviewer.md:111`). They land in a new optional typed
`DOCUMENTED_OPTIONAL` table keyed by **raw** agent type (D-10) — not by the canonical persona, because
the three reviewer agents collapse to one at `validate-digest.py:243-244`, so only the raw key keeps
`mode` illegal on a security review. The agreement between documentation and declaration is now
**mechanical** (D-12, SC-16, T-01 PART 5): it reuses the `CONTRACT_SOURCES` map and `documented_block`
parser that already exist at `tests/integration/test-validate-digest.py:297-314` and `:281-286`, so
this is a case, not a new subsystem. REQ-02 binds on a creation floor (D-11, SC-15). T-01 and T-02 are
one task; T-02 is at station `abandoned`, kept so the merge is visible. SC-14 is deleted.
`check-plan-routes.py` reports the same **1** pre-existing violation (the Q7 manifest deviation) and
no new one. `approval:` is `pending`.

**Two mechanical corrections to the dispatch, neither a ruling deviation.** (1) `plan-merge.py apply`
exits **7 CONFLICT** on a changed value under an existing id — it adds, never replaces. Every
modification here went through `plan-merge.py amend --expect-sha256 --value-file`, which is the same
tool and the same lock; `apply` was used only for the three new decision ids, and `set-task-station`
for T-02. No Edit, no Write, no redirect touched `plan.yaml`. (2) `.claude/agents/*.md` is **generated**
from `.omp/agents/` by `sync-agent-adapters.py`, which copies the body wholesale (`:191-226`), so T-01
and T-03 now edit the `.omp/` source and regenerate rather than hand-editing both twins.

## F1 — critical — closed

**What changed.** The legal set gains `DOCUMENTED_OPTIONAL.get(raw_persona, {})` (T-04 `intent:`), and
the table itself is declared in T-01 PART 1. Requiredness was **not** used: D-10 records why. SC-05's
grading set is re-based on the documented blocks and names them as its source; SC-02 now requires each
persona's accepting fixture to be built from its documented block's **full** field set, which is the
blindness the goal-check found. SC-16 is new and is the mechanical assertion, with its discrimination
demonstrated in-process rather than asserted. T-01 also corrects one value-level disagreement found
during the re-derivation: `.omp/agents/harness-validator-lead.md:135` documents
`severity_max: info|...` and `info` is not in `SEV` (`validate-digest.py:36`), so the documented value
is one the validator rejects today.

**Carriers.** REQ-04 (reworded), REQ-09 (new), SC-02, SC-05, SC-16, D-10, D-12, T-01, T-04.

**Residual risk.** SC-16 compares **keys**, not values. The `info` correction is made by hand in T-01
and pinned by one named assertion; a *future* enum divergence in a documented block is not caught
mechanically. Widening the reverse case to parse pipe-alternation values is a clean follow-up and is
deliberately not in scope here.

### The re-derived enumeration — 16 fields, from the documented blocks

Sources are `.omp/agents/` (the `.claude/agents/` copies are generated). Every field below returned
**0** occurrences from `grep` over `validate-digest.py` at worktree HEAD `7e0c2ec1`.

| raw persona | documented field | `file:line` | declared type |
|---|---|---|---|
| harness-code-reviewer | `spec_violations` | harness-code-reviewer.md:90 | list |
| harness-code-reviewer | `human_commits_in_scope` | harness-code-reviewer.md:94 | list |
| harness-security-reviewer | `in_scope` | harness-security-reviewer.md:92 | bool |
| harness-security-reviewer | `scope_reason` | harness-security-reviewer.md:93 | str |
| harness-security-reviewer | `threat_model` | harness-security-reviewer.md:99 | list |
| harness-ui-reviewer | `mode` | harness-ui-reviewer.md:102 | `{A,B}` |
| harness-ui-reviewer | `in_scope` | harness-ui-reviewer.md:103 | bool |
| harness-ui-reviewer | `states_unspecified` | harness-ui-reviewer.md:109 | list |
| harness-ui-reviewer | `contract_violations` | harness-ui-reviewer.md:110 | list |
| harness-ui-reviewer | `a11y` | harness-ui-reviewer.md:111 | list |
| harness-qa | `kinds` | harness-qa.md:91 | list |
| harness-qa | `sc_evidence` | harness-qa.md:93 | list |
| harness-documentor | `stale_found` | harness-documentor.md:61 | list |
| harness-dev-ops | `test_kinds_written` | harness-dev-ops.md:99 | list |
| harness-visual-designer | `needs_prototype` | harness-visual-designer.md:79 | bool |
| harness-visual-designer | `why` | harness-visual-designer.md:80 | str |
| harness-visual-designer | `prototype` | harness-visual-designer.md:82 | str, `none` via NULLABLE |

Seventeen rows, **16 distinct names** (`in_scope` is documented by two agents). **Clean** — documented
set equals the declared set already: `pm` (`harness-pm.md:85-99`), `dev`
(`harness-digest-dev/SKILL.md:15-32`, the canonical copy for all four devs), `orchestrator`
(`harness-orchestrator.md:129-140`), and `lead` (`harness-team/SKILL.md:237-258`, plus the per-lead
extras `needs_approval` at `harness-product-lead.md:90` and `severity_max` + `adequacy_notes` at
`harness-validator-lead.md:135-136`, all three of which the plan declares).

## F2 — high — closed

T-01 and T-02 are one task landing as one commit (Q4). T-01's `verify:` is now satisfiable at its own
completion: `ALL PASSED`, plus `adequacy_notes`, plus the SC-16 ok line, plus `DOCUMENTED_OPTIONAL` in
the validator, plus `^  adequacy_notes:` in the lead block, plus `sync-agent-adapters.py --check`.
`run_documented_contract_cases` passes because PART 3 is inside the same task. T-02 is `abandoned`
with an intent that says why and forbids dispatch; `T-03.depends_on` moved from `[T-02]` to `[T-01]`,
and REQ-07's task trace is T-01 (T-02's `traces:` row is retained only so the abandoned record stays
well-formed and is excluded from the tables below).

**One deliberate reading of Q4.** The substance lands as one commit; the base-revision pin (F4) is a
second commit touching one note file, because a commit cannot contain its own id.

## F3 — high — closed

**Mechanism (D-11), T-06 CLAUSE B.** `check-domain.sh` refuses the **creation** of a run `state.yaml`
whose write payload declares `schema_version` absent, non-integer, or below 2 — same write-payload path
DEC-160 already owns, keyed on the target not existing on disk.

**How the two coexist without contradiction.** They quantify over different sets. SC-11 grades a
`steps[]` entry inside a file that *already declares* version 1 and keeps it **accepted**; the floor
grades only the *creation event* of a file that does not exist yet. No historical file is read, written
or reclassified, so REQ-08 does not weaken. An **update** to an existing version-1 file is untouched by
both clauses, which is also what lets a run already in flight when this lands finish. SC-15's fourth
fixture is exactly that case, and it is what reddens if a doer keys the floor on the write instead of
on the creation.

**Residual risk.** A lead working from an older *preloaded* copy of `harness-team/SKILL.md` would seed
1 and be refused. T-06's refusal therefore names the seed instruction by path, and no script seeds the
value — grepped: nothing under `.claude/skills/harness` writes a run `state.yaml` `schema_version`, the
lead writes it by hand per `harness-team/SKILL.md:54`, which T-05 updates.

## F4 — med — closed

T-01 PART 6 writes `git rev-parse HEAD` of its own commit — a bare 40-character line — to
`notes/base-revision-pre-T-04.txt` (a tracked file, Write tool, `bash-write-guard.sh` denies a
redirect), and that file is in T-01's `files:`. T-08 reads the id from there and **re-derives both
sides** before using it, as does T-08's own `verify:`: 40 hex characters; `git cat-file -e` resolves it;
`git show <sha>:validate-digest.py` **contains** `DOCUMENTED_OPTIONAL` (T-01 is in) and **does not
contain** `undeclared digest key` (T-04 is out). The two greps are a positive/negative pair on the same
blob, so an empty or wrong blob fails the first rather than passing the second.

`undeclared digest key` replaces `unknown key` as T-04's message literal deliberately: `unknown keys
are ignored` already appears in a comment in `validate-digest.py` (2 occurrences), so the old literal
could not tell the new message from the old comment. All three new literals — `undeclared digest key`,
`schema_version floor`, `every documented key is declared` — return 0 occurrences today.

## F5 — med — closed. **Rows moved: 4.**

The triage row was wrong, and so was the bar that produced it. D-02 now reads: a field earns a
`PASSTHROUGH` row when it is **already declared for another persona** — a `SCHEMAS` member or a
`DOCUMENTED_OPTIONAL` entry — and is seen riding up a lead roll-up; **occurrence count decides
nothing**, and a field declared and documented nowhere is drift whatever its count.

Re-checking every drift row against `UNIVERSAL` ∪ every `SCHEMAS` persona ∪ `{headline}` ∪ the reviewer
inline extension ∪ the documented blocks, **four rows move** out of drift and into `PASSTHROUGH["lead"]`:

| key | triage row | why it is not drift | declared type |
|---|---|---|---|
| `coverage_gaps` | `triage-c0.md:55,62` (2 runs) | required member of `SCHEMAS["qa"]`, `validate-digest.py:193` | list |
| `failures` | `triage-c0.md:72` (1 run) | required member of `SCHEMAS["qa"]`, `validate-digest.py:193` | int |
| `suite` | `triage-c0.md:72` (1 run) | member of `SCHEMAS["qa"]`, `["dev"]`, `["dev-ops"]` | `{pass,fail}` |
| `kinds` | `triage-c0.md:61` (4 runs) | documented at `.omp/agents/harness-qa.md:91`, so `DOCUMENTED_OPTIONAL` under D-10 | list |

`PASSTHROUGH["lead"]` therefore has **eight** rows, and SC-05 and T-08 say eight, not four. `tree_clean`
(4) and `mutants_restored` (4) **stay** drift and were previously right for the wrong reason: they clear
the old 3+ bar but are declared and documented nowhere. No other drift row matches a declared or
documented name — `cycles` ≠ `cycles_used`, `review_sha_examined` ≠ `reviewed`, `expertise_full` ≠
`expertise_update`, `feature_id` ≠ `feature`, `sc_count`/`req_count`/`task_count`/`decision_count` ≠
`tasks`/`decisions`, and the four `kind*` variants are none of `kinds`.

## F6 — med — closed

T-09 now makes **two** writes to `DECISIONS.md`. WRITE 1 is the new entry, unchanged in kind. WRITE 2
corrects the single clause at `DECISIONS.md:2612-2613` that D-03 falsifies: `adequacy_notes` is named
there as the validator lead's per-role extra, and it is now required of all three leads in the canonical
`harness-team` block. One clause, no renumbering, no dated note, no other entry, and the reviewers'
clause at `:2614-2617` stays exactly as it is because it is true. `DECISIONS.md` and
`DECISIONS-INDEX.md` were already in T-09's `files:`; the station stays `team`/`harness-documentor`,
which the checker confirms is granted. **The signature packet must flag this as decision-record-touching**
— BRIEF `## Constraints` carries the DEC-205 line that says so.

## F8 — low — closed by an explicit acceptance

The worktree-scoped default baseline path is **accepted**, and SC-12 now says so: the criterion is
graded inside the ship-decision window while the worktree stands, and a post-merge re-run passes the
owner-root path as `argv[1]`. The baseline file is tracked and merges to `main`, so the pin outlives the
worktree even though the default does not.

## F9 — low — closed by deletion

**SC-14 is deleted.** It asserted that every run `state.yaml` at the owner root still parses; no task
writes a historical file, and SC-12's sha256 manifest is strictly stronger — byte identity implies
parseability. A criterion no plausible wrong implementation can redden is a gate that teaches the
factory to ship (principle 7), so it is removed rather than kept as cheap insurance. REQ-08's traces
are re-checked and intact: SC-11 and SC-12 both carry it. A strengthening was considered and rejected —
"every run created during this feature declares version 2" would redden on concurrent sibling runs
rather than on this feature's behaviour, and SC-15 tests the floor directly instead.

## Also — the `partial`/`weak` criteria, re-checked

| SC | cycle-0 state | now |
|---|---|---|
| SC-02 | yes, but blind to F1 | strengthened: the accepting fixture is built from the documented block's full field set |
| SC-05 | **weak** — graded against the plan's own triage | re-based on the documented blocks, named as the source, one assertion per key |
| SC-09 | **pin, not proof** | kept, and the reason is now written into the criterion: it is a pin, and it discriminates against the plausible wrong implementation — T-04 placing the check *before* the `stop_hook_active` guard at `validate-digest.py:1744` reddens it. D-07 is deliberate; no teeth are added |
| SC-13 | n/a (uat) | unchanged (Q5). DEC-174 admits no substitute |
| SC-14 | **weak** | deleted, above |

**F7 (low) closed too:** T-07's `verify:` greped its own suite's output for `schema_version`, which a
case merely *named* for the version satisfies. It now greps for `undeclared step key` in both the output
and `check-state.sh` — the same vocabulary T-06's refusal uses, 0 occurrences today.
**F10 closed:** T-01 cites `harness-team/SKILL.md:237-258`; the drifted `238-249` is gone.

## Traceability, both directions, after the edits

| REQ | SCs | Tasks |
|---|---|---|
| REQ-01 | 01, 02, 06, 07, 08 | T-03, T-04, T-08, T-09 |
| REQ-02 | 03, 11, 15 | T-05, T-06, T-07, T-09 |
| REQ-03 | 04 | T-03, T-05, T-06, T-09 |
| REQ-04 | 02, 05 | T-01, T-04, T-08 |
| REQ-05 | 08 (01/03 name the key) | T-04, T-06 |
| REQ-06 | 09 | T-04, T-09 |
| REQ-07 | 10 | T-01, T-09 |
| REQ-08 | 11, 12 | T-05, T-06, T-07, T-10 |
| REQ-09 | 16 | T-01 |

| Task | REQs |
|---|---|
| T-01 | 04, 07, 09 |
| T-03 | 01, 03 |
| T-04 | 01, 04, 05, 06 |
| T-05 | 02, 03, 08 |
| T-06 | 02, 03, 05, 08 |
| T-07 | 02, 08 |
| T-08 | 01, 04 |
| T-09 | 01, 02, 03, 06, 07 |
| T-10 | 08 |

No orphan in either direction. SC-13 traces to no task by construction (uat, operator-executed). T-02
is excluded: station `abandoned`, never dispatched.

## The DAG after the merge

Edges: `T-10←[]`; `T-01←[T-10]`; `T-03←[T-01]`; `T-04←[T-01,T-03]`; `T-05←[T-03]`; `T-06←[T-05]`;
`T-07←[T-05]`; `T-08←[T-04,T-06]`; `T-09←[T-04,T-06,T-07,T-08]`. **Acyclic.**

**Topological order: `T-10, T-01, T-03, T-04, T-05, T-06, T-07, T-08, T-09`.**

T-03 sits between T-01 and T-04 and touches no `.py` file, so the F4 pin taken at T-01 still resolves to
a `validate-digest.py` blob that contains T-01 and not T-04.

## Gate output — verbatim, run after the plan edits

    1 violation(s) across 5 plan(s)   (EXIT=1)

The single violation is the **pre-existing** manifest deviation: the worktree's
`.harness/team-config.yaml` differs from the owner root's. Q7 — the operator's item; nothing here
touches it. DEVIATION lines for T-04, T-06, T-07, T-08 and T-10 are the intended DEC-174 carve-out
shape. T-01, T-02, T-03, T-05 and T-09 report `OK`. **No new violation.**
