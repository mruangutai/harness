# Security review — FEAT-56 central onboarding model (c0)

Diff `4b5dbb23..6f34e289`, pin `6f34e289`. All reads via `git show 6f34e289:<path>`.

## Verdict: PASS, `severity_max: low`

No must-fix. One low-severity documentation gap and one info-level, dismissed-with-evidence
observation. My SC-04 quarter (4/4 files): **met**.

## 1. Audit of the one production change — `factory_config.product_config_report()` + `--check-product-configs [--repo]`

`.claude/skills/harness/bin/factory_config.py` (79 new lines: `product_config_report`,
`_check_product_configs`, the two argparse flags). `product_config`, `board_for`,
`validate_board`, and the remote-read/no-disk-fallback design are **0 lines changed** — pre-existing,
confirmed by diff.

**Data exposure — checked live, dismissed.** `product_config_report` catches only `FleetError`;
`detail = str(exc)`. Traced the chain: `factory_gh.file_at_ref` → `run_gh` builds `GhError` whose
`str()` is `factory_cli.body(what, value, next_step)` — never raw HTTP body/headers — where
`next_step = _first_line(stderr) or _first_line(stdout)` (`factory_gh.py:213-214`, unchanged).
Ran three live `gh api repos/.../contents/...` calls against this sandbox's authenticated `gh`
(nonexistent repo, nonexistent path in a real repo, a repo I lack access to): all three render
identically as `gh: Not Found (HTTP 404)` with a generic JSON body — no token, no auth header, no
distinguishing "exists vs. no access" signal, i.e. it doesn't even leak repo-enumeration info. This
text is what lands in the `--check-product-configs` stdout payload's `members[].detail` and in the
`factory_cli.fail` stderr line named in the dispatch. Assessed and dismissed: the forwarded string is
gh's own sanitized human message, not a raw response; empirically verified, not assumed. Residual
note (info, not a finding): this is pre-existing `GhError` plumbing (`factory_gh.py` untouched here)
now surfaced through a *new*, operator-facing CLI report — worth re-checking if a future `gh`
version changes its error format, but nothing to fix today.

**Injection / argument handling — dismissed, no finding.** `--repo` is resolved through
`repo_entry(fleet, name)` (exact dict-key match) *before* anything reaches a subprocess; an
undeclared name raises `FleetError` and never reaches `gh` (`factory_config.py` `_check_product_configs`
→ `repo_entry`). `file_at_ref`'s argv is list-form, no `shell=True`
(`factory_gh.py:917,154-156`); the positional API path is always `f"repos/{repo}/contents/{path}?ref={ref}"`,
which literally starts with `repos/`, so a `repo` value starting with `-` still can't be
misread as a flag by `gh`. `ref` (`default_branch`) and `repo` both come from
`.harness/factory/fleet.yaml`, which is `main-session-direct` lane (not squad- or
fleet-member-writable) — an actor who could poison that value already holds fleet-config write
access, so this is P-02 (no escalation), not a finding.

**STRIDE on the onboarding model — Tampering/Elevation, mechanism settled, documentation gap found.**
Whoever holds push/merge access to a fleet member's default branch fully controls the
`.harness/harness.json` the central factory subsequently treats as authoritative for that repo
(board target, and — per this same file's own contract in other, unchanged modules —
`test_kinds.*.cmd`, which downstream tooling executes) — this design is DEC-220/DEC-174, binding,
correctly not reopened here. What I found unstated: **none** of the four files I own, nor T-07's
doc sweep (`SPEC.md`, `BUILD.md`, `README.md`, the new `DEC-220` entry), tell the operator that this
delegation of trust exists — that landing `harness.json` on a repo's default branch hands whoever can
write that branch the same authority as if they had `.harness/harness.json` write in the control
plane itself. `DEC-220` states *what* is chosen (`.harness/harness/docs/DECISIONS.md:4306`ff.) but not
*who this trusts*. Rated **low**, not high: the mechanism itself predates this diff (0 lines changed
in `product_config`/`board_for`), and every failure mode here is fail-closed — a bad/unreachable
config raises `FleetError` and blocks (`--check-product-configs` exits 2), it never silently
downgrades or falls back. Filed against **T-01** (owner of the onboarding narrative,
main-session-direct lane), applicable across T-05/T-07/T-08's doc surface too — a one-sentence
addition to `harness-init/SKILL.md`'s "Land harness.json" step ("this hands the pusher the same
trust as a control-plane edit") would close it.

## 2. My SC-04 quarter — 4/4 files, `met`

