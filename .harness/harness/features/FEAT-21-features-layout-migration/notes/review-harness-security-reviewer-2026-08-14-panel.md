# Security review — FEAT-21 range panel — 62fef85..b1d3925

Range reviewed: `git diff 62fef85..b1d3925` (5 commits: `4b16f47`, `ea937b1`, `5afa7e3`, `d033b9d`,
`b1d3925`), not `b1d3925^..b1d3925`. Priority per dispatch: the two commits nobody has reviewed
(D-08's label fix inside `d033b9d`, and all of `b1d3925`).

## BLUF

The authorization surface (`team-config.yaml` grants, `check-domain.sh` shape regexes/`SWEEP_GLOBS`,
`check-state.sh` discovery, `check-plan-routes.py`, `validate-feature-json.py`, `.gitignore`) moved
coherently to the `.harness/<repo>/features/` layout. The wildcard-matching mechanism
(`harness_boundary.glob_to_re`: `*` -> `[^/]*`, never crosses `/`) is **unchanged in this range** and
was already segment-safe before the migration, so inserting one more wildcard segment did not widen
any grant beyond one repo-segment level — confirmed by reading the matcher and by running
`test-check-domain.py` (14/14), `test-check-state.py`, `test-check-plan-routes.py`,
`test-bash-write-guard.py`, `test-layout-migration.py`, all exit 0. `git diff --name-only
b1d3925..835692a -- .claude/skills/harness/bin/` is **empty** — no `bin/` source changed between the
review SHA and the working tree these suites ran from, so the green runs verify `b1d3925` itself, not
a later state. `b1d3925` itself (`git show --stat`) touches only `test-layout-migration.py`
(case-20 parity, made to run the real gate instead of a hand-mirror) — test-only, and that suite's
green run (including the new case-20 parity block) *is* the coverage for it. No must-fix findings.
`severity_max: info` (G-07 — scoped in, zero new findings, not `n/a`).

## What was checked against the five named priorities

**1. `team-config.yaml` grant widening.** Diff is a mechanical `.harness/features/*/...` ->
`.harness/*/features/*/...` rewrite across all 43 grants (verified via full diff read). The inserted
`*` is `[^/]*` in `harness_boundary.py` (untouched in this range) — bounded to one path segment, no
cross-slash match, `..` resolved away by `real()`/`os.path.realpath` before any glob comparison, so
no traversal vector. Cross-segment reachability (an agent's `.harness/*/...` grant resolving against
a *second* repo's segment) is real in principle but **this repository has no second segment staged**
(`mruangutai/harness` is deliberately absent from `fleet.yaml`, BRIEF "Out" section) — this is the
already-recorded coverage gap, not re-filed. The FEAT-21 precommit security review
(`notes/review-harness-security-reviewer-2026-08-14-precommit.md`, ground-pinned at `ea937b1`,
predates `d033b9d`) independently measured the same positive/negative `--resolve` set the dispatch
describes (5 positives naming the intended agent, 4 negatives → `NOBODY`, one cross-segment negative
correctly grantable and explicitly called D-01's accepted cost) — re-verified by rerunning
`test-check-domain.py`, still 14/14.

**2. `check-domain.sh` shape regexes / `SWEEP_GLOBS` — fail-open hunt.** Diff is the anchor-preserving
rewrite `^\.harness/features/[^/]+/...` -> `^\.harness/[^/]+/features/[^/]+/...`; `^`/`$` anchors
intact, `[^/]+` (never `.*`) throughout, one inserted segment, nothing else touched. No branch found
where a parse/permission failure now yields allow-not-deny — the DEC-101 fail-open carve-out (absent
manifest) is pre-existing and unchanged, and `test-check-domain.py`'s fail-closed cases
(malformed manifest, non-UTF-8 manifest, malformed `state.yaml`) all still pass.

**3. D-08 label fix, `check-state.sh:55-59` (`_feat_dirs`/`fpath()`).** Read the full mechanical diff
(~30 call sites). `fpath()` only ever receives `feat` values derived from `os.path.basename()` of
directories the script itself discovered via `glob.glob(.harness/*/features/*)` — never from
network/session input; the string it emits is the discovered segment + FEAT id, both filesystem
structure of this same repository. **Assessed and dismissed, on provenance not on the write
mechanism**: any actor able to name — or create — a feature directory in the first place already
reaches the same operator-facing channels (CI logs, session entry) through richer content it
controls directly, e.g. `BRIEF.md`'s own prose, which the same reader displays unfiltered. The label
path grants such an actor nothing they did not already have; it is not that string concatenation is
provably safe against control characters (it is not — `fpath()` does plain concatenation, no
escaping), it is that the discovered value is never lower-privilege than content already flowing
through the same sink. No attacker model in this diff has directory-creation privilege without
already having richer output channels.

**4. `.harness/expertise/harness-pm.md` edited inside `d033b9d`.** Content change is a single-line
path-string correction (`.harness/features/` -> `.harness/harness/features/` in a P-01 exemplar),
confirmed correct and non-behavioral by direct read. Widened the check per advisor review: filtered
the diff of all **18** injected/preloaded instruction files touched in this range (11 `SKILL.md`
files, 3 agent files, `harness.md`, `missions.md`, `build.yaml`, `review.yaml`, plus `harness-pm.md`)
— stripped every added/removed line of the path-rewrite substring and compared the remaining
add/remove multisets per file. **Zero residual mismatches across all 18 files**: every changed line
in every injected file is a pure path-string substitution, nothing else. This strengthens rather than
closes the open question: the unmitigated route (direct/branch commit touching injected content, no
technical gate) carried nothing non-path-shaped *this time*, across the full injected-content surface,
not just the one file the dispatch named.

The process question stands as a real gap and is raised below as an open question, not a ruling, per
dispatch: `d033b9d` is authored directly by the operator (`git show -s d033b9d` — `Author: Mike
Ruangutai`), not dispatched through the `SubagentStart`-hook-gated, distillation-only route
`harness-expertise`/DEC-145 describe as the *only* route Expertise files are meant to be written
through. That route is a documented convention enforced by agent-side skill instructions, not by
`check-domain.sh` or any technical gate — nothing stops a direct commit, or an in-band agent holding
Bash (`harness-dev-ops`, which "bypasses path checks entirely" per `team-config.yaml`'s own comment),
from writing arbitrary content to any `harness-*`'s injected Expertise or SKILL file. The compensating
control that caught this one is exactly what is happening now: pre-commit human/panel review of the
diff before merge (QA's precommit review independently flagged the same stale-path line,
`notes/review-harness-qa-2026-08-14-precommit.md:22`, citing the same content). No technical
lineage/integrity check (hash, required-approval-gate, distillation-marker) exists to catch a
*behavioral* edit riding the same route, only diff review.

**5. `branch-create-gate.sh:77-78` and `bash-write-guard.sh`.** `branch-create-gate.sh:77-78`
hardcodes the literal segment `harness` — this is exactly ADV-2, already ruled with a synthesized
remedy (`${REPO##*/}`, not a wildcard) in the FEAT-21 precommit security review; not re-filed here.
Swept the rest of the range (all touched `.sh`/`.py` source, excluding test fixtures and prose) for
the same CLASS — hardcoded repo-segment literal in enforcement logic — and found none:
`check-plan-routes.py`, `gh-sync.py` (depth-agnostic root walk-up to the `team-config.yaml` probe,
no fixed depth or literal), and `validate-feature-json.py` all use `*`/derived segments.
`bash-write-guard.sh` is **untouched in this range** — it delegates entirely to
`harness_boundary.py`/`team-config.yaml`, both covered above, and its own live fixture behavior
(ungranted write BLOCKED, in-domain write allowed, legacy-shape write BLOCKED, out-of-domain write
BLOCKED) was independently measured in the FEAT-21 precommit review and re-confirmed here by
`test-bash-write-guard.py` passing at the (source-identical) working tree.

## Not re-filed (already ruled, verified still true)

- ADV-2 (`branch-create-gate.sh:77-78` hardcoded segment) — confirmed present, unchanged severity
  (low, fails closed, DoS-shaped not escalation-shaped).
- Cross-segment reachability — confirmed no second segment is staged anywhere in this repo; the gap
  is real but untestable here and already recorded.
- The `check-state.sh` cross-repository feature-dict key collision (bare-basename keys) — confirmed
  present, confirmed it cannot fire with one repository, confirmed BRIEF scopes it out to unit 5/8.
- MF-1 (D-08 label clause) — confirmed fixed and now emits the segment-qualified path (item 3 above).

## Secrets sweep (P-14)

Full range diff swept for credential/token/key-shaped strings (`api[_-]?key|secret|password|token|
bearer|-----BEGIN|ghp_|AKIA`, etc.) beyond the five named files. No hits outside prose describing past
secrets sweeps (this feature's own prior review notes) and one unrelated test-fixture regex variable
named `TOKEN_RE`. Nothing new.

## Threat model

| Boundary | STRIDE | Mitigated |
|---|---|---|
| Agent write path -> `team-config.yaml` grant resolution (segment wildcard) | Elevation of privilege | Yes — matcher unchanged, segment-bounded, tests green |
| `check-domain.sh` shape-sweep / `SWEEP_GLOBS` | Tampering (silent budget-enforcement bypass) | Yes — anchor-correct, execution-tested |
| CI backstop (`check-plan-routes.py`, `validate-feature-json.py`) | Tampering (green-over-nothing) | Yes — segment-level walk tested, non-zero `examined` asserted |
| Branch creation -> work-tracking gate | Denial of service (legitimate work blocked, future multi-repo) | Partially — ADV-2, already ruled, not re-opened |
| Injected instruction content (Expertise, SKILL.md, agent files) via direct/branch commit | Tampering (unauthorized instruction injection) | No technical control — human diff review only; filtered-diff swept clean this time, open question below |

```yaml
VERDICT: PASS
DIGEST:
  headline: "Authorization surface moved coherently to the new layout with no widened or fail-open grant found across the range; the one hardcoded-segment gap (branch-create-gate.sh) is already ruled (ADV-2); a filtered diff of all 18 injected instruction files touched in this range shows pure path-string substitutions only, but no technical control would have caught a non-path edit riding the same direct-commit route."
  in_scope: true
  scope_reason: "Range rewrites the entire write-authorization surface — team-config.yaml grants, check-domain.sh shape regexes and SWEEP_GLOBS, check-state.sh discovery/label emission, check-plan-routes.py and validate-feature-json.py discovery, branch-create-gate.sh, .gitignore — plus edits injected-prompt content (11 SKILL.md, 3 agent files, harness.md, missions.md, two teams yaml, harness-pm.md Expertise) reaching every governed spawn. Authorization and prompt-injection integrity are this role's surface even though nothing here is user input in the OWASP sense."
  severity_max: info
  findings: 0
  must_fix: []
  threat_model:
    - { boundary: "agent write -> team-config.yaml grant resolution (segment wildcard)", stride: "E", mitigated: true }
    - { boundary: "check-domain.sh shape-sweep / SWEEP_GLOBS", stride: "T", mitigated: true }
    - { boundary: "CI backstop (check-plan-routes.py / validate-feature-json.py)", stride: "T", mitigated: true }
    - { boundary: "branch-create-gate.sh work-tracking gate", stride: "D", mitigated: false }
    - { boundary: "injected instruction content (Expertise/SKILL.md/agents) via direct/branch commit", stride: "T", mitigated: false }
  open_questions:
    - { id: Q1, question: "d033b9d edited .harness/expertise/harness-pm.md (injected into every harness-pm SubagentStart spawn) via a direct operator commit on a branch, not through the SubagentStart-hook-gated distillation route DEC-145/harness-expertise describe as the only legitimate write path — and the same commit touched 17 other injected/preloaded instruction files (SKILL.md x11, agent files x3, harness.md, missions.md, two teams yaml) the same way. A filtered diff of all 18 confirms every changed line this time is a pure path-string substitution, nothing else. But no technical control (hash pin, required distillation marker, diff-scoped gate) distinguishes that from a behavioral or exfiltration-shaped edit riding the same route — the only catch is human diff review, which is what caught the one content issue that existed (a stale path, via QA's precommit pass). Is a technical lineage control warranted for .harness/expertise/** and the preloaded SKILL/agent set, or is 'reviewed like any other diff' the accepted posture?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-security-reviewer-2026-08-14-panel.md
```
