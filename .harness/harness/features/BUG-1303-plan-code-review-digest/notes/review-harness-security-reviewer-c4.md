# Security review — BUG-1303 — cycle 4 (pinned 59c5de97)

## Verdict: PASS — no security surface violated; one real integrity question checked and cleared

## Census (every file read, all nine contract paths + full diff)

| Path | What changed | Security-relevant? |
|---|---|---|
| `.claude/agents/harness-code-reviewer.md` | Write-path doc moved from control-plane note to per-feature note; `code_grade`/`reviewed: plan:` doc fields added | No — doctrine text only, no executable logic, no new write grant (matches existing `<HARNESS_FEATURE_TREE_ROOT>` pattern DEC-214 already establishes elsewhere) |
| `.omp/agents/harness-code-reviewer.md` | Byte-identical twin of the above | No |
| `.claude/skills/harness-code-review/SKILL.md` | New "plan-phase review" doc section + one red-flag row | No — prose only |
| `.claude/skills/harness/templates/harness.json` | `bugfix.always` emptied, two conditional `when` legs added (DEC-217) | No injection/auth/secret surface — a QA test-matrix policy value, consumed by pre-existing predicate matching elsewhere, unchanged by this diff |
| `.harness/harness.json` | Same matrix change + new `_matrix_provenance.bugfix` block citing DEC-217 | Same as above |
| `.harness/harness/docs/DECISIONS-INDEX.md` | Two index rows (DEC-216, DEC-217) | No |
| `.harness/harness/docs/DECISIONS.md` | Full DEC-216 and DEC-217 bodies | No — governance record, no code |
| `tests/unit/test-config-shape-matrix.py` | New assertions comparing `harness.json`/template values and `DECISIONS.md` text against expected constants | Read-only: `_load()` (json/yaml load) and `open(DECISIONS_MD, encoding="utf-8")` in read mode. No writes anywhere in the diff. |
| `tests/integration/test-validate-digest.py` | New `run_documented_contract_cases()` + helpers (DEC-216 guard); one new line wiring it into `main()` | Read-only: `_contract_source()` opens fixed, hardcoded repo paths (`.omp/agents/*.md`, `.claude/skills/*/SKILL.md`) via bare `open(path)` (default `'r'`), builds and returns strings. No `open(..., "w")`, no `tempfile`, no `os.remove`, no `chmod` anywhere in the actual diff hunks (confirmed against `git diff` — exactly two hunks: `+254` lines after line 239, `+1` line in `main()`, `0` deletions). |

Grepped the full nine-path diff for credential-shaped strings (`password|secret|token|api[_-]?key|credential|bearer|ssh-rsa|BEGIN (RSA|OPENSSH|PRIVATE)|AKIA…`) — only hits are `reviewed_token`/`plan-mode token` (a text-token variable name, not an auth token) and one pre-existing `_test_kinds_note` string containing the literal word "token"-adjacent prose; none are credentials.

## Q-E: the one plausible integrity surface — test perturbation and its restore path

The dispatch is right that these two test files execute Python and (elsewhere in the same file)
demonstrate red-capability by mutating a copy of the validator on disk. I checked whether *this
diff's own added code* does that, and separately whether the pre-existing perturbation machinery
the diff calls into is safe.

**This diff's added code (the +255 lines) never writes to disk at all.** Every new function in
`test-validate-digest.py` (`_skill_documented_block`, `_agent_documented_block`,
`documented_block`, `documented_contract_gaps`, `documented_contract_results`,
`_required_contracts`, `_reviewer_plan_mode_results`, `_discrimination_ok`,
`_synthetic_contract_results`, `run_documented_contract_cases`) and in
`test-config-shape-matrix.py` (`_config_has_bugfix_predicates`,
`case_project_config_routes_bugfix_kinds_by_surface`,
`case_template_config_routes_bugfix_kinds_by_surface`,
`case_decision_217_exists_and_defines_bugfix_predicates`) reads real repo files by a fixed,
hardcoded path (`CONTRACT_SOURCES` dict, `DECISIONS_MD`, `PROJECT_CONFIG`, `TEMPLATE_CONFIG`) and
does string/dict comparison — no `open(..., "w")`, no `tempfile`, no `shutil`, no `os.remove`, no
`chmod` appears anywhere in the diff hunks (verified directly against `git diff` output, not
inferred).

**The perturbation/mutant machinery the dispatch is describing already existed before this
commit and is untouched by it.** `_install_mutant`/`_remove_mutant`, the DEC-156 `tempfile.mkdtemp`
fixtures, and the red-capability runners (`run_empty_red_case`, `run_dec156_worktree_red_case`,
the BUG-919 mutant runner) are all present verbatim in the merge-base revision
(`git show <base>:tests/integration/test-validate-digest.py | grep _install_mutant/tempfile.mkdtemp`
confirms identical line content at the base). I read the actual mutant-install call sites anyway
(`run_empty_red_case`, `run_dec156_worktree_red_case`, BUG-919 case) to answer the dispatch's
three sub-questions on that pre-existing code, since it's what the two files' "red-capability"
actually refers to:

- **Writes outside `tests/**`/temp dir?** No. Every mutant path is built as
  `os.path.join(isolated_bin(tempfile.mkdtemp()), ".validate-digest-<case>-<pid>.py")` — a brand
  new file under a freshly minted temp directory, never the real `validate-digest.py` in place and
  never any tracked path.
- **Restored on the failure path, not just success?** Yes. Each case wraps the mutant install/fire
  sequence in `try: ... finally: shutil.rmtree(iso_root, ignore_errors=True)` — the temp root (and
  the mutant inside it) is removed whether the body raises or returns cleanly.
- **Leaves a modified tracked file behind if it raises mid-way?** No tracked file is ever written
  to in the first place (the mutant is a new file in an isolated temp dir; the real
  `VALIDATE`/`validate-digest.py` is only ever opened for read via `with open(VALIDATE,
  encoding="utf-8")`), so there is nothing tracked to leave modified.

**Ruling: no finding.** The integrity surface is real but was already closed before this diff, and
this diff adds no new instance of it — only pure-read comparisons.

## Out of scope, explicitly

DEC-217's substance (whether bugfixes should require a unit test) is a delegated Advisor ruling
this dispatch marks binding and non-relitigatable; noted, not assessed, per instruction.

## Read-only compliance

No file was perturbed during this review. Only `git diff`/`git show` (read) and `read`/`grep` tool
calls were used; nothing needed byte-restoration.

```yaml
VERDICT: PASS
DIGEST:
  headline: "No OWASP/STRIDE-relevant surface in the 9 reviewed files; the one plausible test-integrity question (mutant write/restore) traces to pre-existing, already-safe machinery this diff never touches."
  in_scope: true
  scope_reason: "Diff is agent/skill doctrine, JSON policy config, decision records, and two test files. No auth, secret, injection, or data-exposure surface in the 7 non-test files. The 2 test files DO execute Python and (elsewhere in the same file, pre-existing) perturb a copy of the validator on disk for red-capability, so that mechanism was checked concretely; the +255 lines this diff actually adds are pure read-only string comparisons with zero writes."
  severity_max: none
  findings: 0
  must_fix: []
  threat_model:
    - { boundary: "test fixture write (mutant install for red-capability demos)", stride: T, mitigated: true }
    - { boundary: "this diff's new contract-guard code reading repo markdown/json by hardcoded path", stride: I, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1303-plan-code-review-digest/.harness/harness/features/BUG-1303-plan-code-review-digest/notes/review-harness-security-reviewer-c4.md
```
