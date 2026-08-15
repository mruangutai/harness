# QA gate — FEAT-11 T-01 — test-matrix over the pinned diff

**PASS.** Pin `5c433f2` verified to contain the T-01 work and to equal the working tree. Both
required kinds (`unit`, `integration`) ran green with real per-kind counts, not just the
task-local verify. Four Q3(b) mutants all reddened, including the org dead-branch mutant the
plan's own signed prose flagged as the discriminating case (three diagnosed by named assertion,
two by suite crash). Q1 surfaces a real, actionable consequence of the signed D-03 design: a
constructed partial-success GraphQL envelope reaches `item-edit` and writes — recorded as a signed
residual, per the dispatch's framing, not a defect. Q2's two envelope shapes are both unreachable
from this query document against a conformant GraphQL server (fragment-boundary argument, checked
not assumed); the `{"data": null}` shape stays a live, low-severity, write-safe residual.

## Step 0 — pin integrity

- `git rev-parse 5c433f2c52ae2c6711c4c439d26e2c0620000540^{commit}` resolves; it is also `HEAD` on
  `feat/FEAT-11-graphql-field-resolve`.
- `git diff --stat 8dedeae..5c433f2` shows **six** files: the three T-01 surfaces
  (`factory_gh.py`, `test-factory-gh.py`, `test-factory-integration.py`) plus `STATE.md`,
  `feature.yaml` and the build receipt — the latter three are `.harness` bookkeeping written by
  the orchestrator/eng-lead, not code, and require no test kind.
- `git status --porcelain -- .claude/skills/harness/bin/` is **empty** — tree equals pin exactly
  over the surface I gate. All results below are claims about the pinned commit, not a diverged
  tree. (The eng digest's "no commit" note describes the state *before* the orchestrator's commit
  landed; it is stale, not contradictory.)

## Task verify — corroboration

Loaded `plan.yaml` `tasks[0]["verify"]` via `harness_yaml.load_plan` and diffed it byte-for-byte
against the dispatch text — identical. Ran the **loaded** value: `PASS`, exit 0.

## Matrix — per-kind results

`change_type: bugfix`. `test_matrix.bugfix` = `always: [unit]` + bug-class kind = `integration`
(SC-09's evidence lives only in `test-factory-integration.py`, which is in `INTEGRATION_SCRIPTS`,
not `UNIT_SCRIPTS`). Floor: `unit` + `integration`. Nothing beyond the floor was warranted — the
change has no UI, no eval, no new external dependency surface.

| kind | cmd | state | result |
|---|---|---|---|
| unit | `run-unit-tests.sh --kind unit` | satisfied | 10/10 scripts PASS; `test-factory-gh.py` 118/118, all others green (33, 56, 30, 172, 77, 45, 13, 15, 10 checks) |
| integration | `run-unit-tests.sh --kind integration` | satisfied | 12/12 scripts PASS; `test-factory-integration.py` **97/97** — this is the standing-gate integration KIND run, not just the task verify's direct invocation |

No stray `test-*.py` in `bin/` (22 files, matches the 10+12 union) — the predicted drift-detector
obstacle did not fire; both kind commands ran clean, no misconfiguration.

`matrix_ok: true`. Denominator (P-04): 1/1 diffed tasks (T-01) had a kind requirement, and both
required kinds (`unit`, `integration`) ran and are green for it.

**No live `gh` call anywhere in either bucket** — checked before running, and re-checked across
the full integration bucket after the advisor flagged that my first pass grepped only
`test-factory-integration.py`. `test-factory-integration.py` routes through `FACTORY_GH` pointing
at a fake binary (`:315-317`). Across the other 11 integration scripts, the only `gh`-shaped
reference is `test-gh-sync.py`, which points `GH_SYNC_GH` at a stub binary under `tmp/gh`
(`:103,154,172,179`) — also fully faked, no network path. No other integration script references
`gh` at all.

## SC coverage

