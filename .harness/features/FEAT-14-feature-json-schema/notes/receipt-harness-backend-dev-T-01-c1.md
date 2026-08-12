# Receipt — harness-backend-dev — T-01 — c1

## Verify clause, as run verbatim

```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```

Cross-checked against `plan.yaml` T-01's `verify:` — identical string. Matches, not `BLOCKED`.

**Before** (measured before any edit): exit **0**, all scripts PASS (`UNIT_SCRIPTS` held **11**
entries at that point, verified via `git show HEAD:...` — not the "10 scripts" BRIEF.md's
2026-08-10 measurement names; that figure is stale by one and is not repeated here —
`test-validate-feature-json.py` did not exist yet).

**After** (with `feature-schema.json`, `feature_schema.py`, `validate-feature-json.py`,
`test-validate-feature-json.py` in place and registered in `UNIT_SCRIPTS`): exit **0**, 12/12
unit scripts PASS, **41/41** checks inside `test-validate-feature-json.py` PASS (counted via
`grep -c "^PASS "` on a direct stand-alone run, not recalled). Full output captured this run;
final lines:

```
...
PASS forced_unavailable_names_install_command

ALL PASS
PASS test-validate-feature-json.py
```

`python3 -c "import jsonschema; print(jsonschema.__version__)"` → `4.26.0`, re-confirmed on this
machine (not trusted from BRIEF.md's line).

## Files touched

- `.claude/skills/harness/bin/feature-schema.json` (new)
- `.claude/skills/harness/bin/feature_schema.py` (new)
- `.claude/skills/harness/bin/validate-feature-json.py` (new)
- `.claude/skills/harness/bin/test-validate-feature-json.py` (new)
- `.claude/skills/harness/bin/run-unit-tests.sh` (one-line edit: `test-validate-feature-json.py`
  added to `UNIT_SCRIPTS`, not `INTEGRATION_SCRIPTS`)

Nothing else. `.harness/features/FEAT-14-feature-json-schema/feature.yaml` and `STATE.md` show
as modified in `git status` but that predates this run (the orchestrator's own dispatch
bookkeeping — `status: in_progress`, `branch:` set) and I made no edit to either.

## TDD

`test-validate-feature-json.py` written first; run stand-alone, watched RED
(`ModuleNotFoundError: No module named 'feature_schema'`, exit 1) before `feature_schema.py` or
`validate-feature-json.py` existed. Then implementation written, test re-run stand-alone → GREEN,
then registered in the runner and the full `--kind unit` run confirmed GREEN.

**CLI exit-code coverage, added after a first review pass caught a gap:** the first draft only
subprocess-tested the exit-3 (jsonschema-unavailable) path — exit 0 and exit 1 (the codes T-04's,
T-07's and T-08's verify clauses actually branch on: `if r.returncode != 0`) had no subprocess
coverage at all, so an inverted `sys.exit(1 if any_problem else 0)` would have passed every
existing check. Added `case_cli_clean_file_exit_0` and `case_cli_invalid_file_exit_1`, the latter
asserting `== 1` (not merely non-zero) so 1 and 3 are proven distinguishable in the shipped
binary. **Proved with a mutant, not merely added:** replaced `sys.exit(1 if any_problem else 0)`
with `sys.exit(0)`, predicted `cli_invalid_file_exit_exactly_1` alone would redden, ran the
suite, confirmed exactly that one FAIL and nothing else, then restored the file and confirmed its
sha256 matched the pre-mutation hash (`9ee110f9...121deb8`) — the file is untracked so `git
status` shows no diff either way, so the hash is what makes "restored cleanly" checkable.
`case_cli_clean_file_exit_0` also exercises the shebang/exec bit directly (`[VALIDATE_CLI, path]`,
no `sys.executable`) — every other CLI case in this file spawns via `sys.executable`, and CI/T-04
invoke the file by its exec bit, so at least one case now matches that invocation shape.

Also tightened three classes of assertion a first pass left weak: the eight required-key
rejections and the three undeclared-key-name rejections now match the quoted form
(`f"'{key}'" in p`) rather than a bare substring, and the three redirect-sentence assertions
compare against a `REDIRECT_SENTENCE` literal spelled out independently in the test file
(deliberately not imported from `feature_schema`, which would make the assertion tautological)
rather than checking three arbitrary substrings of it. Final count: **41/41** checks in
`test-validate-feature-json.py`, **72/72** across the full `--kind unit` run.

## Schema shape (D-01/D-02)

Eleven top-level keys, `additionalProperties: false` at the top level, inside `runs` items,
inside `github`, inside `factory`, and inside `factory.edges` (the last per the intent's own
explicit spelling of that sub-object, not an extrapolation of D-01). Eight required
(`feature_id, branch, pr, status, review_sha, cycles_used, max_total_cycles, runs`), three
optional (`max_total_runs, github, factory`). No `phase` property anywhere. `status` enum is
exactly `Backlog, Plan, Ready, Building, Review, Done`, compared case-sensitively by
`jsonschema`'s own `enum` keyword (no custom casing logic exists to get wrong). `pr` is
`["integer","null"]`; `branch`/`review_sha` stay plain strings with `none` legal (no `nullable`
added). Verified this is a well-formed draft 2020-12 schema via
`jsonschema.Draft202012Validator.check_schema(...)`.

Every property carries a `description`. Object-valued and reader-censused properties cite the
reader BY NAME (`gh-sync.py's load_recorded`, `check-state.sh INV-21`, `factory_decompose.py's
load_factory`, `factory_claim.py's issue_number`, `check-state.sh INV-24`, `check-plan-routes.py's
finished-feature skip`, `check-state.sh INV-17's seam table`), never by line number, per the
intent's explicit instruction that T-11/T-12 move those lines inside this same build.
`feature_id`, `branch`, `pr`, `max_total_cycles` — the four keys the BRIEF records as having no
demonstrated reader — carry a description saying so, rather than inventing a reader for them.

## Enforcement point (D-03) — where the extension dispatch and the `harness_yaml` import live

**My call, as invited by the intent:** both live inside `feature_schema.py`, not the CLI.

- `problems_for_text(text, display)` is JSON-only — it always parses `text` with `json.loads`.
  This is the function `check-domain.sh` imports at T-06 (per the intent, its entry point), and
  its `display` argument is a label for the message only, never a hint for how to parse.
- `problems_for_file(path)` does the extension dispatch: `path.endswith(".json")` reads the file
  as text and calls `problems_for_text` (stdlib `json` + `jsonschema` only); any other extension
  imports `harness_yaml` **lazily, inside that one branch** and calls `harness_yaml.load_file`.

This keeps D-03's "the CLI is argument parsing, printing and exit codes only, no schema logic"
literally true: `validate-feature-json.py` calls `feature_schema.problems_for_file(path)` per
path and never itself decides how to read a file.

**The empirical check the dispatch asked for, actually run** (not reasoned about): with a
shadow `yaml.py` on `PYTHONPATH` that raises `ImportError`, `import feature_schema` still
succeeds, `feature_schema.JSONSCHEMA_AVAILABLE` is `True`, and
`feature_schema.problems_for_text(json.dumps(<valid required-only doc>), "sample.json")` returns
`[]` — proving the `.json` path never touches `harness_yaml`/PyYAML. Separately confirmed that
`import harness_yaml` itself DOES succeed under that same shadow (its own `try/except` sets
`yaml = None`), which is the DEC-171-am.1 "loud only when actually needed" shape — but
`feature_schema`'s JSON path never reaches that import at all. Command run and full output are
in this session's transcript (not reproduced here per the "claims plus pointers" rule); the
assertion is `problems == []`, verified truthy this run.

## The two jsonschema-unavailable proofs — mechanism for each

1. **CLI case** (`case_cli_jsonschema_unavailable_exit_3`): spawns `sys.executable
   validate-feature-json.py <path>` as a real subprocess with `PYTHONPATH` prepended to a
   temp directory containing a `jsonschema.py` whose entire body is `raise ImportError(...)`.
   Because `sys.path` puts the invoked script's own directory first and the `PYTHONPATH` entry
   next (ahead of site-packages), `feature_schema.py`'s module-level `import jsonschema` binds to
   the shadow module and raises, setting `JSONSCHEMA_AVAILABLE = False` in that fresh
   interpreter. Asserts `returncode == 3`, `returncode not in (0, 1)`, and `"REQUIRED" in stderr`.
2. **In-process case** (`case_problems_for_text_jsonschema_forced_unavailable`): calls
   `feature_schema.problems_for_text(...)` in the SAME interpreter after directly setting
   `feature_schema.JSONSCHEMA_AVAILABLE = False` (module-attribute assignment, restored in a
   `finally`). Both `problems_for_text` and `problems_for_file` read the module-global
   `JSONSCHEMA_AVAILABLE` by name and return `[UNAVAILABLE_MESSAGE]` **before touching
   `jsonschema` at all** — the check is the first statement in each function — so this is not
   vacuous: flipping the flag alone is sufficient to force the branch, because no code path
   between the flag check and the return references the real `jsonschema` module.

## Loading by extension — the `.json`-invalid-YAML-valid case

`case_json_extension_rejects_yaml_content_yaml_extension_accepts_it` writes the SAME text (a
complete, valid, block-style YAML document — unquoted keys, no braces, therefore not valid JSON)
to both `sample.json` and `sample.yaml` in one tempdir. `problems_for_file` on the `.json` path
returns one problem naming a JSON decode error; on the `.yaml` path it returns `[]` (the document
is not just parseable, it fully validates) — proving dispatch is by extension, not a blanket
tightening, and that the `.yaml` sibling is genuinely ACCEPTED rather than merely not rejected
for the wrong reason.

## Fixture naming

`sample.json`, `sample.yaml` — no fixture is named `feature.yaml` or any variant. The CLI's
no-argument sweep globs `.harness/features/*/feature.*` and filters by suffix; no filename is
hardcoded. No test reads or writes any real path under `.harness/features/*/`.

## Redirection message

Chosen as ONE fixed sentence, printed verbatim for every undeclared-key rejection regardless of
nesting level. The intent's phrase "a destination line chosen by nesting level" only ever gives
one block of text to print, and the redirect table itself does not vary by nesting depth — so I
read "chosen by nesting level" as a trivial selector that always returns the same sentence, not
as an instruction to write per-level variants. This is a cheap, reversible wording call; noted
here rather than escalated because SC-02's own bar is "each fixture's rejection message names
the offending key" — no per-level differentiation is asserted anywhere in the BRIEF or the SCs.

## The no-argument sweep's silent-empty-glob case (not enumerated by T-01's test list, fixed anyway)

`discover_paths()` in `validate-feature-json.py` (the no-argument branch) now prints
`scanning <root>/.harness/features/*/feature.{json,yaml,yml} — <n> file(s)` to stderr before
returning, the same reasoning `check-plan-routes.py:607-609` already states for its own
discovery: a legitimate zero-feature checkout and a wrong-`CLAUDE_PROJECT_DIR` defect must not
print the same (nothing) and exit 0 identically. This does not add a fourth exit code — exit
stays 0 when the glob is empty, matching the three-code contract T-01 pins — it only makes the
zero-file case loud instead of silent. Not exercised by a test (T-01's intent lists no case for
the no-argument sweep, and this module's own tests are scoped to tempfile fixtures only, never
the real corpus), so this is a code-review-shaped fix without a red-then-green cycle behind it;
flagging that explicitly rather than letting it read as tested.

## Open questions

- `{ id: Q1, question: "The redirection message is implemented as ONE fixed sentence printed for
  every undeclared-key rejection regardless of nesting level, because T-01's intent gives only
  one block of text under the phrase 'a destination line chosen by nesting level' and the
  destination table itself does not vary by depth. Confirm this reading — a single uniform
  sentence, not per-level variants — is what was intended.", blocking: false }`
- `{ id: Q2, question: "feature_schema/validate-feature-json.py print problems to STDERR (matching
  T-01's own 'stderr LINES' wording), but T-04's plan.yaml verify block reads r.stdout on a
  non-zero exit ('validator exited %d: %s' % (r.returncode, r.stdout[-800:])). The exit code will
  still redden T-04's gate correctly, but the diagnostic text captured in that failure message
  will be empty. Worth fixing at T-04 or by having the CLI mirror problems to stdout too.",
  blocking: false }`
