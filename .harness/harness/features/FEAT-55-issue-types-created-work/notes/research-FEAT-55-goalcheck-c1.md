# Goal-check — FEAT-55-issue-types-created-work — delivery, at review_sha

**All twelve success criteria are MET at the pinned commit `cd6a3c0dee795ca9261d0ecf2e67df09d2e47b86`
(branch `feat/issue-1289-issue-types`, merge-base `eb9d044e`), and all eleven requirements are
traced to shipped, verified code — the feature delivered its goal.**

Every `verify: automated` criterion was graded by RUNNING its test file with `env -u
HARNESS_AGENT_TYPE`, capturing exit status and counting `^FAIL ` lines; every `verify: inspection`
criterion was graded by reading content at the pinned sha with `git show cd6a3c0d:<path>`. No
criterion was graded by judgement where its method names a mechanical check. SC-10 is graded on
operator ruling **F-03** (`notes/answers-build-blockers-20260905.md`), with its mechanical half
re-confirmed at the sha.

`git -C <worktree> status --porcelain` **at the start of this segment**:
`` M .harness/harness/features/FEAT-55-issue-types-created-work/feature.json`` — one modified
run-state file written by the orchestration tier, **not** source, tests, plan.yaml or BRIEF.md. No
other entry.

**At the end of this segment** the same command adds only: my two writes (`notes/research-FEAT-55-goalcheck-c1.md`,
`observations/harness-pm.md`) and four files belonging to the concurrently running review panel
(`observations/harness-qa.md` and three `notes/review-*.md`), which this segment neither read nor
graded. `feature.json` remains the only modification outside `notes/` and `observations/`; no
source file, test, `plan.yaml`, `BRIEF.md` or `STATE.md` is dirty.

## Suite runs (this segment, at the pinned sha)

| invocation | exit | `^FAIL ` |
|---|---|---|
| `tests/unit/test-issue-types.py` | 0 | 0 |
| `tests/unit/test-issue-types-pin.py` | 0 | 0 |
| `tests/integration/test-gh-issue-types.py` | 0 | 0 |
| `tests/integration/test-gh-backlog-issue-types.py` | 0 | 0 |
| `tests/integration/test-factory-issue-types.py` | 0 | 0 |
| `tests/integration/test-gh-sync.py` (compat control) | 0 | 0 |
| `tests/integration/test-factory-decompose.py`, `test-factory-integration.py`, `tests/unit/test-factory-gh.py`, `tests/integration/test-anchor-directions.py` | 0 | 0 |
| `tests/manual/probe-issue-types.py` (read-only default, D-19) | 0 | `CAPABILITY ABSENT mruangutai/harness declares no native issue types` |

Note for the record: `test-factory-gh.py` lives under `tests/unit/`, `test-anchor-directions.py`
under `tests/integration/` — the reverse of the paths the dispatch's measured-claim list implies.
Both are green where they actually live.

## Per-SC verdicts