| SC | covered_by | evidence |
|---|---|---|
| SC-01 | `uat` | operator-run, board 6, not mine to run or close |
| SC-02 | unit | quoted `"field-list"`/`"project", "view"` absent from `factory_gh.py` and `test-factory-integration.py` (grep, 0 hits each — verified directly); one `gh api graphql` call asserted at `test-factory-gh.py:288-294` |
| SC-03 | unit | `factory_gh.py:202-219` `_FIELD_QUERY`; regex guard `test-factory-gh.py:310,312,314` on the argv-emitted query text — confirmed by mutant 3 (over-scope shape reddens) |
| SC-04 | unit | field-absent/option-absent: `test-factory-gh.py:326-335` (option), `:466-472` (field-not-single-select) — both name the value and both D-04 strings confirmed rendered literals, not braced templates |
| SC-05 | unit | `test-factory-gh.py:427-434`, both fixtures (`label` iterates exit-1 and `GRAPHQL_ORG_OK_JSON` at `:85`/`:415`) — dead-branch mutant 5 (removing the `__typename` check) reddens via an unexpected `item-edit` call, proving this test discriminates |
| SC-06 | unit | `test-factory-gh.py:447-453` board-absent case, distinct message from org case |
| SC-07 | unit | zero item-edit assertions present across every failing case (`:328`, `:408`, `:429`, `:449`, transport-failure case) |
| SC-08 | unit | `test-factory-decompose.py`/`test-factory-claim.py`/`test-factory-land.py` sha256-pinned unedited (task verify, all 3 hashes matched) **and** exercised for real via `test-factory-integration.py` (subprocess-level, no module patch) — A-1's correction from plan review holds |
| SC-09 | integration | `test-factory-integration.py` 97/97 green **on the integration KIND command**, not merely the task verify — this is the gap the dispatch called out, now closed with a real run |
| SC-10 | unit | positive clause: `test-factory-gh.py` bare-owner/board/field assertions throughout (`str(exc)` content, not label strings — read directly, not relayed); negative clause ("never `api graphql`"): `:335`, `:410`, `:434`, `:453`, transport-failure case. Holds for every response the query document can actually produce (see Q2 below); the `{"data": null}` shape is safe but diagnostically imprecise |
| SC-11 | unit | `test-factory-gh.py:406-410` unknown-owner, distinct from org and board-absent |
| SC-12 | unit | `test-factory-gh.py:466-472` field-not-single-select uses the empty-dict fixture and asserts the same error as field-absent |

## Q3 — assertions: discriminating, or merely green?

**(a) Readable now — pass.** Both D-04 freeze assertions (`test-factory-gh.py:332`, `:468`) are
rendered literals (`"field Station on owner project 3 does not offer it"`,
`"field-list for owner project 3 does not offer it"`), not braced templates. Grepped the file for
`{field}`/`{owner}`/`{number}` inside an assertion — none found.

**(b) Mutants — all four reddened**, run in scratchpad against a copy of `factory_gh.py` +
`test-factory-gh.py` + their two local deps (`factory_cli.py`, `gh_issues.py`):

| mutant | reddened | manner |
|---|---|---|
| reword `next_step` at branch (d) (`field-list for...`) | yes — 2/118 failing | **diagnosed**: named `check(...)` failures |
| reword `next_step` at option-not-offered raise (`field {field} on...`) | yes — 1/118 failing | **diagnosed**: named `check(...)` failure |
| `_FIELD_QUERY` → `fields (first: 100) { nodes { ... } }` (over-scope, space defeats substring) | yes — 3/118 failing | **diagnosed**: the three failures are exactly the three named regex checks (`test-factory-gh.py:310/312/314`), confirming the guard fires on this shape, not on incidental breakage |
| branch (d) `if not field_obj:` → `if field_obj is None:` (empty-dict case) | yes | **crashed**: `KeyError: 'id'` inside `_project_field_resolve`, uncaught — the suite halts, it does not report a named failing check |
| remove `__typename` check from success path (dead-branch defect) | yes | **crashed**: `AssertionError: recorder ran out of results` — the mutant proceeds to an **unexpected `item-edit` call** against the exit-0 org fixture, exhausting the fixture's canned result list. This is the exact defect D-03/SC-05(b) exist to catch, and the fixture catches it, but by exhaustion rather than a named assertion |

