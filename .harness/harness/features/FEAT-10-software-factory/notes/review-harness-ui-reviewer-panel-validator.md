# UI review — FEAT-10, CLI output surface vs DESIGN.md C-3

## Verdict: FAIL — two `high` findings, both confirmed live (offline, no `gh`/network calls)

The surface is not GUI; it is C-3's contract: stdout/stderr split, the four-row exit table, and
the failure grammar (`factory_cli.message`/`body`). Reviewed by reading all 15 new files
(untracked — `git diff` shows nothing, per the dispatch) and running the tools directly against
synthetic bad inputs, offline. Bounds respected: nothing committed, no live `gh`, no real branch.

## MUST-FIX 1 — the exception-class-name leak (w2-eng Q1), confirmed live and systemic

**Not the carved-out exception.** C-3's carve-out for `unexpected failure: <type name>` applies
"where by definition there is no operator-actionable value to name." Every instance found below
has one, embedded in the exception's own `str()` — the carve-out's stated premise is false on its
face, and this is the same defect plan-phase MF-4 forbade.

**Strongest instance — `factory_decompose.py:279,433`.** `harness_yaml.load_plan()` raises
`PlanSchemaError` (a `harness_yaml.YamlParseError` subclass) with fully-formed operator
instructions — the offending field, the task id, the legal values. `expected=(FleetError,
GhError)` at line 433 does not include it. Confirmed live, offline, against a `plan.yaml` missing
`tasks:`:
```
factory: decompose: unexpected failure: PlanSchemaError: failed to parse YAML in
<path>/plan.yaml: `tasks:` is missing, empty, or not a list — re-run with FACTORY_DEBUG=1
for a traceback
```
The message that reaches the operator is a genuinely actionable one — `tasks:` is missing, here
is the file — wrapped in a class-name prefix that C-3 says never to print. An operator who reads
only the first clause after `unexpected failure:` sees a Python type, not an instruction.

