# UI Review — BUG-1071 inv32-era-guard

## Census (measured)

- `DESIGN.md`: **absent**. `.harness/harness/features/BUG-1071-inv32-era-guard/` contains
  `feature.json`, `feature.json.lock`, `notes/` (`handoff-build.md`, `handoff-plan.md`),
  `review_sha`. No design contract exists for this bug, consistent with it being a gate-script
  fix rather than a UI feature.
- Rendered-surface file count in the diff: **0**. The diff touches exactly two files,
  `.claude/skills/harness/bin/check-state.sh` and `.claude/skills/harness/bin/test-check-state.py`
  — a shell/Python gate script and its Python test suite. No `.html`, `.css`, `.scss`, `.tsx`,
  `.jsx`, `.vue`, `.svelte`, `.less`, template, or markup file appears anywhere in the 139-line
  diff (`git diff --stat 75daa3bb bf12a96b`).
- Operator-facing output: the diff adds two new `warn.append(...)` calls inside the INV-32 era
  guard (`check-state.sh` lines ~198-214), each printed at runtime with the `note` label (per
  `check-state.sh:1906`, `for m in warn: print(f"  note       {m}")` — the internal list is named
  `warn` but the printed category is `note`, matching the file's existing non-blocking-item
  convention, e.g. INV-17's exemption note and INV-22's budget note use the same label).

## Remit judgment

Terminal `note`/`warn` text emitted by a repo-wide gate script IS in remit here. Two independent
signals converge on this: (1) the dispatch names it explicitly as the candidate surface to judge,
and (2) this checkout's own project-tier Expertise (P-06, repo-tier P-01) already states that
adjacent CLI/hook-emitted text is the scope this role reduces to on a no-rendered-UI diff in this
repository. Declining review of these two strings on the ground that they are "not UI" would
contradict Expertise this role wrote for itself.

Reviewed **only** the two new strings, per the assignment's confinement. Did not touch era logic,
the 2026-08-31 boundary, or the four new test cases — those are other reviewers' ground.

## Findings

**F1 — low, non-gating.** The undated/malformed-date note names the defect but not the remedy.
Text (verified live on the real tree):

> `INV-32: FEAT-40-harness-writes-done is approved but approval.date is missing or malformed (''), so its panel era cannot be placed; not graded. The undated signature is the defect to fix.`

It tells the operator *what* happened and *that* it's the thing to fix, but not *how*: no field
path, no expected format. Every other actionable `note` in this same file names a concrete
remedy — INV-28: `"Record it with \`gh-sync.py record-pr ...\`"`; INV-21: `"Re-run \`open\` to
record it."`; INV-22: `"Set it in .harness/harness.json (default 20)."` This is the established
house convention this role's Expertise (G-13) exists to check for, and the new note falls short
of it: an operator reading it must independently discover that the fix is adding an
`approval.date: YYYY-MM-DD` key to the plan's `approval:` block in `plan.yaml` — a fact stated
only in the surrounding code comments, never in the message itself. Concrete scenario: an operator
scanning 32 `check-state.sh` notes at once sees this one, wants to close it, and has nothing in
the string itself to act on. Non-blocking because `check-state.sh` exits 0 regardless (verified:
`exit=0` with this note present) — this is a clarity gap, not a functional one.

**F2 — no finding.** The pre-era note is fine as written:

> `INV-32: FEAT-45-adversarial-plan-panel was signed 2026-08-30, before the adversarial panel shipped (2026-08-31); not graded. A plan signed before the panel existed cannot carry a record of it.`

It requires no operator action (the plan is legitimately exempt), and purely-explanatory notes
with no remedy are the house convention for exemptions too (INV-17's `"exempt from handoff
notes — {reason}. Suppressed ..."` carries no action item either). Consistent, no gap.

**Info — volume, not this diff's defect.** Verified live: 32 `INV-32:` lines print in one run (31
pre-era + 1 undated), in `plan_docs.items()` iteration order (not alphabetical, not
severity-grouped — sampled order: FEAT-45, FEAT-32, FEAT-27, FEAT-37, FEAT-38, FEAT-43, FEAT-31,
FEAT-12, ...). This is a real scan-cost concern the dispatch flagged as "anyone's" — but it is not
new: every other multi-hit `note`/`bad` category in this script (INV-22 run-budget notes, INV-23
line-budget notes) already prints in the same unsorted per-feature order, so this diff did not
introduce the ordering behavior and fixing it here would be scope creep onto a pre-existing,
file-wide presentation pattern. Recorded as advisory only.

## Verdict rationale

No `must_fix`. F1 is a real, concrete-scenario clarity gap but caps at `low`: it doesn't block,
mislead about severity (the `note` label already signals non-fatal), or misstate a fact — it just
omits a remedy step other sibling messages include. `severity_max: low` → PASS.

## Open question

None blocking. Whether to tighten F1's wording to name the field and format is a cheap, reversible
copy edit — not escalating it, noting it as a take-it-or-leave-it improvement for whoever next
touches this block.
