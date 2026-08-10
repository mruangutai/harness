# Code review — FEAT-10 software factory, working tree vs f9488a2

BLUF: **FAIL**, `severity_max: high`. Not gated by opinion — one concrete fail-open
(`factory_land.py:77`) and one confirmed BLOCKED-gate issue (`functional` kind still
misconfigured) both clear the `must_fix`/`high` bar. Everything else below is ranked but
non-blocking.

Scope actually reviewed: `git status --porcelain` confirms the 15 new `.py` files under
`.claude/skills/harness/bin/` are `??` (untracked, no diff exists) and were read as whole files;
`git diff HEAD` was used for the four modified in-scope files. Ran `run-unit-tests.sh --kind unit`
and `--kind integration` read-only: **all green**, 7/7 new unit files PASS, `test-factory-integration.py`
93/93 checks PASS, `test-check-state.py` (T-08, withheld) still PASS. No live `gh`/`git`, no writes,
no commits made.

## FIX ORDER — carried verbatim from qa's dispatch, with my agreement stated

1. `.harness/harness.json` decision first. **Confirmed and I agree with the ordering.**
   `test_kinds.functional.cmd` is still `null` with `_reason: "unset — dev-ops has not run detection
   yet"` (`.harness/harness.json`, `git diff HEAD` shows only the `integration` block touched).
   `factory_gh.py` (`subprocess.run([gh]+args)`) and three cross-module orchestrators are
   `api`/`cross_module` by qa's own diff-read classification, both of which put `functional` in
   `always`. That resolves to qa's own gate rule — misconfigured → `BLOCKED`, not a soft skip — and
   it is a decision about the gate's own config surface, not something a code-quality pass can
   discharge. Fixing it is not a source-code change, so it does not conflict with anything below.
2. `factory_land.py:77` via a `create_pull_request` helper behind `factory_gh`, not a patch in
   place. Agreed — see finding 1 below, and see why patching in place throws away nothing useful:
   there is no test currently anchored to the in-place predicate's exact regex.
3. Do NOT patch `factory_land.py:77`'s predicate directly. Agreed, for the reason qa gave: item 2
   replaces the whole mechanism.

I have no disagreement with this ordering.

## Stage 1 — spec compliance

Traced every in-scope module against its `plan.yaml` task and cross-checked the two
`verify: inspection` criteria directly (not by trusting qa's table):

- **SC-03** (inspection) — confirmed. `grep -n "open(\|\.write(\|dump("` across `factory_claim.py`,
  `factory_workspace.py`, `factory_land.py`, `factory_gh.py`, `factory_config.py` returns **zero**
  matches — none of those five modules opens any file at all. The only write surface in the feature
  is `factory_decompose.py:177-209` (`write_factory`), which targets only
  `<feature-dir>/feature.yaml` via tempfile + `os.replace`. `extract_brief`
  (`factory_decompose.py:57-72`) opens `BRIEF.md` with the default read mode only. Holds as
  claimed.
- **SC-09** (inspection) — confirmed against `docs/harness/DECISIONS.md:5421-5464` (DEC-186, `git
  diff HEAD` shows it as pure addition). Every clause the criterion names is present with a
  citable line: three purposes closed-set (`:5430-5435`), DEC-138 named as the amended baseline
  (`:5424-5428`), the rendered `blocked_by` edge "NEVER read" (`:5449-5451`), the per-blocker cost
  (`:5453-5455`). `docs/harness/DECISIONS-INDEX.md`'s new DEC-186 row (`@5421`) matches a fresh
  `gen-decisions-index.py --stdout` run byte for byte (`diff` returned nothing). `check-docs.sh`
  ran clean (62 patterns, 296 files, no stale statements). T-09 holds.
- Spot-verified T-10's `harness.json` change directly (not from qa's table): the `integration`
  detect glob change and the `_reason` deletion both match the task's exact instruction, and the
  verify script in `plan.yaml` passes when re-run (`integration detects 2 file(s)`).
- No scope creep found: every changed file traces to a task in `plan.yaml`, and the two files
  outside my 15-file scope (`gen-omp-agents.py`, `omp-reviewer-guard.check.ts` and their tests) are
  correctly excluded as held dirt — I did not open them.
- No omission found against REQ-01..08 at the module level: all five command-line tools, the
  shared `factory_cli` contract, and the DAG edge functions exist and match their task's `intent`
  on every point I sampled (see Stage 2 for the places the *details* diverge).

## Stage 2 — code quality, ranked

### 1. `factory_land.py:77` — the loosest of three gh-error predicates in this codebase, unmeasured, exit-0 on miss. **HIGH.**

