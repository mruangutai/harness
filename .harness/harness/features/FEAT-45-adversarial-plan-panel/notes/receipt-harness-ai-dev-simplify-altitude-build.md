# Altitude review (build-side) — FEAT-45-adversarial-plan-panel

Angle: ALTITUDE, read-only. Scope: `git diff 1d3e5db..HEAD` in the FEAT-45 worktree (40 files,
+3108/-135). No worktree file was written.

BLUF: one real altitude finding — the validator lead's plan-panel transcription contract
(dedup / severity_max / "pm assigns PF- ids, never the lead" / unrated-gating / skip-recording)
is stated in full at its one authoritative home (`.omp/agents/harness-validator-lead.md`,
"Hosting plan-panel") and then restated in `plan-panel.yaml`'s closing comment, with no test
cross-checking the two. This is a re-flag, not a new discovery: the plan-phase simplify pass
already caught it (`notes/receipt-harness-ai-dev-simplify-altitude.md` in this diff, section
"3 & 5") and correctly returned it FLAG-ONLY because both files resolve to NOBODY — the
apply never happened, and it is still open in the shipped code today. Everything else audited
sits at the right depth. `fold-in` (backlog row; not appliable this run).

## What I examined

- `panel_findings.py` (61 lines, whole file) and its three intended consumers: the INV-32
  branch in `check-state.sh` (lines 174-238), `.omp/agents/harness-validator-lead.md` +
  `.claude/agents/harness-validator-lead.md` ("Hosting plan-panel" sections, identical text),
  and the pm/plan doctrine (`harness-spec-driven/SKILL.md` "The panel result",
  `templates/plan.yaml` `panel:`/`approval:` comments, `plan-panel.yaml`'s own closing
  comment).
- All three team files in `.claude/skills/harness/teams/` (`build.yaml`, `review.yaml`,
  `plan-panel.yaml`) for shape parity, plus `harness/SKILL.md`'s "validator segment" and
  `harness-plan.md`'s orchestrator line for how `plan-panel` is resolved/invoked.
- `sync-agent-adapters.py`'s diff (the `fable-advisor` SPAWNS entry + its own comment
  explaining it is inert today, reachable only via `--bootstrap-from-claude`).
- `test-check-state.py`, `test-panel-findings.py`, `test-plan-panel.py`,
  `test-harness-yaml-corpus.py` for whether any of them hardcode the hash algorithm or
  cross-check the duplicated comment content.
- `DECISIONS.md`'s two new entries (DEC-206, DEC-207) and `BRIEF.md`'s "Verification gaps"
  section for the residual/compensating-control question.

## 1. Capability at the right home — clean

`panel_findings.py` is genuinely the one place the hash is computed. Every consumer that
needs the VALUE calls the CLI or imports the module rather than re-deriving it:
`harness-spec-driven/SKILL.md:110` and `plan-panel.yaml:58` both say "pm computes identity
… with `panel_findings.py`," never restate the algorithm; `test-panel-findings.py` imports
`finding_id` and asserts behaviour (reword-insensitive, content-sensitive, reader-sensitive,
length 11), never a literal hash value.

The one consumer that does NOT call the module — `check-state.sh`'s INV-32 — legitimately
doesn't need to: it only ever treats `id` as an opaque string (set membership for
overrule-matching, presence for "malformed"), never re-derives or format-validates it with a
regex. That is the "validates shape, doesn't need the module" case the dispatch called out as
possibly fine on its own merits, and here it is fine: nothing in INV-32 could disagree with
`panel_findings.py` about what an id IS, because INV-32 never computes one.

## 2. One authoritative statement of a rule — one real gap

Traced the five rules (when the panel runs, what a reader returns, override record format,
finding-id format, stale-override condition) across `harness/SKILL.md`, `harness-plan.md`,
`harness-spec-driven/SKILL.md`, `templates/plan.yaml`, `plan-panel.yaml`, and both
`harness-validator-lead.md` copies. Four of five have a clean single authority with callers
that only reference it. The fifth does not:

**`.omp/agents/harness-validator-lead.md:97-119` ("Hosting plan-panel") is the one place
that actually governs the lead's live behaviour — it is what gets loaded at every spawn.
`plan-panel.yaml:54-62`'s closing comment restates the SAME specific mechanics**, not the
generic recap `review.yaml`'s own closing-comment convention uses (merge/dedupe/
severity_max/trace — true of every panel, not FEAT-45-specific): both say the lead never
assigns unrated a severity, both say the lead does not assign the PF- id ("pm computes
identity" / "pm computes it once with `panel_findings.py`"), both describe the skip-record
obligation in near-identical wording ("status skipped" + persona + reason; never report a
skipped reader as having run and found nothing).

Cost: nothing detects drift here. `test-plan-panel.py` checks the team file's structure
(readers, `on_fail`, personas, spawn allowlist, roster census) and separately checks the
Target-state bullet in `harness-plan.md` names `plan-panel` — it never diffs or cross-checks
`plan-panel.yaml`'s closing-comment prose against `harness-validator-lead.md`'s prose. If a
later feature revises the lead's transcription mechanics (e.g. changes what "unrated" gates
against, or moves id assignment), `.omp/agents/harness-validator-lead.md` — the loaded,
authoritative copy — updates, and `plan-panel.yaml`'s comment has no reason to follow and no
test to catch that it didn't. The team-file copy becomes decorative-at-best,
misleading-at-worst.

