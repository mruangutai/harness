# Review application — FEAT-50 plan fix cycle, 2026-08-31

**All six gating findings applied, F2 before L1, plus F3. F1 applied, F4 applied.** The plan now
carries 8 tasks (T-08 is new), 8 decisions, 7 REQ and 15 SC (SC-15 is new). `harness_yaml.load_plan`
loads it; `check-plan-routes.py` exits 0 with `0 violation(s) across 1 plan(s)` and the same five
expected DEC-174 DEVIATION lines. Max budgeted-field count is **45** (T-03), against a cap of 50.
`approval.status` is `pending`, `approval.rulings` is present and empty, there is no `panel:` key.

## Counts after the edit

| | before | after |
|---|---|---|
| REQ | 7 | 7 |
| SC | 14 | 15 |
| tasks | 7 | 8 |
| decisions | 8 | 8 |
| lanes rows | 9 | 12 |

## Per-finding disposition

| id | disposition |
|---|---|
| F2 | **applied first**, before any L1 edit. REQ-03 narrowed to the MAIN checkout; T-03's intent drops the sibling-worktree denial and now says the rel it reads is raw; T-03's "resolves inside it" bullet says the branch is skipped, not taken; T-05 case 2's stated purpose corrected to DEC-143's stripped match |
| L1 | applied, after F2. (1) T-04 step 3 carries the validator's **verbatim** replacement wording and threads an absolute-target parameter through `shape_problems`; the `root + rel` premise sentence is deleted. (2) T-05 cases 5 and 7 must build the fixture digest inside a registered worktree via case 1's helper, and SC-05 names that clause |
| ENG-A | applied. D-03 re-specified: prefix selection, refuse on ambiguity, containment by `checkout_relative` identity and never `realpath.startswith`. New **T-08** (`team`, `harness-backend-dev`) lands `harness_boundary.worktree_for_feature` + `AmbiguousWorktree` and cuts `inflight_registry.feature_root` over. T-03 `depends_on: [T-08]`, stays `main-session-direct`, and says in its own intent that the cutover is layer 0 under DEC-174 while the library is not. Three lanes rows added |
| ENG-B | applied, **exit (i)** |
| ENG-C | applied. REQ-01 replaced with the eng digest's **verbatim** weaker wording; a `## Verification gaps` row now records the `stop_hook_active` bound. D-01's exit-2 direction untouched; the passthrough itself untouched |
| ENG-D | applied. T-03 and T-04 each gained an executable behavioural `verify:`; both spelling-pinned greps dropped. T-01's `not validated` literal **kept** |
| F3 | applied. The ui-reviewer's **verbatim** recording instruction appended to the open-ruling section, plus one clarifier naming `plan.yaml` as the file that carries `approval:`; `rulings: []` added to that block |
| F1 | applied, **verbatim**. Raised a conflict the finding did not see — see Open questions |
| F4 | applied, **verbatim** replacement first sentence |

### Simplification / efficiency angle