| SC | method | verdict | evidence (pinned sha) |
|---|---|---|---|
| SC-01 | automated / integration | **MET** | per-issue, not totals: `test-gh-issue-types.py` CASE A (parent `IT_feature`; T-01 `IT_bug`; T-02/T-03/T-04 `IT_task` — five separate assertions); `test-gh-backlog-issue-types.py` CASE A (bug→`IT_bug`, chore→`IT_task`, enhancement→`IT_feature`, one assertion each) |
| SC-02 | automated / integration | **MET** | `test-factory-issue-types.py` CASE A — parent via `I_node41`, T-01/T-02/T-03 via `I_node42/43/44`, one assertion per issue; T-03 pins D-18 (`feature` change_type → `IT_task`) |
| SC-03 | automated / integration | **MET** | null-`issueTypes` fake: gh CASE C (five issues, exact label lists, zero `updateIssue`, exactly one `^gh-sync: issue types ` line), backlog CASE C (three issues), factory CASE C (four issues, exactly one `^factory: issue types `). Positive control = the `FAKE_TYPES=available` fake in the same files (CASE A/B); byte-identical-labels control = `test-gh-sync.py`'s untouched label assertions, green |
| SC-04 | inspection | **MET** | every type id reaching `apply_type_args` is a lookup in `declared`, which `classify_capability` builds from the repository's own GraphQL response (`gh_issue_types.py:105-135`): `gh-sync.py:997-998`, `:1004-1005`, `:1703-1704`; `factory_decompose.py:440`, `:446`. No `IT_`-style literal and no pattern-derived id exists anywhere under `.claude/skills/harness/bin/` at the sha; node ids come from `node_id_args` (`gh_issue_types.py:136-137`, an API read), never from a string pattern |
| SC-05 | automated / unit | **MET** | `test-issue-types.py`: twelve change_type assertions (ok 1-12), three natures (ok 13-15), parent (ok 16), and `UnknownWorkNature` raised + message content for both resolvers (ok 17-22). Red-first shown: `receipt-harness-backend-dev-T-01-c1.md` records the RED run under T-01's `UNEXPECTED PASS` gate; independently corroborated — `gh_issue_types.py` does not exist at merge-base `eb9d044e` |
| SC-06 | automated / integration | **MET** | gh CASE E — parent→`Epic`, bugfix→`Defect`, config/logic/feature→`Maintenance` (declared names, not defaults, on both a task sub-issue and a parent); factory CASE D — `Bug`→`Story` and `parent`→`Story` with `Task` deliberately un-overridden as the negative control |
| SC-07 | automated / integration | **MET** | active mode, all five routes: gh CASE B (no `--label bug`/`chore`, `--label harness` on every create, `--milestone FEAT-…` intact), backlog CASE B, factory CASE B (`feature:<FEAT>` present; `factory:claimed` exactly where it is today). Compatibility mode restores both labels: gh CASE C/I, backlog CASE C, factory CASE C |
| SC-08 | automated / integration | **MET** | asserted per command in that command's own file: `gh-sync open` CASE F and K, `gh-sync backlog` CASE G and H, `factory_decompose` CASE I and J. Each asserts non-zero exit, zero `issue create`, zero `updateIssue`, and a message naming both the missing type name and `github.issue_types` |
| SC-09 | automated / integration | **MET** | gh CASE G, backlog CASE E, factory CASE E — provenance stays `created`/`false` after a failed apply, rerun makes no second create, no close, no delete, applies the type to the recorded node id, and only then promotes to `True` |
| SC-10 | automated / issue_types_live | **MET, on operator ruling F-03** | `notes/answers-build-blockers-20260905.md` item **F-03** (2026-09-05): the recorded capability-absent verdict satisfies the signed criterion. Recorded run: `notes/qa-2026-09-05-01-validator.md:143-148`; reproduced this segment (`rc=0`, `CAPABILITY ABSENT mruangutai/harness …`). Mechanical half confirmed at the sha: `tests/manual/probe-issue-types.py` present, and `.harness/harness.json` `test_kinds.issue_types_live` is `status: locally_run` with `cmd: tests/manual/probe-issue-types.py` (non-null). The live pass against an organization-owned, Issue-Types-enabled repository is **backlog per F-03, not a gap** |
| SC-11 | inspection | **MET** | `DECISIONS.md:3029-3037` (DEC-138: the read-back is authorised) and `:3038-3056` (**Issue type** — native types supersede the two derived labels, with the compatibility fallback stated); `:6089-6103` (DEC-203's eighth read-back purpose). Index matches: `gen-decisions-index.py --stdout \| diff - DECISIONS-INDEX.md` → empty, exit 0. Standing guard `test-issue-types-pin.py` green (the row is identical in `github-mirror.md`) |
| SC-12 | automated / integration | **MET** | gh CASE H/H2 (adopted `--parent` 4242 never typed on the adopting run or the rerun, provenance `adopted` on both; `source_issues` #100 and #200 each asserted separately) and CASE J (absent provenance: legacy 9001/9002 untyped, no `typed` entry, on first run and rerun); factory CASE F (adopted parent) and CASE H (absent provenance, with the un-recorded tasks still typed to prove the bound is not a dead run). The per-case red gate exists for each file — T-03 loops `A B C D E F G H H2 I J K`, T-05 `A…H`, T-07 `A…J` — so an omitted case fails as loudly as a failing one |

No SC came back UNMET, so there is no wrong-versus-unproven call to make and no owning T-NN to
route. No criterion's grade rested on a drifted count or a moved line anchor.

## REQ coverage — REQ-01..REQ-11

**REQ-11 is included and was added to the enumeration**: the dispatch named REQ-01..REQ-10, but
BRIEF states eleven requirements and REQ-11 (host-only probe registered as a runnable test kind) is
in scope and traced.

| REQ | traced tasks | verified by |
|---|---|---|
| REQ-01 all five creation routes type | T-03, T-04, T-05, T-06, T-07, T-08 | SC-01, SC-02 — per-issue assertions on all five routes |
| REQ-02 capability per target repo, ids never inferred | T-01, T-02, T-04, T-08 | SC-04 inspection + unit ok 34-49 (`classify_capability`, `capability_query_args` pinning `-f owner=`/`-f name=` per D-22) |
| REQ-03 defaults + per-repo name overrides | T-01, T-02, T-03, T-04, T-07, T-08 | SC-05 (unit ok 1-16), SC-06 |
| REQ-04 mapping total, unknown reported | T-01, T-02, T-05, T-06 | SC-05 (twelve + three, `UnknownWorkNature` ok 17-22) |
| REQ-05 compat mode preserved, one diagnostic, never fails | T-03..T-08 | SC-03; gh CASE D/I, factory CASE G (rerun creating nothing still prints exactly one) |
| REQ-06 competing labels suppressed, operational labels intact | T-03..T-08 | SC-07 |
| REQ-07 refuse before creating anything | T-03..T-08 | SC-08, per command |
| REQ-08 not mirrored until typed; safe rerun | T-03..T-08 | SC-09 |
| REQ-09 DEC-138 and DEC-203 amended | T-11, T-12 | SC-11 + `test-issue-types-pin.py` standing guard |
| REQ-10 never retype what Harness did not create | T-03, T-04, T-07, T-08 | SC-12 (its only falsifiable grading, per BRIEF) |
| REQ-11 host-only probe registered as a runnable kind | T-09, T-10 | SC-10 — probe present at the sha, `issue_types_live` `locally_run` with non-null `cmd`, verdict recorded and reproduced |

No requirement lacks a traced, verified task.

## Recommendations (not adopted — BRIEF is approval-gated)

- **R-1.** The `Feature` override key is legal (`gh_issue_types.LEGAL_OVERRIDE_KEYS`) but no
  integration fixture renames it on the **backlog enhancement** route; it is covered only by the
  shared `_resolve` path proven at unit level and by the `parent` key at integration level. SC-06
  binds "a task sub-issue and a parent", both fixtured, so this is not an SC gap — it is a thin
  spot. Adding it would be one case in `test-gh-backlog-issue-types.py`. **Do not treat this as an
  emergent criterion**; it is a suggestion for a later feature or a backlog item.
- **R-2.** F-03's backlogged live probe against an organization-owned, Issue-Types-enabled
  repository is the only thing that can falsify the fake's API shape (BRIEF `## Verification gaps`,
  "What the fake cannot prove"). Worth an issue so it is not lost with this feature's context.