| # | File | `file:line` @ 6f34e289 | met? |
|---|---|---|---|
| 1 | `.claude/skills/harness/templates/harness.json` | `:2` — `"_template": "Canonical harness.json. /harness-init instantiates this as the control plane's own .harness/harness.json, and as a fleet member's own .harness/harness.json which must be committed to that repository's default branch..."` | met |
| 2 | `.claude/skills/harness/templates/team-config.yaml` | `:4` — `# .harness/team-config.yaml - check-domain.sh reads only that file and a product` (continues line 5 "repository never carries one") | met |
| 3 | `.claude/skills/harness/templates/BRIEF.md` | `:2` — `<HARNESS_FEATURE_TREE_ROOT>/.harness/<segment>/features/<FEAT>/BRIEF.md; harness-pm owns it thereafter,` | met, with a noted nuance below |
| 4 | `.claude/skills/harness/references/github-mirror.md` | `:23` — `own \`harness.json\` on its \`default_branch\`, the file onboarding lands there; for the control plane it` | met |

Nuance on #3: `BRIEF.md` states only the fleet-registration half (its own file lands in the central
per-segment tree) — it never claims to *be* or name the product-resident file, because it isn't one.
Graded `met` because it makes no claim inconsistent with the two-part model and its scope (per
`plan.yaml` T-05 item 4 and the task's own `verify:` grep for `<segment>/features`) was correctly
narrow — a BRIEF template has no reason to restate harness.json's role. Recording this rather than
silently accepting, per instruction: a stricter reading of SC-04's literal "states...plus one
product-resident file" as a *per-file, both-halves-every-time* requirement would flip this file to
`not_met`; I did not adopt that reading because three of my other four files, and every plan.yaml
task intent for T-05, treat the requirement as "accurately describes the piece of the model
relevant to this file," which #3 does.

## 3. Lead's offered angle — T-01 step 2's "land it by hand" instruction

`.claude/skills/harness-init/SKILL.md:160-163` (git show 6f34e289): "Land `.harness/harness.json` on
that repository's `default_branch`. Harness has no write route into a product repository... The main
session asks the operator for this commit or PR; do not continue until it is on the default branch."

**Concur it is incomplete, do not escalate it to a security finding.** It names no path for "the
operator cannot push" (protected branch requiring review, no write access, org policy) — no
"escalate", "ask a repo admin", "file it and move to another member" branch exists; the prose reads
as an unconditional wait. From an access-control angle this is worth a documentation fix (silently
stalling a flow with no named next step is a process defect a later operator will hit), but it is
**not itself a security gap**: the instruction is fail-closed in the direction that matters — no
code path here lets onboarding proceed *without* the config landing (step 4's
`--check-product-configs ... must exit 0` before step 5), so there is no unsafe fallback for a
missing-access operator to be routed into by mistake. I did not add this to must_fix; it's a UX/PM
completeness gap, not a defect this role gates on.

## Assessed and dismissed (recorded per instruction)

- `workspace_root: "/"` guard (`factory_config.py:load_fleet`, `os.path.dirname(os.path.normpath(...))`
  check) — pre-existing (0 lines changed here), already carries its own review-panel provenance
  comment; re-confirmed fails closed. Not this diff's own surface.
- `_value_from_argv` / `_what_from_argv` in `factory_gh.py` — unchanged, not exercised by
  `file_at_ref`'s explicit `value=` construction; no new exposure.
- Rest of the 56-file diff (T-02/T-03/T-04's tests, T-06/T-07's prose, receipts, notes, `plan.yaml`,
  `BRIEF.md`, agent-file duplication) — no input/output/credential/third-party-data surface; prose,
  comments, docstrings and test fixtures only, confirmed by `git diff --stat` census.

```yaml
VERDICT: PASS
DIGEST:
  headline: One production change (product_config_report + --check-product-configs) has no injection or credential-exposure defect; one low-severity documentation gap (unstated trust boundary for remote-read product config) filed against T-01/T-05/T-07/T-08; SC-04 quarter (4/4) met.
  in_scope: true
  scope_reason: "The diff's sole production behaviour change makes a network read of third-party repository content and forwards third-party CLI error text into an operator-facing report — squarely OWASP data-exposure and STRIDE-tampering surface; the doc rewrite around it (T-01/T-05/T-07/T-08) is where the corresponding trust boundary should be, and mostly is, documented."
  severity_max: low
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "gh CLI error text -> --check-product-configs stdout/stderr", stride: I, mitigated: true }
    - { boundary: "--repo CLI flag -> subprocess argv (file_at_ref)", stride: T, mitigated: true }
    - { boundary: "fleet member's default_branch -> product_config (remote read, no disk fallback)", stride: T, mitigated: false }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-56-central-onboarding-model/.harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-security-reviewer-c0.md
```