The distinction matters: the first three are diagnosed (a specific `check(...)` names what broke);
the last two are detected only by the suite crashing outright. Both count as "reddened" per the
task's requirement, but a future regression in either shape would produce a traceback to debug
rather than a labeled assertion failure — worth a follow-up if these paths get touched again.

Eng-lead's "the skip cannot happen on a green run" claim about the over-scope guard sitting inside
`if set_exc is None:` (`test-factory-gh.py:290`) — verified by the mutant run above: the guard
*did* fire (mutant 3), so the branch is reachable on this suite's own success path, not merely
reasoned to be.

## Q1 — the D-03 partial-success hole, measured

Constructed the envelope the plan's transport table has no row for: exit 1, stdout parses to a
mapping with `data` complete (no null anywhere) and `errors` non-empty. Fed it through a scratchpad
probe importing `factory_gh` directly (stubbed `subprocess.run`).

**Result: `project_field_set` returns successfully and DOES call `item-edit`.** Two calls recorded:
the graphql call, then `['gh', 'project', 'item-edit', '--id', 'ITEM1', '--project-id',
'PVT_kwFAKE', '--field-id', 'F1', '--single-select-option-id', 'O1']`.

This is worse than a returned success that is only read — it is a write performed on a call `gh`
itself reported as failed. As the dispatch instructed, I am receiving this as a consequence of the
signed D-03 (diagnose any exit-1 stdout carrying a `data` key as the same walk), not as a build
defect — the member implemented D-03 exactly as written. Whether this shape is reachable in
practice: GraphQL partial-success (data present, some field null-propagated, `errors` non-empty)
is a documented real behavior of the spec, and this query has exactly one leaf selection set
(`repositoryOwner → projectV2 → field`) with no field capable of null-propagating without making
an ancestor null too under GraphQL's null-propagation rule — so for *this specific query shape* I
believe the hole is not reachable from a real `gh` response, only from a hand-built stub. I cannot
prove that from a static read alone since the JS/GraphQL spec's propagation is a language-level
guarantee, not one this codebase enforces. **Recommendation: backlog, not a fix cycle** — record
it as a known, accepted risk of D-03 with the reasoning above, rather than block ship on adding a
diagnosability check for a shape not reachable from the query's own structure. Route to pm/eng-lead
to make the accept/backlog call formal; not mine to close.

## Q2 — two unfixtured envelope shapes, measured

- `{"data": None}` at exit 0 and at exit 1: `env.get("data") or {}` collapses to `{}`,
  `repositoryOwner` reads `None`, raises `GhError("project owner not found", "owner", ...)`. **Safe
  (no item-edit), but misdiagnosed** — the actual failure is a wholly null data envelope (a real
  transport/schema anomaly), not an unknown owner login. The message is actionable-shaped but
  factually wrong about the cause. Not a write risk; a diagnostic-accuracy risk only.
- field dict present but missing `"options"`: raises `GhError("project field option not found", ...)`
  safely — `resolved["options"]` is `[]` via `.get("options", [])`, so the loop over options simply
  finds no match. No write.
- field dict present but missing `"id"`: **raises bare `KeyError: 'id'`, not `GhError`**, inside
  `_project_field_resolve`'s return-dict construction (`field_obj["id"]`), before any item-edit
  call is reachable. No write is attempted.