```python
m = re.search(r"https?://\S+", combined) if "already exists" in combined.lower() else None
if m is None:
    raise
url = m.group(0)
```

Compare the same shape's other two implementations in this same diff: `factory_gh.py:229`
(`create_ref`) requires **both** `"422"` and `"already exists"` in the combined output, matching a
live-measured HTTP status; `factory_decompose.py:407` (`blocked_by`) requires **both** `"422"` and
`"already been taken"`, also live-measured (D-14). `factory_land.py:77` requires **neither a status
code nor a measured phrase** — just the bare substring `"already exists"`, and then greedily takes
the *first* URL-shaped token anywhere in the combined stdout+stderr, with no check that it is a
`github.com/<repo>/pull/\d+` URL.

Two independent ways this fails open, both landing past the point of no return (the push already
happened in step 3):
- **Predicate too loose.** Any `GhError` from `gh pr create` whose combined output happens to
  contain `"already exists"` (case-insensitive, no status check) plus any URL is silently treated
  as "PR already open." `land` then reports `exit 0`, sets the board station to `Review`, and
  prints the extracted URL as the PR link — even if no pull request exists at all.
- **First-URL-wins, unvalidated.** Even on the *genuine* conflict path, `re.search` takes whatever
  URL-shaped token appears first in `stdout+"\n"+stderr`, never confirming it is the PR link. I
  could not verify live (out of scope, no live `gh`) whether `gh pr create`'s non-TTY captured
  output ever carries a second URL ahead of the PR link — flagging this half as an aggravating but
  **unverified** hypothesis, not a confirmed mechanism. The predicate-looseness half above is
  confirmed by direct reading and needs no live check.

I checked whether the test suite exercises the actual gap and it does not:
`test-factory-land.py`'s case `(M2)` (line 218-232) uses the real gh wording verbatim and is
correctly handled; case `(M2b)` (line 234-247) uses a message with **neither** token
(`"authentication failed, run gh auth login"`) and correctly stays fatal. There is no case with a
message that contains `"already exists"` as an incidental substring while being a genuinely
different failure — the exact shape the two sibling predicates were built to exclude by requiring a
status code. `(M2c)` (line 249-262) is a good, separate fail-closed case (missing board item exits
2) and does not touch this gap.

**Failure scenario:** `gh pr create` fails for a reason unrelated to a duplicate PR, but the
combined captured text contains both the words "already exists" (in any context — a repo setting,
a branch-protection rule, boilerplate) and a URL (a docs link, an org page). `factory_land` reports
success, moves the board card to `Review`, and the operator sees a "done" journey with nothing to
merge — the control plane's chief signal (exit code + payload) becomes indistinguishable from a
correct landing, which is exactly the class of confusion REQ-08 exists to prevent, just at exit 0
instead of exit 1.

**Note on qa's stated detectability chain:** I independently verified the part of qa's reasoning
this dispatch flagged as broken, and it is broken as written — `factory_claim.py:330` moves the
item's station to `Building` in step 6 on the winner, so by the time `factory_land` runs, the item
is already out of the `Ready` column regardless of what `land` does; nothing about this defect lets
the item get re-claimed. That does not change my severity: the real cost is a silently false board
state and a possibly-bogus URL reported as fact, not a double-claim.

### 2. `factory_gh.load_fleet`'s absent/unparseable-file path exits through the generic "unexpected failure" trap, leaking `type(exc).__name__` into what MF-4 ruled against — but stays fail-closed. **MED.**

Verified live (in-process, no fixture needed):

```
$ factory_config.load_fleet('/nonexistent/fleet.yaml') under factory_cli.run
exit code: 2
stdout: ''
stderr: "factory: config: unexpected failure: YamlParseError: failed to parse YAML in
        /nonexistent/fleet.yaml: [Errno 2] No such file or directory:
        '/nonexistent/fleet.yaml' — re-run with FACTORY_DEBUG=1 for a traceback"
```

