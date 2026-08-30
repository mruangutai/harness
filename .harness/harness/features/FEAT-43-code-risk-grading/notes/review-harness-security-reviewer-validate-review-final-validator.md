# FEAT-43 final pinned security review — FAIL

**BLUF:** The exact pinned change is still not safe to ship. The grading command itself reports
`code_grade: fail` because `test-check-plan-routes.py:1399` is a new grade-1 function. Independently,
two high-severity enforcement findings remain: reviewer-controlled revision text is passed to Git as
options and can both bypass `n_a` enforcement and activate Git's output-file write option; and
repository-controlled filenames are emitted raw to a human terminal/log, permitting control-sequence
or record injection. The former NUL-unsafe omission defect is fixed.

## Pin and complete census

Both objects resolve as commits:

- base: `df63193f7ec9798d9660904e0e4e7c78d52358f5`
- review: `45328d7a280d251a94b09672a7b6724d55a79f83`

`git diff --name-only df63193..45328d7a280d251a94b09672a7b6724d55a79f83`
returns exactly **48 paths**, identical to the shared census. Every path was inspected from the
committed diff before scoping:

- **Agent delivery (12):** `.claude/agents/{harness-ai-dev,harness-backend-dev,harness-code-reviewer,harness-data-engineer,harness-dev-ops,harness-frontend-dev}.md`; `.omp/agents/{harness-ai-dev,harness-backend-dev,harness-code-reviewer,harness-data-engineer,harness-dev-ops,harness-frontend-dev}.md`.
- **Guidance (3):** `.claude/skills/harness-code-review/SKILL.md`; `.claude/skills/harness-code-risk-grading/SKILL.md`; `.harness/glossary.md`.
- **Runtime/enforcement (6):** `.claude/skills/harness/bin/{check-plan-routes.py,code-grade.py,code_grade.py,gate_policy.py,run-unit-tests.sh,validate-digest.py}`.
- **Targeted tests (5):** `.claude/skills/harness/bin/{test-check-plan-routes.py,test-code-grade-cli.py,test-code-grade.py,test-gate-policy.py,test-validate-digest.py}`.
- **Configuration/contract (3):** `.harness/harness.json`; `.harness/harness/features/FEAT-43-code-risk-grading/answers/Q1-t09-owner-resolver.md`; `.harness/harness/features/FEAT-43-code-risk-grading/plan.yaml`.
- **Evidence outputs (19):** `notes/qa-build-qa{,-rerun}.md`; `notes/receipt-harness-backend-dev-{T-01-c0,T-01-c1,T-02-c0,T-02-c1,T-06-c0,T-07-c0,T-07-c1,simplify-apply,simplify-efficiency,simplify-reuse}.md`; `notes/receipt-harness-dev-ops-{T-03-c0,T-03-c1,simplify-altitude,simplify-simplification}.md`; `notes/research-T-10-t10-product.md`; `notes/ship-review-t06-eng.{html,md}` (all under the feature directory).

## Security scope and threat model

**In scope.** The diff crosses four trust boundaries: reviewer-authored digest fields into Git
subprocess argv; contributor-authored Git paths into a human/agent-interpreted report; branch checkout
configuration into the owner checkout's authorization resolver; and configuration/digest data into
gate decisions. OWASP-shaped review covered command/option injection, path handling, input validation,
secrets/data exposure, output injection, dependencies, auth, SSRF, and redirects. There is no new
network, dependency, credential, session, tenant-data, redirect, template, SQL, CSV, or spreadsheet
surface.

| Boundary | STRIDE | Mitigated? | Result |
|---|---|---:|---|
| reviewer `reviewed` field → `git diff` argv | T/E | no | SEC-01 |
| Git pathname → text report/terminal | T/E | no | SEC-02 |
| Git pathname census → grader | T/R | yes | NUL-delimited status parsing and odd-name fixtures close the prior omission |
| branch worktree → owner authorization manifest | T/E | yes | canonical owner resolver, loud deviation, unreadable-owner refusal |
| JSON gate configuration/digest → verdict | T | partly | ordinary shape/vocabulary failures are loud; revision option injection remains |
| committed notes/HTML → reader | I/T | yes | no secrets; static HTML has no script and rendered prose is escaped |

