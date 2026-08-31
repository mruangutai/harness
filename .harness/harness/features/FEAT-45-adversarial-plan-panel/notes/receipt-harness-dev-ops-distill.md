# FEAT-45 distillation receipt — harness-dev-ops

## BLUF

Applied one craft Gotcha (G-17, severity-gate fail-open via deny-list normalization) and three
repository Gotchas (G-08 hardcoded team count, G-09 `check-domain.sh --resolve` in symlink-mirrored
roots, G-10 post-merge KIND-DRIFT). Rejected two of the three relayed candidates (C2 as literally
stated, C3 for tooling reasons) with reasons below. Ruled on the standing G-03 advisory: **kept
craft, not moved.** Both files applied via `expertise-merge.py apply`, exit 0, no conflicts, no
cap breaches. Nothing else touched; no commit made.

## Section counts

| Tier | Section | Before | After |
|---|---|---|---|
| craft | Patterns | 15/15 | 15/15 (unchanged) |
| craft | Gotchas | 14/15 | 15/15 (+G-17) |
| craft | Outcomes | 0/10 | 0/10 |
| craft | Open | 0/5 | 0/5 |
| repo | Patterns | 1/15 | 1/15 (unchanged) |
| repo | Gotchas | 6/15 | 9/15 (+G-08, +G-09, +G-10) |
| repo | Outcomes | 0/10 | 0/10 |
| repo | Open | 0/5 | 0/5 |

Craft file: 34 → 35 lines (150-line budget). Repository file: 12 → 15 lines (40-line budget).

## Ops applied (verbatim)

