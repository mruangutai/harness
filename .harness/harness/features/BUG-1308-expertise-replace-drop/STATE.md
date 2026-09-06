# STATE

## Current

- feature: BUG-1308-expertise-replace-drop
- run: .harness/harness/features/BUG-1308-expertise-replace-drop/runs/2026-09-05-review-panel-c4-validator/digest.md
- squad: validator
- status: in_review

SHIP-READY, pending the main-session-only GitHub steps. Validation is green: review panel cycle 4
PASS (severity_max `med`, no `must_fix`, VL-01 through VL-06 all closed), and the final goal-check
plus operator amendment grade fourteen of fourteen criteria met. Cycles used 9 of 9: the Advisor
authorized cycle 9 solely to repair seven feature-local artifact violations surfaced by the
post-BUG-1305 canonical checker; production code and tests were untouched.

Merged onto latest `origin/main` (`0f885a0a`, BUG-1305's ship state) at `cc16f721`, clean, no
conflicts. Both the rebase onto `4b0d04e9` and this merge were performed by the MAIN SESSION:
`git rebase` and `git merge` are in `bash-write-guard.sh`'s closed `HEAD_MOVERS` set and are refused
to every governed agent, this orchestrator included. Verified after the fact —
`git merge-base --is-ancestor 0f885a0a HEAD` exits 0.

DECISION NUMBER. This feature's decision is **DEC-219**, and it survived the merge unique and still
highest (`grep -c '^## DEC-219'` = 1, one index row, max entry 219). It was DEC-216, became DEC-218
when BUG-1303 landed 216 and 217, and moved again when BUG-1304 landed DEC-218. Each move was an
operator ruling, treated as a pure identifier substitution with the plan panel waived and both
signatures standing.

WHAT SHIPPED. `expertise-merge.py` gains a second subcommand, `ops`, carrying the distill contract's
op objects as JSON **from a file path** (`--ops <path>`, never inline JSON). Targets are keyed on
section plus entry id, both required; every op resolves against one base snapshot under the lock
`apply` already holds; each affected section is rebuilt in base order, so a proposal is
order-independent, a replace rewrites its entry without moving it, and caps are checked once on the
final state. `merge` stays an authoring concept. Refusals: 10 MISSING TARGET, 11 AMBIGUOUS TARGET,
12 MALFORMED OPS. Recorded as SPEC §5.3 and DEC-219.

WHAT THE PANEL COST, AND WHY IT EARNED IT. Three consecutive panels each found a high the suites did
not: VL-01 (a newline in an op entry injected a section header past the cap check, falsifying
REQ-03), then VL-05 (VL-01's ROOT CAUSE survived its own fix — the validator rejected two characters
where the parser's `str.splitlines()` breaks on ten), then VL-06 (`target` was never matched against
`ENTRY_RE`, so `add` could persist data the tool's own parser could not see, or plant a duplicate id
that locked that entry against every future replace and drop). Every one landed on a surface no
success criterion named, which is why twelve green criteria coexisted with a falsified requirement.

TRUST — measured by the orchestrator on the MERGED tree, not relayed:
- unit exit 0, 0 `^FAIL ` lines, 29 files (BUG-1305 added one). Integration exit 0, 0 FAIL, 46 files.
- Exploit probes, run directly against the tool: newline, U+2028, `\x0b` and `\x85` in an entry, and
  targets `PPPP-1` and `P-01: fake prefix`, ALL refuse at 12 with the file's sha256 byte-unchanged.
  Positive controls: `add P-09`, `replace P-01` and `drop G-01` each exit 0. The refusals cannot be
  passing by rejecting everything.
- T-04's own `verify:` block passes verbatim on the merged tree, `test-gen-decisions-index.py` exit 0.
- REQ-07 holds mechanically: `git diff origin/main -- expertise-merge.py | grep -c '^-[^-]'` is 0 —
  pure addition across every cycle, so the `apply` path is untouched.
- Board parent #1325 and sub-issues #1326-#1329 all read `review`.
- UNVERIFIED, inherited: the post-amendment re-signature. The main session reported SIGNED/APPLIED
  with no diff because the fields were already identical; this orchestrator can neither write nor
  re-run `sign-approval`.

DEAD ENDS, still active. Do NOT renumber the cycle-1 panel finding at `plan.yaml:248`, which reads
DEC-216 — its id is a hash over the reader plus that text and the operator ruled it stays as
transcribed history. Do NOT repair SPEC §5.3's APPLY-SIDE citations (`compute_union`, `cmd_apply`,
`CAPS`, the dead `acquire_lock` symbol); that drift predates this feature and is a backlog row, kept
out of this diff deliberately. Do NOT re-type `ENTRY_RE`'s grammar or `str.splitlines()`'s alphabet
anywhere — both checks are DERIVED from their source on purpose, and a hand-copied duplicate is
exactly the defect VL-05 and VL-06 were. Do NOT touch the `apply` path: REQ-07 forbids it.

WORKING SET. `BRIEF.md` · `plan.yaml` · `feature.json` ·
`runs/2026-09-05-review-panel-c4-validator/digest.md` ·
`notes/research-BUG-1308-expertise-replace-drop-goalcheck-sc-c4.md`.

## Open Questions

- **Harness process, observed THREE times in this feature.** A REQ-falsifying panel finding creates
  no criterion, so consecutive goal-checks re-grade the same SC list and stay blind to the same
  class. VL-01, VL-05 and VL-06 each landed on a surface no SC named. Should a REQ-falsifying panel
  finding be required to propose an SC alongside its fix?
- **Harness defect, confirmed live at this HEAD (re-measured, not inherited).** `notes/handoff-*.md`
  cannot be written for a feature whose directory exists only in a worktree. `handoff_done_when.py`
  resolves `feature_dir` against the PROJECT ROOT, and the main checkout has no
  `.harness/harness/features/BUG-1308-.../`, so `brief-sc:` and `plan-task:` are both unresolvable;
  `finding:` requires `F-\d+`/`PF-\d+` while this repo mints hex ids; `approval:` resolves but both
  approvals read `approved`, so it binds nothing and is correctly refused. An attempted write of
  `handoff-build.md` citing `brief-sc:SC-10` was BLOCKED with exactly that message. BUG-1304 did not
  fix it. Suggested fix: resolve `plan-task:`/`brief-sc:` against the feature-tree root per DEC-214's
  two-anchor rule, and widen `FINDING_RE` to the hex ids `panel_findings.py` mints. This section is
  the documented disk-only successor path and carries the handoff content.
- Harness defect: the unit runner's discovery count is caller-dependent — 28, 29 and 74 files were
  reported from the same command by different callers, and it false-fails `test-plan-merge.py`
  unless invoked as `env -u HARNESS_AGENT_TYPE`. A zero FAIL count therefore does not bound what ran.
- Informational, `max_total_runs`: `runs[]` stands at 31 against a budget of 20. INV-22 emits a NOTE
  and never stops a branch. The runs earn their place: the overrun is three adversarial panel cycles
  that each caught a high the suites could not, plus their fixes — not churn. Every run returned a
  verdict and advanced the feature.