**Revised finding, after checking reachability against the query document rather than asserting
it.** `id`, `name` and `options` are all selected *inside* the `... on ProjectV2SingleSelectField`
inline fragment (`factory_gh.py:209-212`). GraphQL resolves an inline fragment as a unit: if the
concrete type does not match `ProjectV2SingleSelectField`, none of the fragment's fields resolve
and `field` comes back `{}` — which is exactly the measured, fixtured, empty-dict shape this suite
already covers. If the type *does* match, the server must resolve everything the fragment
requests, and `id`/`name` are conventionally non-nullable GraphQL node fields. So a field dict that
is present, non-empty, and still missing `id` is not a shape this specific query document can
produce from a conformant server — only from a hand-built stub. Same argument covers the
missing-`options` case (also inside the fragment, also empty-list-safe via `.get("options", [])`
regardless). **Reclassifying: residual, not a routable defect.** No fixture owed. SC-10 holds for
every response this query document can actually produce; my earlier "genuine gap" framing
overstated it by not checking the fragment-boundary argument before writing it down. The
`{"data": null}` misdiagnosis point stands on its own — it does not depend on this argument and is
lower-confidence-reachable (a wholly null top-level `data` is a genuine, if unusual, transport
scenario), so it stays recorded as a residual worth the operator's attention, not a fixture-owed
gap either — it fails safely (no write) with an actionable-shaped, if not fully accurate, message.

## Coverage gaps

SC-01 is **not** listed here — it is correctly routed to `uat` per the BRIEF, and an operator-run
UAT is a satisfied verification path, not a gap.

- **Q1's partial-success envelope** (exit 1, `data` complete with no null, `errors` non-empty): no
  fixture reaches it, and per the fragment-boundary analysis I believe it is not reachable from a
  real `gh` response for this exact single-leaf query shape — recorded as a residual, not
  recommending a new fixture be forced in. Route the accept/backlog call to pm/eng-lead.
- **Q2's shapes, on reflection, are not a coverage gap** — see the revised finding above: both are
  unreachable from this query document against a conformant server. Not routing either as a
  fixture-owed gap.
- **The org exit-0 fixture (`GRAPHQL_ORG_OK_JSON`) remains derived, not measured** — unchanged from
  the BRIEF's own disclosed gap; still true, still honestly disclosed there.

## The eng digest's vacuity claim, verified rather than trusted

The eng digest reports the member added, then removed, two `except Exception` scaffolds — one of
which let `"a non-diagnosable transport failure raises GhError"` pass on an unrelated
`json.JSONDecodeError`. I did not take that as given; grepped the shipped file for any broad
handler: `grep -n "except Exception\|except:\|except BaseException"
test-factory-gh.py` returns exactly one hit, `silent_stdout`'s generic exception-capture helper
(`:74`), used only to record `(result_or_exc, stdout)` pairs for the stdout-emptiness checks —
unrelated to the transport-failure assertion. The transport-failure case itself
(`test-factory-gh.py:372-392`) catches narrowly: `except fgh.GhError as e:` at `:379`, then
`isinstance(exc, fgh.GhError)` at `:384`. No vacuous broad-catch scaffolding survives in the
shipped file.

## Test-first compliance audit

The work landed in a single commit (`5c433f2`), so git history shows no separate RED commit to
diff against — order cannot be verified from history. The only order evidence is the receipt's own
narrative (`notes/receipt-harness-backend-dev-T-01-c0.md:10-169`): a verbatim RED section (11 of
108 checks failing, run against the unchanged `factory_gh.py`), then a hardening section describing
the two `except Exception` scaffolds found and removed, then a GREEN section with the final
118/118. The RED-to-GREEN check count (108 → 118, +10 from the post-RED hardening's added
assertions) is internally consistent with the two removed scaffolds plus "two missing `api graphql`
assertions" the receipt separately claims to have added. I did not independently reproduce the RED
run (that would require reverting `factory_gh.py` to `8dedeae` and is out of scope for a gate over
the finished diff) — this is the receipt's self-report, corroborated by internal consistency and by
the independent vacuity check above, not independently re-executed.

## Open items from the plan-contract validator (Q1/Q2 there) — status

Both were correctly demoted to non-blocking residuals at plan time and remain so at gate time:
Q1 (matrix binding integration only via task verify) is now moot for this run — I ran the
integration KIND command directly and it is green (97/97), independent of the task verify. Q2
(unmeasured envelope shapes) is what this run's own Q1/Q2 measured; see above.

## What I did not do

Did not touch `run-unit-tests.sh`, any DEC-174 carve-out file, or anything under `bin/`. All
mutation and probe work ran in the scratchpad against copies, never in-place. No commit. Cleaned
scratch state is outside the repo and does not appear in `git status`.
