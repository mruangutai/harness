# Review — PR #1247 (BUG-720-plan-merge-yaml)

Diff reviewed: `b2e36bf3..50da6493` (single commit, `main` tip == merge-base — clean rebase).
Files: `plan-merge.py` (11 read sites), `harness_yaml.py` (docstring only), `test-plan-merge.py`
(2 new cases + 1 split into 2).

## Verdict: PASS

Mechanical read-side migration, exactly matching issue #720's ask (mechanical half-1 move plus a
half-2 decision gated on counting on-disk `plan.yaml` files first — the count was done and is
correct). No scope creep: 3 files, nothing outside the stated diff. No spec (BRIEF/plan.yaml)
exists for this direct-flow bug PR per the assignment; issue #720 is the applicable spec and is
satisfied.

## The five requested checks — all verified, not just inspected

**(1) 11 call-site swaps, behaviorally correct.** Grepped: zero `yaml.safe_load` reads remain in
`plan-merge.py` (only 5 `yaml.safe_dump` **writes**, unchanged, correctly left on plain `yaml`).
The two sites that moved from `except (OSError, yaml.YAMLError)` to `except
harness_yaml.YamlParseError` (`_load_panel_value`, `_load_structured_value`) are NOT a coverage
loss: `harness_yaml.load_file` (`harness_yaml.py:245-262`) wraps `OSError` *and*
`UnicodeDecodeError` into `YamlParseError` itself (F-01, a documented prior fix). Verified live,
not just read: `harness_yaml.load_file('/tmp/does-not-exist.yaml')` raises `YamlParseError`
wrapping `FileNotFoundError` with the original errno text intact. Ran the full suite
(`env -u HARNESS_AGENT_TYPE python3 test-plan-merge.py`, HARNESS_AGENT_TYPE unset — set it and
`sign-approval` cases false-fail under DEC-120's agent gate, a harness artifact of my own shell,
not the PR): **285 PASS, 0 FAIL**, including the pre-existing `case_unparseable` (genuinely
malformed YAML syntax, not just duplicate keys) and both new issue-720 cases.

**(2) Does `harness_yaml.py` have a dump function? No — verified, not trusted.** AST-walked
every `def` in the file: 23 functions/classes, none named dump/save/serialize, no `yaml.dump`/
`yaml.safe_dump` call anywhere in the module. The 5 `safe_dump` write sites in `plan-merge.py`
correctly stay on plain `yaml` (D-03: this tool splices bytes, never re-renders a whole document
through a dumper — pre-existing decision, cited correctly, not invented by this PR).

**(3) `_load_pm()` in the new `case_f02_verify_signature_comparison_loop_is_not_dead_code` —
legitimate.** `_load_pm()` (`test-plan-merge.py:1825`) is a pre-existing helper, documented as
"the tool as a module, for unit-testing helpers no end-to-end path can reach," and was already
used by an unrelated pre-existing case (`:1846`, hash-computation helper) before this PR. The new
case's own docstring states the precise reason no front-door document can reach the branch
anymore (post-#720, a duplicate key is caught one layer earlier by `_verify_signature`'s own
reload, before the value-comparison loop runs) — this is exactly the situation the escape hatch
exists for, applied correctly rather than reached for out of convenience.

**(4) The 55-file, 0-failure on-disk survey — reproduced independently.** `git ls-files | grep
'plan\.yaml$'` = 55 (54 feature plans + template, matches the claim). Ran
`harness_yaml.load_str` over the text of every one: 0 failures. Claim holds exactly as stated.

**(5) Exception-message text changes — no caller depends on the wording.** Repo-wide grep for
production callers that subprocess `plan-merge.py` and inspect its stderr: only `gh-sync.py`
(two call sites, `:571-629` and `:1045-1063`), and both only display the **last line generically**
(`detail[-1] if detail else '(no output)'`) or the whole stripped blob — neither pattern-matches
a specific PyYAML syntax substring or line/column format. The refusal **prefixes**
(`UNPARSEABLE: proposal failed to parse:`, `cannot load panel value from {path}:`, etc.) that a
caller could plausibly match on are unchanged; only the embedded `{exc}` detail — previously raw
PyYAML text, now `harness_yaml`'s wrapped `"failed to parse YAML in {where}: {original}"` (or,
for the new duplicate-key case, `"duplicate key ... (DEC-156)"`) — differs. Nothing in the tree
matches on that inner text.

## Code grade (mechanical)

`code-grade.py --base b2e36bf3 --head 50da6493`: 4 records, all new test functions, all
**GRADE 4, PASS**, driver `abc`, bar 3. No `SEVERITY:` lines, no `RESULT: FAIL`. `code_grade: pass`.

## Notes, non-blocking

- `_parsed_value`'s `harness_yaml.load_str(raw, "<base plan>")` label is technically accurate
  (raw is always the base plan's decoded text at both call sites) but the exception is caught
  bare (`except harness_yaml.YamlParseError:`, no `as exc`) so the label is never surfaced —
  cosmetic only, not a finding.
- `fixtures/prior-harness_yaml.py.fixture` and `fixtures/prior-check-plan-routes.py.fixture`
  still describe the pre-#720 world ("`plan-merge.py`... required to import PyYAML plainly").
  These are intentionally frozen historical snapshots (last touched `4adb2219`, consumed only by
  `test-check-plan-routes.py`/`test-validate-digest.py` for unrelated diff-grading self-tests) —
  correctly untouched by this PR, not a defect.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Mechanical read-side migration verified correct on all 5 requested axes — 11 call-site swaps preserve every prior failure mode (incl. OSError via harness_yaml's own wrapping, confirmed live), no dump function exists in harness_yaml.py (AST-verified), the on-disk survey (55/0) reproduces exactly, the new _load_pm() escape-hatch use matches its pre-existing documented convention, and no caller depends on the changed inner exception text. Full suite 285/0, code-grade 4/4 clean."
  severity_max: none
  findings: 2
  must_fix: []
  spec_violations: []
  reviewed: "b2e36bf3983f73bb64d929054b0cd496f7f67a3e..50da6493fec683dd4819624ed6ad7f5b4cadc24b"
  human_commits_in_scope: []
  code_grade: pass
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-720-plan-merge-yaml/notes/review-harness-code-reviewer-pr1247.md
```
