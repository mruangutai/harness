# Security review — FEAT-26 (pr linkage recorded) — review_sha bad32441dfc0

## Verdict: PASS, severity_max info, 0 must_fix

## Scope
Diff base `3df18d3`..`bad32441dfc0`, 45 files. In scope: `gh-sync.py`'s new `_record_pr`/
`cmd_closes`/`parse_source_issues`, `check-state.sh`'s INV-28 block, `feature-schema.json`'s
new `pr` reader/`source_issues` field — these cross the untrusted-input boundary
(`feature.json` is unsigned) into a subprocess call and into text an operator pastes into
a PR body. Out of scope, checked and dismissed: 11 `feature.json` PR-number backfills
(pure data, grepped for secrets — none), `DECISIONS.md`/`INDEX` prose (grepped — none),
receipts/observations/notes (no code).

## What I checked

**1. Command construction (`_record_pr`, gh-sync.py:533-620).**
`args = ["pr", "list", "--repo", repo, "--head", branch, "--state", "merged", "--limit",
"10", "--json", "number"]`, run via `subprocess.run([GH] + args, ...)` — list-form argv,
no `shell=True` anywhere in the diff (grepped `shell=True|eval(|os.system|Popen(` across
every changed `.py`/`.sh` — zero hits). `repo` comes from `harness.json` via
`load_config()` (gh-sync.py:1013), operator-config, not feature.json. `branch` comes off
disk (`doc.get("branch")`, untrusted) but is never positional — it is always the
argument-value of `--head`, and both `argparse`-style and Go `pflag`-style (which `gh`
uses) parsers consume the very next token as a flag's value unconditionally, regardless
of a leading `-`. My prior expertise (G-02) flags positional args starting with `-` as
reinterpretable flags; this call has no untrusted positional arg, so that gotcha does not
apply here. Non-string/`"none"` branch is refused before the subprocess ever runs
(gh-sync.py:~556-558).

**2. Untrusted-input parsing.** `parse_source_issues` (plan.yaml, signed) and
`load_recorded`'s `gh.get("source_issues")` reader (feature.json, unsigned) both apply the
identical filter — `[n for n in si if isinstance(n, int) and not isinstance(n, bool)]`
(gh-sync.py:338 and :480) — non-list values return `[]`, non-int/bool members are dropped
silently, never raised. `_record_pr`'s `gh pr list` JSON parse: `json.loads(r.stdout)`
wrapped in try/except, non-list/empty/ambiguous (`len(found) > 1`)/non-int-number all
degrade to "no write, one printed line, exit 0" — no crash, no unbounded read (the process
list itself is bounded by `--limit 10`).

**3. Injection into rendered output (`cmd_closes`, gh-sync.py:868-884).** Reads through
`load_recorded`, not `parse_source_issues` directly — so the render path gets the SAME
int-only filter as the mirror path (same code, gh-sync.py:478-480), not a separate,
possibly-weaker one. `print(f"Closes #{n}")` — `n` is guaranteed `int` (non-bool) by that
filter before it ever reaches the f-string, so a `source_issues` member that is a string,
dict, or float cannot smuggle text into the "Closes #N" line even via a hand-edited,
unsigned `feature.json`. Cross-checked against `test-validate-feature-json.py`'s new
cases: `case_rejected_source_issues_non_integer` (`492.5`) and
`case_rejected_source_issues_quoted_number` (`"492"`) both assert the schema validator
rejects them too — defense in depth, not the only control. No test explicitly drives a
hostile string through `load_recorded` -> `cmd_closes` end-to-end, but the enforcement is
structural (one filter, one call site), not test-coverage-dependent — recorded as an info
note, not a gap.

**4. Shell quoting in INV-28 (check-state.sh:1044-1082).** The entire block reading every
`feature.json` and building the remedy line is Python, inside a **quoted** heredoc
(`<<'PY'`, check-state.sh:24) invoked as `python3 - "$root"` — quoting the delimiter means
bash performs zero expansion inside the body, so there is no bash variable interpolation
of feature ids or paths at all, and no `eval`-shaped construct (grepped, zero hits). The
"remedy command" string (`gh-sync.py record-pr {relpath}`) is composed as a Python
f-string appended to a `warn` list and only ever printed — never passed to `subprocess`,
`os.system`, or `eval`. Dispatch item 4's concern does not apply to this diff.

**5. Data exposure.** No new logging of tokens or credentials. `gh_cost_log.measured`
(pre-existing mechanism, unchanged by this diff) persists `argv` — for this call site,
`repo` and `branch`, both already non-secret and already on disk in `feature.json`/
`harness.json` — to a log file; this is the same accepted, pre-existing pattern applied to
a new call site, not a new exposure class. `gh` stderr on a `pr list` failure is truncated
to 200 chars and printed to stdout only (gh-sync.py:~577-578) — never written into
`feature.json` or any persisted artifact. Grepped the full diff for
`token|secret|password|api[_-]?key|ghp_|github_pat|Authorization|Bearer` — zero
credential-shaped hits (matches were all `orchestrator_context_warn_tokens`, an unrelated
budget field, and prose using the word "token" to mean substring).

## Findings
None at med/high/critical. No must_fix.

## Threat model
- boundary: feature.json (unsigned, disk) -> `_record_pr`'s `gh` subprocess argv — mitigated: true (list-form argv, branch always a flag-value, never positional; repo is operator-config not feature.json)
- boundary: feature.json (unsigned, disk) -> `cmd_closes`'s stdout (operator pastes into PR body) — mitigated: true (int-only filter enforced on the render path via shared `load_recorded` code, backed by a second, independent schema-validator check)
- boundary: gh stdout/JSON (external, GitHub) -> `_record_pr`'s parse — mitigated: true (try/except, ambiguity and non-int guards, all degrade to no-write rather than crash or wrong write)
- boundary: check-state.sh INV-28's feature-id/path interpolation -> shell — mitigated: true (pure Python inside a quoted heredoc; no shell expansion occurs)