```yaml
expertise_update:
  - op: add
    section: Gotchas
    file: .harness/expertise/harness-dev-ops.md
    entry: "G-17: WHEN a gate normalizes an absent or null field before testing membership in a deny-list DO check where the normalized value lands — it typically falls outside the deny set, so missing data passes silently. Prefer an allow-list of the few known-safe values instead, so absence fails closed by construction."
    why: "code-reviewer c0 Finding 1 (must_fix/high): INV-32's severity default `.get(\"severity\", \"\").strip().lower()` landed an absent/null field outside the {high,critical,unrated} deny-set and sailed through un-gated, contradicting DEC-206. Fix (c1, independently corroborated CLOSED) inverted to an allow-list of the three known-safe values. General shape, not this-repo-specific."
  - op: add
    section: Gotchas
    file: .harness/harness/expertise/harness-dev-ops.md
    entry: "G-08: WHEN adding a new team YAML file under `.claude/skills/harness/teams/` DO also bump `TEAMS_EXPECTED` in `test-harness-yaml-corpus.py` by hand, with a comment recording the new count's justification — it is a hardcoded literal, not derived from a directory listing, and stays wrong (loud SC-05 failure) until corrected."
    why: "T-12 receipt: plan-panel.yaml (T-02's product) became the repo's third team file; TEAMS_EXPECTED=2 was stale and had to be bumped to 3 with a D-15 comment block explaining why it wasn't drift. Turns on this repo's specific corpus test and directory."
  - op: add
    section: Gotchas
    file: .harness/harness/expertise/harness-dev-ops.md
    entry: "G-09: WHEN a RED proof needs a symlink-mirrored `/tmp` root because the domain guard denies an in-place mutation DO expect `check-domain.sh --resolve` to fail resolving paths inside it (its harness/git-worktree detection) — run an unmutated control there first and count only mutant-minus-control as a real, mutation-caused failure."
    why: "sc03supersession receipt: 4 of 28 checks reddened in the unmutated control inside a symlink-mirrored /tmp root, all `check-domain.sh --resolve` calls returning NOBODY — an artifact of that repo tool's own worktree detection, not the mutation. Only mutant-minus-control isolated the two real reds."
  - op: add
    section: Gotchas
    file: .harness/harness/expertise/harness-dev-ops.md
    entry: "G-10: WHEN `run-unit-tests.sh`'s `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` arrays are touched by a merge from `main` DO run `--check-kinds` (or `--kind unit`) immediately after — a merge can resurrect a registration for a file `main` already deleted, which the KIND-DRIFT detector rejects with exit 2 before any test collects, even though every script still passes standalone."
    why: "f4-gate-revival receipt fixed three dangling registrations (test-context-watch*.py) that main had deleted but this branch's merge reintroduced; qa-c2 independently caught the same break live as a BLOCKED matrix (exit 2, 2x KIND-DRIFT, zero tests collected). Names this repo's specific runner and drift mechanism."
```

Applied with:
```
python3 .agents/skills/harness/bin/expertise-merge.py apply --file .harness/expertise/harness-dev-ops.md --entries <scratch>
python3 .agents/skills/harness/bin/expertise-merge.py apply --file .harness/harness/expertise/harness-dev-ops.md --entries <scratch>
```
Both exit 0. Craft: `ADDED G-17`, all 15 Patterns + 14 prior Gotchas `PRESERVED`. Repo: `ADDED G-08,
G-09, G-10`, `PRESERVED` P-01, G-01, G-02, G-04, G-05, G-06, G-07 (all unchanged).

## Relayed candidates — judged

**C1 — ACCEPTED (as G-17 above).** Verified directly against `review-harness-code-reviewer-c0.md`
Finding 1 (`must_fix`/`high`) and its `c1` corroborated-CLOSED fix. The candidate's description
matches the receipts exactly: `str(item.get("severity", "")).strip().lower()` normalizes both an
absent key and a YAML `null` to values (`""`, `"none"`) outside `{"high","critical","unrated"}`,
so the deny-list gate failed open on exactly DEC-206's named risk. Genuinely general — any
risk-classification gate using a deny-list default can have this shape. Not stale at HEAD.

**C2 — REJECTED as literally stated; distilled instead as G-08's sibling G-10, corrected.** The
candidate claims "the runner exited BEFORE collecting anything — exit 0, zero `^FAIL ` lines, and
zero tests actually run." That is not what happened: `review-harness-qa-c2.md` measured the actual
failure live — `run-unit-tests.sh --kind unit` (and `--kind integration`, and `--check-kinds`)
**exits 2**, printing two `KIND-DRIFT:` lines, before any test collection — a loud, blocking
failure, not a silent exit-0 pass. My own `f4-gate-revival` receipt fixed the same three dangling
registrations but never itself characterized the pre-fix exit code; the "exit 0, zero FAIL" framing
in the relayed candidate does not match the measured ground truth in either receipt. I distilled
the corrected, verified version as repository G-10 (this repo's specific KIND-DRIFT mechanism) —
the durable lesson ("verify the canonical aggregator after a merge, not just the constituent
scripts") survives, but with the true failure mode.

**C3 — REJECTED for this dispatch, tooling reason stated as an open question, not an Expertise
entry.** The mutant-vs-control isolation technique in `sc03supersession`'s receipt is real and
would extend craft `P-17` (which currently only requires "every other case stays green," an
assumption C3 shows can be violated by the proof *environment* itself). Craft Patterns is at cap
(15/15). `expertise-merge.py apply` has no working `replace` or `drop` path: `compute_union` is
purely additive — same id + different text is a hard conflict (exit 7, "resolve it yourself"), and
there is no delete operation anywhere in the tool. I could not safely displace a weaker Pattern
entry within this dispatch without corrupting the union or fabricating a workaround the tool
doesn't support. Flagged below as a genuine harness-tooling gap (op:`replace`/`drop` are documented
in `harness-distill` but not implemented), not folded into Expertise as a workaround.

## G-03 advisory ruling

Read `.harness/expertise/harness-dev-ops.md:20` (pre-edit) — "avoid `declare -A`... this machine's
default bash is 3.2.57... See the drift-detector's nested-loop membership check in
`.claude/skills/harness/bin/run-unit-tests.sh` for the working pattern." **Ruling: kept craft, not
moved.** The load-bearing fact (`declare -A` errors on macOS's stock bash 3.2.57) is true of any
machine with that shell, not particular to this repository; the cited file is a pointer to a working
exemplar (explicitly permitted by the distill skill), not the thing the rule turns on. No edit made.

## Not applied / no room

Two self-derived candidates considered and dropped without using a slot, in favor of the four ops
above: (a) T-09's mutant M1 reddening a second, unpredicted-but-genuine check (`case5b`) alongside
its target — already generalized by existing craft P-17's discrimination discipline, not distinct
enough to earn scarce Gotcha room over C1; (b) the `arch-eng` receipt's Q1-Q4 architecture findings
— decision-input material for the operator/pm, not a durable dev-ops workflow rule, so out of scope
for Expertise by the decision-vs-observation boundary in `harness-expertise`.

## Open question for the harness owner (not an Expertise entry)

`expertise-merge.py`'s `apply` subcommand implements only additive union-merge with conflict
detection on divergent same-id text (exit 7) and a cap check (exit 8); it has no `replace` or
`drop` mechanism, despite `harness-distill`'s documented ops schema listing `replace`/`drop` as
legitimate op types. A distiller who needs to update or displace an existing entry in a
capped section has no tool-supported path today. Not filed as a bug ticket by me — surfacing it
here per the report_issue / open_questions convention.

## expertise_update / files_touched (for DIGEST)

files_touched:
- .harness/expertise/harness-dev-ops.md
- .harness/harness/expertise/harness-dev-ops.md