## Must-fix findings

### SEC-01 — high — reviewer revision text is interpreted as Git options

`validate-digest.py:540-555` splits the reviewer-controlled `reviewed` string and passes both pieces
directly after Git options. It neither resolves each value to a commit OID nor prevents an option-like
value. The same unsafe construction exists in `code-grade.py:73-93` and
`code_grade.py:279-317`.

**Actor/access/gain:** a compromised or prompt-injected code-review agent can submit the otherwise
schema-valid, nominally read-only return `reviewed: "--output=/dev/null..HEAD"`, `code_grade: n_a`,
`VERDICT: PASS`. The Stop-hook validator accepts it as `digest ok`; Git treats the base as its
`--output` option, emits no pathname census, and reports success. Replacing `/dev/null` with a
writable path activates Git's output-file write under the validator process, crossing the reviewer's
read-only boundary, while also bypassing the Python-diff `n_a` check. A second probe with
`--no-patch..HEAD` was likewise accepted, proving the false-clean path without relying on file output.
The CLI itself also returned `PASSING: 0`, exit 0, for
`--base=--no-patch --head=HEAD`.

**Remedy constraint:** resolve both revision inputs independently to commit OIDs with end-of-options
handling before every diff/show, reject anything that does not resolve to a commit, and pass only the
resolved OIDs onward. Add a regression proving option-like revisions are rejected and no selected
output path is created or changed. Fix all three consumers; fixing only the validator leaves the
manual grading command bypassable.

### SEC-02 — high — raw Git paths inject terminal/log records

`code-grade.py:110-127` interpolates `record['path']` directly into the text report. The committed
integration fixture at `test-code-grade-cli.py:96-124` deliberately creates
`src/rename\nnew.py` and asserts the literal raw newline appears after `PATH:`. Git paths may also
contain escape/control bytes.

**Actor/access/gain:** any contributor able to add a path to the reviewed commit can name a Python
file with embedded newlines that forge `RESULT`, `SEVERITY`, or `PASSING` records, or with terminal
control sequences interpreted when the reviewer opens the report. The contributor thereby tampers
with the human/agent review channel and can manipulate the reviewer's terminal state. The process
exit code is not sufficient mitigation because the feature explicitly makes this text the actionable
human review record.

**Remedy constraint:** encode every untrusted path in text output with one reversible, single-line
representation (for example JSON/C-style escaping), including parse-error and `UNGRADED` output.
Assert that odd paths round-trip but no literal newline, carriage return, tab, or escape byte crosses
the record boundary. JSON mode is already escaped by `json.dumps`.

## F-01 through F-12 disposition

