## Plan-panel review — FEAT-56, scope lens (plan-phase, no review_sha)

reviewed: plan:.harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml
code_grade: n_a

**BLUF.** Structurally the plan is sound — 8 tasks trace to all 6 REQs, `depends_on` is a valid
topological order (T-04 → T-01 → {T-02,T-03,T-05,T-06,T-08} → T-07), and the fix cycle's two
closures (D2 #203/#206 reconciliation, D3 the `team-config.yaml` parse error) are real: I
independently reproduced the `yaml.ParserError` at `templates/team-config.yaml:28` col 11 / line 33
col 1 on the current tree, matching the fix-cycle note and T-05's repair verbatim. No orphan REQ, no
task tracing a nonexistent REQ, no verify block that references a file a predecessor deletes or
renames. The four leads I was handed each check out on inspection — three refute cleanly, one (T-05
red claim) confirms. The two assigned questions surface two real, unaddressed gaps in how the plan's
21 inspection-only files get backed by anything mechanical.

### Findings

1. **SC-01 is labeled `verify: inspection` but T-01's own `verify:` already mechanically discharges
   every element it claims.** severity: low. `BRIEF.md:92-97` requires four things of the rewritten
   skill (fleet.yaml mention, central-tree mention, `default_branch` mention, no
   `templates/team-config.yaml` match); `plan.yaml:168-172` (T-01's `verify:`) greps for exactly
   those four, unconditionally, before any human reads the file. `BRIEF.md:151-154`'s own
   "Verification gaps" section states "only SC-02's verbatim strings and SC-09's operator read stand
   behind" the rewrite — that understates what already exists. Consequence: a reviewer duplicates
   machine-proved work under SC-01's inspection citation, and the BRIEF's own risk framing is
   inaccurate about existing coverage. Fix is cheap: reclassify SC-01 `verify: automated`, or note in
   BRIEF that T-01's verify discharges it.

2. **Answering lead Q1 — no, the plan's acceptance cannot distinguish "rewritten and correct" from
   "rewritten and merely keyword-compliant."** severity: med. T-01's mechanical checks
   (`plan.yaml:168-173`) are `grep -qF` substring tests anywhere in a 370-line file — they cannot
   detect whether D-04's load-bearing ordering claim (config lands on default branch BEFORE fleet
   registration) survives the rewrite, or whether the nine steps remain internally consistent. A
   rewrite could mention every required token, omit the forbidden one, and still state the steps in
   the wrong order or contradict D-04, and pass T-01's `verify:` and a good-faith SC-01 citation
   (the tokens are present *somewhere*). Only SC-09 (`BRIEF.md:139-141`, `verify: uat`, a one-shot
   operator read after all 8 tasks land) would catch that class of error, and BRIEF says so itself
   (`:158-160`, "Verification gaps"). This is disclosed, not hidden — but it is the direct answer to
   the question, and a cheap incremental check is available and unused: assert the *order* of two
   markers mechanically (e.g. compare the line numbers `grep -n` returns for the fleet-registration
   marker text vs. the harness.json-landing marker text) rather than only their presence. That would
   catch a reordering defect — this feature's own failure class — before UAT, not just at it.

3. **Answering lead Q2 — inspection at 21 files is not a rubber stamp for ~18 of them (their owning
   task's own `verify:` already backs the same claims), but two files in T-06 carry zero mechanical
   backing despite being the routing prose this feature exists to fix.** severity: med. T-06's
   `files:` (`plan.yaml:565-569`) lists `.claude/commands/harness.md` and
   `.claude/commands/harness-grilling.md` alongside `harness-plan.md` and the two dev-ops agent
   files; T-06's `verify:` (`plan.yaml:570-574`) greps `harness-plan.md` once and each dev-ops file
   once — nothing greps `harness.md` or `harness-grilling.md` at all. Both are read at runtime, not
   just by a human: `harness.md:11-13`'s "## 0. Gate" paragraph is literally the routing condition
   ("except 'BRIEF.md missing', which routes to `/harness-init`") the main session evaluates on
   *every* `/harness` invocation, and T-06 item 1's own intent says this exact condition is stale and
   must be restated (registered in fleet.yaml / config unreadable / no central tree — not "BRIEF.md
   missing"). `harness-grilling.md:7-8` carries the same exposure ("the answers seed `harness.json`,
   the domain description, and the first glossary terms" — confirmed present, unedited, at HEAD). A
   subtly wrong rewrite of either ships undetected by anything but one reviewer's SC-04 citation
   spread across fourteen other files in the same pass. Cheap fix: mirror the `harness-plan.md`
   treatment — one `grep -qF` per file added to T-06's `verify:`. Same shape, lower priority:
   `templates/harness.json`'s `_template` field (currently at `templates/harness.json:2`, "Canonical
   harness.json. /harness-init copies this to .harness/harness.json...", the exact stale sentence
   T-05 item 2a must replace) gets only a `json.load` validity check in T-05's `verify:`
   (`plan.yaml:481`) — no content assertion — though it is the text every future onboarded
   repository's operator reads at instantiation. `SPEC.md`/`BUILD.md`/`DECISIONS.md` (T-07, zero
   automated backing either) are lower-priority still: static reference docs, not runtime-evaluated
   routing prose.

### Leads — checked at source, three refuted, one confirmed

- **T-04's SC-05 stubs — not a weakness, matches established convention.** severity: info (non-issue,
  recorded per P-15). `factory_config.product_config` (`factory_config.py:180-215` in this worktree)
  is already unit-tested exclusively via a stubbed `factory_gh.file_at_ref`
  (`tests/unit/test-factory-config.py:14-19,62-70` — `patched_file_at_ref`, "No case in this file
  may invoke gh or make a network call"). `factory_gh.file_at_ref` itself has its own separate unit
  file (`tests/unit/test-factory-gh.py`, confirmed present). T-04's `test-fleet-product-config.py`
  follows the exact same layered pattern the codebase already uses for every GH-remote read; the
  stub proves the report's aggregation logic, not the wire call, which is out of scope and already
  covered elsewhere.
- **T-01 `depends_on: [T-04]` — not an inversion.** severity: info (non-issue). T-01's rewrite
  literally names T-04's CLI flag (`--check-product-configs`) and its verify greps for the literal
  string (`plan.yaml:172`). Sequencing the doc after the flag lands and is proven (rather than before)
  avoids documenting an interface that does not yet exist or could still change shape — a defensible
  build-order choice, not a topological error; no cycle exists (T-04 has `depends_on: []`). One minor
  observation: the dependency is not itself verify-enforced — T-01's grep-based checks would pass
  identically whether or not T-04's code exists — so the ordering is a construction-time discipline,
  not a build-time gate. Not worth a separate finding.
- **T-03 "amends and deletes tests" — it deletes none.** severity: info (non-issue). Re-read
  `plan.yaml:389-457` (T-03's full intent): 4 items under "AMENDED - comment only, assertions
  untouched," 4 items under "UNCHANGED, and each for a stated reason — assert this rather than assume
  it." Every one of the 8 named test-file sites is individually named with its exact disposition; none
  is deleted; nothing is left to a doer's discretion.
- **T-05's verify RED claim at `templates/team-config.yaml` — confirmed independently, not just
  quoted from the fix-cycle note.** severity: info (confirms a prior claim). Ran
  `python3 -c "import yaml;yaml.safe_load(open('.claude/skills/harness/templates/team-config.yaml'))"`
  against this worktree: `yaml.parser.ParserError: while parsing a flow sequence ... line 28, column
  11 ... expected ',' or ']', but got '<scalar>' ... line 33, column 1` — byte-for-byte the failure
  `notes/research-FEAT-56-planfix-c1.md` reports, and the cause (unquoted `## Approval` inline
  comments inside the `main_session.writes:` flow sequence at `templates/team-config.yaml:28`) is
  visible at source. T-05's repair (quote all three entries) is well-specified and its `verify:`
  places the load as the first `&&` conjunct (`plan.yaml:480`), so it cannot pass without actually
  fixing the parse.

### Not found

No orphan `REQ-NN`, no task citing a nonexistent REQ, no `depends_on` cycle or out-of-order listing,
no `verify:` clause asserting content a predecessor task deletes or renames (T-03 explicitly
re-anchors the two line-number citations into `SKILL.md` that T-01's rewrite would otherwise rot —
`plan.yaml:410-413,449-455`). No `verify:` clause found to be tautological or checking for a string
its own task's intent does not require.
