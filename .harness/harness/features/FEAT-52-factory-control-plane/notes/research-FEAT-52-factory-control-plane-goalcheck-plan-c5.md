# Goal-check — FEAT-52 REPAIRED plan (15 tasks) vs the operator's stated intent — cycle 5

**Yes, with two named residuals.** Every clause of the grilling note is now carried by a task or a
decision, including the one c0 graded `partial` (settled item 3's spawn-time half, now D-07 + T-03
step 5 + SC-12) and the one the HIGH panel finding opened (direction enforcement, now T-02's THIRD
violation class + the new T-15). Neither residual is a dropped clause: one is the #356 headline
symptom never re-measured end to end, one is a single-spelling scan. Graded against the 15-task
plan — `len(tasks) 15`, `T-01..T-15`, `'approval' in doc: False`, `status: plan`.

## The grilling, clause by clause

| Clause (grilling note) | Carried by |
|---|---|
| Destination: worker in a product checkout uses the control plane without reading/writing the wrong repo | D-01, D-06; T-03 (read anchor injected), T-01 + T-09 (write anchor resolved/refused) |
| Worker LOCATES the control plane: Harness injects the absolute root into the preamble | D-01, D-02, T-03 steps 1-2; SC-01 (asserts injected root ≠ cwd) |
| Worker MAY READ Harness skills through that root, read-only | D-05, T-05 (anchor + explicit read-through), T-08; SC-06 both directions |
| Product writes remain constrained by the EXISTING grants | D-05, T-05 step 2 (no `team-config.yaml` grant), T-08 ("write grants unchanged, still resolved by check-domain.sh"); SC-07 |
| Drift prevented by a STATIC LINT over factory-reachable instructions | T-02 (scope + inline **and** fenced rule), T-12 (required `integration` step, proven red), **T-15** (whole-scope run at the reviewed sha, which T-12's working-tree run cannot discharge) |
| …AND by a SPAWN-TIME assertion | D-07, T-03 step 5 — `HARNESS_PATH_DRIFT`, exit 0 on every branch; SC-12. This is what c0 graded `partial`; it now asserts the PATH CONTRACT, not merely that a root resolved |
| "Narrowest provider-neutral implementation" | The injected placeholders `<HARNESS_CONTROL_PLANE_ROOT>` / `<HARNESS_FEATURE_TREE_ROOT>` are text, and the carrier (`inject-expertise.sh`, `SubagentStart`) is registered for both runtimes by `merge-settings.py:46-48` and exercised by `omp-hooks.test.ts:148`. No new mechanism |
| Out of scope: kaya-ai product code | Respected — no task names a product path (grep of all 15 intents: `kaya` 0, `496` 0) |
| Out of scope: widening product-checkout write permissions | D-05, SC-07, T-05 step 2 |
| Fact: `CLAUDE_PROJECT_DIR` unusable inside an agent shell → needs an agent-visible path | Honoured: the value arrives as injected TEXT (D-01), and the write anchor is resolved by a script that reads its own directory (T-01), never the environment |

**Issue #356's four planning items** (comment 4): (1) one resolved root readable by an agent — T-03;
(2) anchor the four families — T-04, T-05, T-06, T-07, with per-site pinned-tree proof in **T-15**;
(3) a check, because "without a check this class returns" — T-02 + T-12 + T-15; (4) the fifth family
needs a different answer — T-05, anchor PLUS stated read-through. All four land.

**What the repair added, and why it matters to intent.** T-02's third class (`VIOLATION <path>:<lineno>:
control-plane path anchored to the feature tree`) and its second class now read ONE named predicate,
`^\.harness/([^/]+/)?features/`, from opposite sides, so exactly one anchor is legal for any matched
token — chosen from the path's shape, never a hand-list. Without it the panel's case
(`<HARNESS_FEATURE_TREE_ROOT>/.harness/harness.json` in `harness-qa-gate/SKILL.md`) satisfied the rule
and resolved the qa matrix against the wrong checkout — the exact "reading the wrong repository" the
destination clause forbids. T-15 then proves each of the five canonical sites individually at
`git show <ref>:<path>`, with a per-row red proof; the pre-repair plan had only bare placeholder greps.

## Residuals — named, not fixed

- **R1 — #356's HEADLINE symptom is never re-measured.** The ticket is "a factory worker cannot WRITE
  its receipt or observation, in any product." The plan makes the path absolute and correct; no task
  and no SC fires `harness_boundary.classify` / `check-domain.sh` on that absolute path with the
  agent standing in a product base (grep of all 15 intents: `classify` 0, `check-domain` only T-08,
  as prose). Read directly, `harness_boundary.py:451` selects the base by `inside(abs_target, base)`
  — target-side — so the anchored write SHOULD be allowed, and the grants are already segmented
  (`.harness/*/features/*/notes/receipt-<agent>-*.md`, `team-config.yaml:185`). But "should" from a
  code read is the same inference #356 comment 4 refused to ship on. *Would carry it:* one
  `test-check-domain.py` case asserting `allow` for the absolute receipt path from a product-shaped
  base.
- **R2 — the spawn-time assertion is single-spelling.** T-03 step 5 scans
  `<root>/.omp/agents/<agent_type>.md`; both `.claude/agents/` and `.omp/agents/` carry 16 files, and
  a Claude-runtime spawn's real definition is the `.claude` twin. Drift between them is invisible at
  spawn, though T-02's scope and T-15's pinned whole-scope run catch it in CI. Matches SC-12 as
  written, so it is an intent-level narrowing, not an unmet criterion. *Would carry it:* scan both
  spellings when both exist.

## Open for the operator

- The `approval:` mapping is still absent — the known, separate, unruled blocker. Not created here.
- The seven non-HIGH panel findings remain `open` by instruction; not re-litigated in this note.
- Repair-note Q1 stands: the shared predicate widened class 2 to the unsegmented `.harness/features/`
  spelling (a strengthening; 11 template spans stay legal). Nothing in the grilling contradicts it.