| Prior | Final disposition | Evidence |
|---|---|---|
| F-01 grade-1 gate | **OPEN / final blocker.** Two former grade-1 functions improved, but `test-check-plan-routes.py:1399 case_27` remains grade 1: cyclomatic 6, cognitive 6, ABC 50.0, driver ABC, test bar 3, `RESULT: FAIL`, severity high. | real pinned CLI run |
| F-02 comprehension filters | **Closed.** Each comprehension `for` and `if` now increments cyclomatic; the 12-fixture test reports PASS. | `code_grade.py:201-212`; `test-code-grade.py` |
| F-03 deletion behavior | **Closed.** Both changed-file readers consume status records and omit `D`; the CLI odd-path fixture deletes `src/deleted.py` and asserts it is neither graded nor `UNGRADED`. | `code-grade.py:73-93`; `code_grade.py:302-317`; targeted CLI PASS |
| F-04 `n_a` basis | **Original mechanism closed, enforcement still bypassable.** `n_a` now checks the declared reviewed diff rather than `files_touched`, but SEC-01 supplies an option-injection bypass and write primitive. | `validate-digest.py:540-555,752-760`; crafted digest probes |
| F-05 `info`/`none` vocabulary | **Closed.** Canonical severity is `none`; `info` is rejected, and ordinary invalid values/configuration raise named policy errors. | targeted gate-policy and digest scripts PASS |
| F-06 predecessor discrimination | **Closed.** Both fixtures use immutable `PRE_FEATURE_REVISION=df63193…` and `git show` that object, not `HEAD`; route case 27b and digest predecessor acceptance passed. | `test-check-plan-routes.py:1379-1459`; `test-validate-digest.py:1741-1809` |
| F-07 derived fixtures | **Closed.** Exactly 12 hand-derived fixtures span grades 1–5 and a minimum-count assertion is present. Independent re-derivations: empty = cyc 1/cog 0/A=B=C=0/ABC 0/grade 5; eleven-operand BoolOp = ten extra conditions/cyc 11/C 10/ABC 10/grade 2; comprehension fixture = one `for` + eight filters → cyc 10, A 1/B 1/C 11/ABC 11.1/grade 3. | `test-code-grade.py:19-112,296-328`; targeted PASS |
| F-08 adverse ordering | **Closed behaviorally.** The CLI sorts changed paths and final records; two copied repos created `alpha.py`/`zeta.py` in opposite orders and produced byte-identical stdout/status. | `code-grade.py:73-93,137-158`; targeted CLI PASS |
| F-09 named metric movement | **Closed.** Six pairs assert the named metric itself moves: four worse and two better. | `test-code-grade.py:48-112,313-320`; targeted PASS |
| F-10 NUL-safe paths | **Closed for census, superseded for rendering by SEC-02.** Both readers use `-z`; library and CLI fixtures preserve tab/newline rename paths through grading. | `code-grade.py:73-93`; `code_grade.py:302-317`; both targeted scripts PASS |
| F-11 approximation label | **Closed.** Every record carries `cognitive_method: Sonar-style approximation`; text prints it beside the score and JSON preserves it. | `code-grade.py:50-56,110-127`; targeted CLI PASS |
| F-12 per-record bar/outcome | **Closed.** `_record` derives bar 3 for configured tests and 4 otherwise; text emits `BAR` and `RESULT` for every record and JSON contains both fields. | `code-grade.py:42-56,110-127`; targeted CLI PASS |

## Pinned code-grade result and reason record

Exact command:

`/opt/homebrew/bin/python3 .claude/skills/harness/bin/code-grade.py --base df63193 --head 45328d7a280d251a94b09672a7b6724d55a79f83`

Outcome: **exit 1; `code_grade: fail`; `PASSING: 81`; no `UNGRADED` paths.** The complete
below-bar set is 17 records: one grade 1, nine grade 2, and seven grade 3. Every emitted record,
including the 81 passing records, carried its derived `BAR` and `RESULT`.

- Grade 1: `test-check-plan-routes.py:1399 case_27` — 6/6/50.0, driver ABC, bar 3, FAIL.
- Grade 3 production failures: `check-plan-routes.py:91 resolution_manifest` (8/11/22.0);
  `code-grade.py:73 _diff_paths` (7/11/19.2); `code_grade.py:232 _records.collect`
  (4/11/9.1); `code_grade.py:302 _changed_python_files` (6/11/14.6);
  `gate_policy.py:33 load_policy` (8/11/17.3); `gate_policy.py:75 evaluate_qa`
  (8/10/17.0); `validate-digest.py:540 reviewed_python_change` (9/7/13.7). Each had
  production bar 4 and `RESULT: FAIL`.

Every grade-2 demand and written reason:

| Function (metrics; bar/outcome) | Written reason |
|---|---|
| `check-plan-routes.py:775 main` (10/13/30.9, ABC; 4/FAIL) | One auditable route-check transaction owns mode/root selection, owner manifest resolution, plan traversal, cross-feature checks, reporting, and status. |
| `code-grade.py:137 main` (9/11/27.3, ABC; 4/FAIL) | The CLI boundary coherently owns argparse validation, one of two report modes, deterministic serialization, and process status. |
| `code_grade.py:322 _body_hashes.collect` (9/18/17.3, cognitive; 4/FAIL) | The local recursive walker keeps qualified names, docstring exclusion, stable body hashing, and nested traversal in one identity algorithm. |
| `code_grade.py:350 gated_set` (8/25/22.6, cognitive; 4/FAIL) | This is the core pre-image transaction: rename/path resolution, same-name and same-body matching, and one partition into gated versus informational records. |
| `test-code-grade-cli.py:96 test_diff_and_determinism` (3/3/29.2, ABC; 3/FAIL) | One integration repository intentionally couples deletion, odd rename, and adverse-order copies to prove the related diff/output contract. |
| `test-code-grade.py:136 check_changed_function_resolution` (5/0/33.3, ABC; 3/FAIL) | SC-07/08 require one seven-way repository fixture with exact-set and individual exclusion assertions. |
| `test-code-grade.py:296 main` (8/11/35.7, ABC; 3/FAIL) | The test entry point aggregates the fixture oracle, band floor, direction pairs, changed-set, worked-example, and delivery checks into one suite result. |
| `test-gate-policy.py:55 check_policy_loading` (1/0/36.1, ABC; 3/FAIL) | One configuration-boundary matrix keeps valid keyed loads and all malformed/missing/unreadable variants adjacent and comparable. |
| `test-validate-digest.py:1760 run_code_grade_cases` (11/16/38.1, cyclomatic+cognitive+ABC; 3/FAIL) | One cross-module fixture lifecycle proves `n_a`, fail/pass consistency, policy switching, missing gates, and predecessor discrimination together. |

These reasons satisfy the requested record but cannot override the grade-1 high blocker or the two
security findings.

## Targeted evidence and adequacy gaps

- Pinned grader command above: exit 1; full result summarized above.
- `/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-code-grade.py` → exit 0, `PASS test-code-grade`.
- `/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-code-grade-cli.py` → exit 0, `PASS test-code-grade-cli`.
- `/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-gate-policy.py` → exit 0; all named policy/error checks passed.
- `/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-validate-digest.py` → exit 0; 65/65 CLI, joint hint, code-grade/policy, 14/14 hook, 24/24 T-09, and 2/2 template groups passed.
- First direct route-test invocation selected Homebrew for the parent but did not prepend it to child `PATH`; it exited 1 with 36 environmental `python3 -P` failures. This is not smoothed over as source evidence. Reissue with `PATH=/opt/homebrew/bin:/usr/bin:/bin /opt/homebrew/bin/python3 .claude/skills/harness/bin/test-check-plan-routes.py` → exit 0, `ALL PASS`, including 27a/27b/27c.
- Crafted validator probes with `reviewed: "--no-patch..HEAD"` and `reviewed: "--output=/dev/null..HEAD"`, `code_grade: n_a`, `VERDICT: PASS` → both exit 0, `digest ok`.
- `/opt/homebrew/bin/python3 .claude/skills/harness/bin/code-grade.py --base=--no-patch --head=HEAD` → exit 0, `PASSING: 0`.
- Secret sweep across the entire 48-file committed diff found no credential, token, password, private-key, or API-key value. Committed receipts expose absolute workstation paths/usernames, assessed as low-value local metadata rather than credentials or cross-user data.

Adequacy gaps: the immutable pin still fails its own grade-1 rule; no test rejects Git option-like
revision values; the odd-path test currently requires unsafe raw rendering instead of safe encoding.
SC-11 remains a separate UAT criterion and was not substituted by this security review.

**Files touched:** `.harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-security-reviewer-validate-review-final-validator.md` only.