| id | disposition |
|---|---|
| EFF-01 | applied, **verbatim** figures, into D-03's `because` |
| EFF-02 | applied, remedy **(a)** in its strongest form: `RE_RUN_DIGEST` is now specified NOT to go into `SHAPE_PATTERNS`. `has_shape_rules` gates only the POST named-target route (`check-domain.sh:1377`); the PRE route builds its target unconditionally (`:1367-1370`). Omitting the pattern therefore costs the PRE route nothing and removes the extra read entirely, rather than documenting it |
| SIMP-05 / ENG-F | applied. D-08 no longer pins a number; T-07 resolves it against `DECISIONS.md` at execution and asserts uniqueness; T-07's verify and SC-14 anchor on the heading text |
| SIMP-06 / ENG-G | applied. SC-11's exact-count leg dropped; the count is now a dated measurement, not graded. A positive control was added so an errored `check-state.sh` cannot pass as clean |
| SIMP-04 / SIMP-07 | applied as part of ENG-D (both greps dropped) |
| SIMP-01 / ENG-H | **rejected.** T-01's inline exit-code checks are the only behavioural proof at T-01's landing moment — T-02 does not exist yet. Removing them moves T-01 in exactly the direction ENG-D (gating, higher severity) condemns. Duplication between a one-shot landing gate and the permanent suite that supersedes it one task later is not drift that can hurt |
| SIMP-02 / ENG-J | **rejected.** `intent:` is the literal dispatch prompt and the doer receives nothing else about the task. Replacing the mutant checklist with "per D-07's idiom" would send the doer a citation it cannot resolve |
| SIMP-03 / ENG-K | **rejected.** The three intents already state the FACT the comment must carry, not its phrasing; they name measurements, which is this file's own comment convention (`check-domain.sh:952-955`, `:1083-1087`). There is no exact wording to drop |
| EFF-03 / EFF-04 / ENG-L | **rejected for this cycle.** Grading-time redundancy in `command:` lines, no correctness consequence, and collapsing five criteria onto one shared evidence note weakens P-04 (each criterion asserting for itself). Noted, not applied |
| ENG-E | **not mine.** Declined by the lead; L1's re-specification of T-05 cases 5 and 7 is the T-05 change in scope |

## What I added beyond the findings, and why

- **SC-15** grades T-08's seam (prefix selection, the `FEAT-XY`/`FEAT-X` boundary, ambiguity
  refusal, the `inflight_registry` fallback). Without it the correction ENG-A forced would ship
  ungraded. `evidence: unit` — `test-harness-boundary.py` is in `UNIT_SCRIPTS`, not
  `INTEGRATION_SCRIPTS`.
- **SC-03 fourth clause and T-05 case 1's second assertion**: the short-form worktree. Every
  existing clause stays green under an equality-matching implementation, so without this the
  criterion cannot fail for ENG-A's reason.
- **T-05's PRE-only assertions** in case 2, binding T-04 steps 1 and 2 behaviourally.

## Evidence — the new verifies were run, not assumed

Against the **pre-change** tree, so each is proven red for the right reason:

- T-03's verify: control (no worktree registered) exits 0 with empty stderr — the fixture and its
  manifest grant are well-formed; the bound case also exits 0, so `bound.returncode == 2` is red
  today and only T-03 can turn it green.
- T-04's verify: first draft was **broken, not discriminating** — `harness_boundary` discarded the
  fixture root for carrying no `.harness/team-config.yaml` and fell back to the real repo root, so
  the rule could never have fired. Fixed by writing a minimal manifest into the fixture; all three
  probes then return exit 0 cleanly, with `bad` the clause T-04 must flip.
- T-08's verify: `hasattr(harness_boundary, 'worktree_for_feature')` is `False` today, and
  `inflight_registry.feature_root(root, 'FEAT-X-thing')` fails to resolve a registered `FEAT-X`
  worktree — ENG-A's second-consumer claim measured directly rather than cited.

## Open questions

- **Q1 (blocking, inherited).** The eng segment's Q1 stands unchanged: does the host's
  `SubagentStop` payload ever set `last_assistant_message` to an empty string on a tool-only final
  turn? D-01's exit-2 direction rests on the answer being no. Not answerable inside this repository.
- **Q2 (non-blocking, new).** F1's verbatim example spells the words `NOT VALIDATED` while the
  existing requirement pins the literal lowercase `not validated`, which T-01's verify greps. I
  applied the verbatim wording and resolved the collision by making every check of those words
  case-insensitive (T-01's `grep -qi`, T-02 cases 2 and 3), rather than editing the supplied
  wording. If the reviewer intended the lowercase spelling in the message itself, that is a
  one-word change to T-01's intent.
- **Q3 (non-blocking, new).** `check-domain.sh:1148-1150` passes `for_path=os.path.join(root, rel)`
  to `feature_schema` with the same stripped `rel` — the line L1 says T-04's mechanism was copied
  from. Out of FEAT-50's scope, and I did not establish whether it is a live defect there. It wants
  its own ticket.