**Second instance — `factory_config.py:70-75` (w2-eng Q1 as originally raised).** `load_fleet()`
calls `harness_yaml.load_file(path)` unguarded before its own validation begins; on an absent or
syntactically-invalid `fleet.yaml` it raises `YamlParseError`, not `FleetError`. Confirmed live,
offline, against a nonexistent fleet path:
```
factory: config: unexpected failure: YamlParseError: failed to parse YAML in
/tmp/does-not-exist.yaml: [Errno 2] No such file or directory: '...' — re-run with
FACTORY_DEBUG=1 for a traceback
```
`load_fleet()`'s own docstring promises `FleetError` "on every one of the nine listed shapes of
malformed fleet" — all nine are structural mutations of an otherwise-valid parsed dict
(`test-factory-config.py`'s own docstring confirms this: "the nine ways a fleet file can be
malformed"). "File absent" or "not YAML at all" is a tenth, untested shape, and it is the one a
fresh fleet setup — day one, per DESIGN.md's own stated pre-condition narrative — is most likely
to hit.

**Systemic, not local.** `load_fleet()` is called by all five command-line tools
(`factory_config`, `factory_decompose`, `factory_claim`, `factory_workspace`, `factory_land`),
and none of their `expected` tuples include `YamlParseError`/`MissingDependency`. `MissingDependency`
is also a `YamlParseError` subclass, so a machine without PyYAML — the single most-anticipated
environment failure the harness names — hits this same route, `unexpected failure:
MissingDependency: ...`, carrying `INSTALL_COMMAND` behind a class-name prefix.

**Discriminator, so the review is internally consistent:** `factory_workspace.py:38-61`'s
`run_git` also lets a non-`expected` exception (`RuntimeError`) reach the generic trap, but this
is *not* a finding — `run_git` already prints the actionable line (command, exit status, git's
own first stderr line) at `:56-59` before raising, so the operator has what they need before the
class-name line ever appears. In the `YamlParseError`/`PlanSchemaError` routes, no actionable line
is ever emitted separately — the class-name-prefixed line *is* the only signal.

- Severity: **high**. Root cause is one place (`load_fleet()`'s unguarded read, and each tool's
  `expected` tuple) with day-one blast radius across all five tools.
- Anchors: `factory_config.py:70-75`, `factory_config.py:184-185`; `factory_decompose.py:279`,
  `factory_decompose.py:433`; same pattern present (untested) at `factory_claim.py:337`,
  `factory_workspace.py:140`, `factory_land.py:106`.
- Coverage gap corroborating this: `test-factory-config.py` never constructs an absent or
  syntactically-broken fleet file; `test-factory-decompose.py` was not checked for an equivalent
  case but the code path is identical.

## MUST-FIX 2 — `factory_land.py:73-84,99` fail-open lies to the operator on two channels

Judged strictly on the output-contract lens (the correctness/predicate angle is the code
reviewer's): when `gh pr create` fails with a message containing "already exists" **anywhere** in
combined stdout+stderr, and a regex finds **any** `https?://\S+` substring anywhere in that same
text, the tool treats it as an adopted retry — no verification that the URL is actually a pull
request, or that "already exists" refers to a PR at all.

The mechanical JSON-parses-in-one-`json.loads` clause of C-3 is **not** what breaks — the payload
is syntactically valid either way. What breaks is the human-facing half of the contract:
`factory_land.py:81-84` prints, **unconditionally in that branch**,
`factory: land: pull request for {branch} already open — {url}` — an affirmative, unhedged
factual claim that is false whenever the matched URL is not a PR. Paired with `:99`'s
`project_field_set(..., "review")` — C-1's own definition of `review` is "an open pull request
carries the work" — the operator gets **two independent signals**, one on stderr and one on the
board, both asserting a PR that does not exist. Exit 0 completes the lie: the operator has no
reason to distrust either signal.

**Compare to the codebase's own established pattern for exactly this ambiguity.**
`factory_gh.py:217-231` (`create_ref`) and `factory_decompose.py:403-414` (the `blocked_by`
handler) both require the specific HTTP status **and** a specific phrase (`"422"` and `"already
exists"`/`"already been taken"`) before treating a `GhError` as non-fatal. `factory_land.py:77`'s
predicate is strictly weaker than its own siblings — no status check, and the URL match is
unconstrained. This is a regression from the pattern already proven safe elsewhere in this same
diff, which is why it reads as an implementation slip rather than a deliberate design choice.

**Untested.** `test-factory-land.py`'s only case for this branch (`M2`) uses a realistic gh
message where the URL immediately follows "already exists:" in the same sentence — a true
positive. No case exercises an unrelated "already exists" phrase paired with an unrelated URL —
the exact shape of the false positive.

- Severity: **high**. Silent, exit-0, board-mutating misinformation on the one channel (`review`
  station + PR link) an operator uses to decide the item is done.
- Anchors: `factory_land.py:73-84` (predicate + stderr claim), `:99` (station write consuming the
  bad payload), `:102` (stdout payload carries the wrong `url`).

## FIX ORDER — concurred, with the evidence that supports it

1. `.harness/harness.json`'s `functional.cmd` gates qa's BLOCKED verdict — unrelated to either
   finding above; fixing it clears qa's gate and changes nothing about mine. Both findings above
   **survive** that fix.
2. `factory_land.py:77` via a `create_pull_request` helper behind `factory_gh` — agreed, and the
   evidence above makes the reason concrete: `create_ref` and the `blocked_by` handler already
   carry the strict `"422" AND <phrase>` predicate and both live behind `factory_gh`; a
   `create_pull_request` helper there inherits that sibling pattern for free. Patching `:77`'s
   predicate in place would be the third copy of this logic with no shared enforcement — exactly
   what `factory_cli` exists to prevent for the failure grammar generally.
3. No disagreement with the ordering.

## Confirmed compliant (checked, not assumed)

- **Stream split.** Every `print()` across all 7 modules goes to `sys.stderr` except
  `factory_cli.payload()`'s single `print(json.dumps(obj))` (stdout). Grepped exhaustively.
- **Import-time output.** Measured: `import <module>` for all 7 modules produces 0 stdout bytes
  and 0 stderr bytes. (`factory_config.harness_root()`'s stderr line on a bad
  `CLAUDE_PROJECT_DIR` exists but is stderr, and did not fire in this environment.)
- **Exit vocabulary scoping.** Grepped: only `factory_claim.py` calls `nothing_to_do`/`lost_race`
  (exits 1/3); the other four tools never do. Exit 3 only fires under `--issue`
  (`factory_claim.py:311-314`).
- **`factory_claim`'s two `nothing_to_do` causes** — `"no work available"` (`:256`) vs `"no
  claimable work"` (`:323`) — two distinct stderr lines, confirmed by reading, matching C-3.
- **Skip-reason distinctness (C-2/C-2-amendment).** Seven textually distinct reasons in the
  candidate loop: not-open, already-claimed, already-assigned, three blocker-gate reasons
  (`edge_i`/`unresolvable`/`open`, `factory_claim.py:162-176`), and ref-already-exists. Matches
  w2-eng's count; verified by reading, not accepted on faith.
- **Q9 (exit code for a fresh `--issue` claim on a blocked candidate).** `plan.yaml` resolves it
  explicitly: exit 2 via `factory_cli.refuse`, reasoned as distinguishable from exit 3. Code
  (`factory_claim.py:298-301`) matches exactly. No finding.
- **C-4 colour-as-information.** `factory_gh.py:23` — one `_LABEL_COLOR` constant used for every
  `ensure_labels` call; grepped for any other colour constant or ANSI escape sequence
  (`\033`/`\x1b`/colorama/termcolor) across all 7 modules — none found. Colour was not
  "improved" into coding; text is the only channel, as C-4 requires.
- **Point-of-no-return table (C-3).** Read against code for all five tools; each tool's mutating
  calls begin exactly where the table says (`factory_decompose`'s `ensure_labels` at step 5;
  `factory_claim`'s `create_ref`; `factory_workspace`'s clone/fetch+reset; `factory_land`'s push)
  — no tool mutates earlier than its stated point.

## Lower-severity / advisory

- **`factory_config.py` invoked with no `--show` prints nothing and exits 0.** Measured:
  `json.loads("")` raises. C-3 says "the whole of stdout on a successful run must parse in one
  `json.loads`" — a literal, if narrow, divergence on a tool C-3 explicitly binds. No operator is
  misled and nothing mutates; `low`. Whether a validate-only invocation counts as "a successful
  run" under C-3 is a plan-level clarification worth having, not a blocking defect.

## Explicitly out of scope, per settled rulings

Palette/type/spacing/dark-light: `n/a` (DESIGN.md's own ruling, not re-litigated). Station words
`Ready`/`Building`/`Review`, including the accepted `Review`-as-imperative residual: not reopened.
T-08/`check-state.sh`: withheld under DEC-174, not touched or cited beyond noting qa's BLOCKED
verdict traces to it, which is qa's finding, not restated as mine.

## Dimension this role cannot verify from source

**Rendered stderr line-width/wrapping legibility.** The confirmed `unexpected failure:` line runs
well past 80 columns and interpolates a full filesystem path plus a nested exception message; several
other stderr lines interpolate a repo name, an issue number, and gh's own error text into one line.
Whether an operator reading only stderr in a real terminal can parse these once they wrap is not
checkable from source — human or UAT check required.

## DIGEST fields

Both `high` findings are independent of qa's `functional.cmd` blocker and of each other; fixing
one does not fix the other. `factory_land.py:77` should be fixed via a `factory_gh` helper per FIX
ORDER, not patched in place. The exception-leak finding's root cause is `factory_config.load_fleet()`'s
unguarded read plus every tool's `expected` tuple — one fix point, five-tool blast radius.