This is not a new finding: the plan-phase altitude pass already found it (this diff's own
`notes/receipt-harness-ai-dev-simplify-altitude.md`, "3 & 5. One rule, two homes") and
recommended trimming `plan-panel.yaml`'s comment to the `review.yaml`-style generic recap,
dropping the FEAT-45-specific mechanics. That recommendation was correctly returned
FLAG-ONLY (`plan-panel.yaml` and `harness-validator-lead.md` both resolve to NOBODY per
`check-domain.sh` — confirmed again for this pass) and was never applied, which is why the
duplication is still present in the code I'm reading now. Re-raising it here because it is
an accepted residual with no compensating control named anywhere in the diff (no test, no
comment pointing at the authority) — it should be a visible backlog row, not silently
dropped a second time.

**fold-in** (backlog row — `appliable: false`, both files resolve to NOBODY). Concrete
alternative unchanged from the earlier pass: trim `plan-panel.yaml:54-62` to the generic
recap only (merge, dedupe, `severity_max`, trace, assessed-and-dismissed) and a one-line
pointer to `.omp/agents/harness-validator-lead.md` as the mechanics' one authoritative home;
drop the FEAT-45-specific detail (unrated-as-high, PF- id ownership) from the team-file
comment entirely.

One place this pattern is legitimate and I am NOT flagging it: `check-state.sh:202-204`'s
`STALE OVERRIDE` message and `templates/plan.yaml:34-37`'s comment both restate the same
"reworded finding → new content-hash id → old ruling stops applying" rationale that
`panel_findings.py`'s own module docstring states. Unlike the case above, neither of these
computes anything — one is a human-facing runtime error string, the other is prose guiding a
human filling out a template — and a self-contained error message can't just say "see the
docstring." `test-check-state.py` (lines 3005-3007) already pins the wording it depends on
(`"reworded"`, `"asked again"`), so drift there is caught. Examined and left as-is.

## 3. The third team file — right level, not bolted on

`plan-panel.yaml` has the identical top-level shape to `build.yaml`/`review.yaml` (`name`,
`purpose`, `lead`, `inputs`, `steps`), and `harness/SKILL.md:97-98` resolves it exactly the
way `harness/SKILL.md:120-121` resolves `build.yaml` — project override first, shipped
default second, via `harness-team`'s standard resolution, not a special-cased path.
`test-harness-yaml-corpus.py:160-165` names the directory's expected file count as three and
cites D-15 as the ruling that makes the third file legitimate, rather than hand-waving it —
that is the drift detector doing its job, not a special case. No finding.

## 4. Accepted residuals — compensating controls

The one BRIEF-level residual (`## Verification gaps`: no runner grades panel finding
QUALITY) names its compensating control explicitly — SC-11 (operator, by eye) plus the
single hand-run against FEAT-38, n=1 — so it is accepted correctly, with the control stated,
not silently. `BRIEF.md` is out of scope for a proposed edit here regardless (settled/signed
plan surface); noting it as correctly handled, not a finding.

DEC-206's residual (the wrapped reader's return is structurally unvalidated by
`validate-digest.py`) also names its compensating control inline — self-emitted severity,
`unrated` fails closed to high, transcription-not-invention by the lead — and that control is
itself enforced by `INV-32`'s `unrated`-gating check. Accepted correctly.

The one residual accepted WITHOUT a named compensating control is §2 above (the closing-
comment echo) — folded into that finding rather than listed separately, since it is the same
underlying gap.

## 5. Deeper fix vs. reopening scope

The deeper fix for §2 (trim the comment, point at the authority) does not reopen any signed
requirement or task — it is a same-shape edit to a comment block, matching the pattern
`review.yaml` already uses. It only cannot land THIS run because both touched files resolve
to NOBODY under the current domain grant; that is a grant-routing fact, not a reason to widen
the fix into something that would reopen scope. No case in this diff required recommending
`leave` on the grounds that only a scope-reopening fix exists.

## Verdict

One finding, `fold-in`/backlog, `appliable: false`. Everything else examined sits at the
right altitude.