`factory_config.load_fleet` (`factory_config.py:70-139`) validates only the **shape of an already-
parsed dict** (the nine cases T-02's intent lists) and never catches
`harness_yaml.YamlParseError`, which `harness_yaml.load_file` raises for a missing file, an
unreadable file or invalid YAML syntax (`harness_yaml.py:237-255`). None of the five tools' `expected=`
tuples include `YamlParseError` (`grep -n "expected=" factory_*.py` — all five list only
`FleetError`/`GhError`), so this class of failure — a common, entirely foreseeable operator error
(fleet.yaml not yet created, a typo in `--fleet`, a garbled edit) — falls through to
`factory_cli.run`'s generic trap and prints the exception's class name in the value slot, which is
the exact resurfacing the dispatch names (plan-phase MF-4, `STATE.md:35`). `test-factory-config.py`
has no case for a missing or unparseable fleet file at all (`grep -n "YamlParseError\|nonexistent\|
does not exist\|corrupt"` returns nothing) — the gap is untested as well as unhandled.

Ranked **med, not high**, because D-08's own carve-out text (`plan.yaml:247-254`) explicitly
permits the class name in this exact slot for "by definition no operator-actionable value" cases,
and here there *is* still an actionable value in the message — the file path appears twice in the
actual output above. The exit code is correct (2, not 1), stdout stays empty, and T-12's own case
(B) ("a `--fleet` path that does not exist exits 2 with a stderr line naming that path") passes
against this exact behaviour. The defect is inconsistency with the codebase's own established
pattern (every other fleet problem gets a polished `FleetError` message; this one class gets an
ugly generic one) and a real, if softened, echo of a pattern this project has already ruled against
once — not a fail-open.

### 3. `factory_gh.py:229` vs `factory_decompose.py:407` vs `factory_land.py:77` — three predicates for the same class of GitHub conflict, only two of them measured. **Restated as the general shape of finding 1**, not a separate item — see finding 1 for the concrete instance that matters. Worth naming here only because it is the seam the FIX ORDER's `create_pull_request` helper (item 2) should close: putting the predicate behind `factory_gh` alongside its two siblings is what makes it inherit their discipline (status code + measured phrase) rather than staying a third, looser one-off.

### 4. `factory_decompose.py:292` — a repeat publish under a different `--repo` silently mixes issue numbers across repositories. Nobody guards it. **MED.**

```python
factory = load_factory(feat_dir)      # loads the RECORDED factory.repo, if any
factory["repo"] = args.repo           # unconditionally overwritten, no comparison
```

**Failure scenario:** publish once against `--repo ownerA/repoA`, interrupted after `create_issue`
for some task but before its board add (the documented "partial" disposition,
`factory_decompose.py:236-237`). Re-run the same feature directory against `--repo ownerB/repoB`
(a plausible operator slip — wrong terminal history, a copy-paste error, or a genuine change of
target mid-increment). `sort_dispositions` (`:227-240`) keys only on task id inside `factory["issues"]`/
`factory["items"]`, with no repo comparison, so the task is still read as "partial" and step 7
(`:349-363`) builds `url = f"https://github.com/{args.repo}/issues/{num}"` — **repoB's owner/name
with repoA's issue number.** Two outcomes, neither guarded: the number doesn't exist in repoB and
`project_item_add` raises `GhError` (safe, exit 2, but a confusing message that never names the
actual mismatch); or the number *does* exist in repoB as an unrelated issue, and that issue is
silently boarded, labelled and gated as if it were this feature's task. Nothing in `plan.yaml`
requires this guard explicitly, so I am reporting it as a guard omission rather than a spec
violation — the fix is a one-line refusal at step 1 (`factory["repo"]` recorded and non-null and
`!= args.repo` → `factory_cli.refuse` before any call), matching the tool's own established style
for every other unlisted/mismatched-repository case.

### 5. `_strip_factory_block`'s round-trip test proves less than it appears to. **LOW.**

`factory_decompose.py:137-154`'s skip loop treats *any* line starting with `""`, `" "`, `"\t"` or
`"#"` as a continuation of the just-stripped `factory:` block — including a stand-alone, column-0
comment that happens to sit immediately after it. `write_factory` always appends the `factory:`
block last (`factory_decompose.py:191-194`), so on a *fresh* file this never bites; it only matters
on a second publish where something (an operator hand-edit, or another tool) has appended content
after an existing `factory:` block. `test-factory-decompose.py` case 9 (`:419-444`) asserts "a
trailing comment survives," but its fixture places that comment in text with **no pre-existing
`factory:` block at all** (`extra` never contains a `factory:` key), so `_strip_factory_block`
never enters `skipping` mode during that test — the assertion passes without exercising the risky
code path. No test publishes twice against a fixture where a comment trails an already-recorded
`factory:` block. Consistent with the presence-check-needs-an-absence-check-beside-it discipline —
here it's a presence check that happens to sit outside the risk it was meant to cover.

### 6. `factory_land._find_item_id` / `factory_claim`'s `--issue` path query `is:open` (unbounded by station), not the ready-column-scoped query D-10 describes elsewhere. **INFO, not a defect.**

Both read the whole open-issue set (measured 70 of 150 on board 3) rather than the ready-only
query poll mode uses. This is not fail-open: `project_items` still raises `GhError` when
`totalCount` exceeds the returned items (`factory_gh.py:187-192`), so a growing board fails
*closed* at exit 2 rather than silently truncating, and the default `limit=500` leaves real
headroom over the measured 70. I looked for an alternative (a project-item query filterable by
issue number) and found none documented anywhere in D-14/T-03 — these two code paths need the item
regardless of its current station (self-ownership re-entry; moving an item that's already past
`Ready`), so `is:open` is close to the narrowest available bound given the API, not an oversight.
Naming it only so a reader doesn't rediscover it as a surprise later.

## `expected=` / import-side-effect items raised by w2-eng, assessed and downgraded

- **`FEATURES_ROOT` computed at module import in `factory_claim.py:43`.** Confirmed it happens.
  Not escalating: T-05's own plan section (`plan.yaml:962-1273`) carries no "importing must have no
  side effects" sentence (unlike T-02, T-03, T-06, T-11, which explicitly state it), and the
  identical pattern already exists, accepted, in `factory_config.py:50` (`FLEET_PATH` computed at
  import via the same `harness_root()`), which *does* carry that requirement in its own docstring
  and states the side effect is intentional and read-only. The module's own comment
  (`factory_claim.py:41-43`) documents this is deliberate for monkeypatchability, and `_main`
  reads `FEATURES_ROOT` as a live module global rather than a captured default, so a test
  reassigning `factory_claim.FEATURES_ROOT` after import is honoured — verified by reading the call
  site (`factory_claim.py:259`). **LOW/informational** — a style inconsistency worth a line, not a
  functional defect.
- **qa's Q3/Q4 (informational, as labelled in the dispatch).** Confirmed both are real but
  non-blocking: `factory_config.py` has no required argv, so its `(A) config: no arguments exits 2`
  case (`test-factory-integration.py:333`) passes because the synthetic root carries no
  `fleet.yaml` (a `FleetError`), not because of any argument-parsing trap — the intended
  "unwrapped entry point" catch still would have worked here via a different route (an unhandled
  `FleetError` would have printed a Python traceback and exited 1, which the assertion `!= 1` would
  have caught), so the test's *purpose* still holds even though its *mechanism* differs from the
  other four tools. SC-10's gh-auth case is correctly asserted as structurally unreachable for
  `config`/`workspace` (`test-factory-integration.py:353-356`, comment says so and the code doesn't
  assert it for those two). Neither changes a verdict.

## Findings NOT escalated after checking

- Requested check on whether `gh pr create`'s captured (non-TTY) output could carry an unrelated
  URL ahead of the real PR link: **could not verify live** (constraint: no real `gh`). Recorded as
  an unverified aggravating hypothesis inside finding 1, not as its own item.
- `factory_gh.py:229`'s and `factory_decompose.py:407`'s own predicates: both matched their
  documented, live-measured shapes exactly (D-05, D-14) and are correctly narrow. No finding.
- Re-checked qa's own blocking `functional` finding against the diff directly rather than trusting
  qa's table: confirmed via `python3 -c "json.load(...)['test_kinds']['functional']"` — `cmd` is
  still `None`, `_reason` still present, untouched by `git diff HEAD -- .harness/harness.json`.
  Folded into FIX ORDER item 1 rather than reported as a separate finding, since it is qa's gate to
  own.

## DIGEST fields

```yaml
VERDICT: FAIL
DIGEST:
  headline: "factory_land.py:77's unmeasured gh-error predicate fails open past the point of no return, and functional's cmd:null still blocks qa independently of any code fix — both clear must_fix/high"
  severity_max: high
  findings: 6
  must_fix:
    - "factory_land.py:77 — build create_pull_request behind factory_gh with a measured status-code + phrase predicate (matching factory_gh.py:229 / factory_decompose.py:407's discipline), never patch the regex in place (fix order item 2/3)"
    - ".harness/harness.json test_kinds.functional.cmd is still null/misconfigured for a diff qa classifies as api/cross_module — resolve before re-gating (fix order item 1)"
  spec_violations: []
  reviewed: "f9488a2..working-tree (15 untracked .py files read whole; git diff HEAD for run-unit-tests.sh, .harness/harness.json, docs/harness/DECISIONS.md, docs/harness/DECISIONS-INDEX.md)"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Does gh pr create's captured (non-TTY) stdout/stderr ever carry a second URL ahead of the PR link on the genuine already-exists path? Unverifiable without live gh; if yes it strengthens finding 1's first-URL-wins half.", blocking: false }
    - { id: Q2, question: "Should load_fleet wrap harness_yaml.YamlParseError into FleetError so a missing/garbled fleet.yaml gets the polished message shape instead of falling into factory_cli.run's generic unexpected-failure trap?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-10-software-factory/notes/review-harness-code-reviewer-panel-validator.md
```
