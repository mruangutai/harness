# Goal-check — FEAT-56 Central onboarding model — ship, cycle 0

**BLUF: the feature meets its goal pending only SC-09 (uat).** Nine of ten SCs graded at
`review_sha` 62debeaf: eight `met`, SC-09 `pending_uat`, none `not_met`. Every automated grade was
**re-run here**, not inherited from qa's earlier pin; every inspection grade was **re-cited at
62debeaf**, not inherited from the panel's 6f34e289 read. Five of the six REQs are fully covered.
**REQ-03 and REQ-04 are partly covered**: three live sites still assert the deleted per-product
install model, one of them inside a task's own `files:` list. Neither is graded by any SC — see
§Letter-only. Recorded, not fixed.

## Tree state at grading

- `git status --porcelain` — empty. Working tree clean.
- `git diff 62debeaf --stat` — one file, `features/FEAT-56.../feature.json`. HEAD is `43133830`.
- `git diff 62debeaf --name-only` over every path SC-01's block reads
  (`harness-init/SKILL.md`, `tests/integration/test-hooks-install.py`,
  `bin/check-instruction-paths.py`, `templates/team-config.yaml`) — **empty**. The working tree is
  byte-identical to 62debeaf for all of them, so SC-01's block was run **in-tree** (route: working
  tree, proven identical). Content-graded citations still use `git show 62debeaf:<path>`.
- Changed by the fix cycle, `git diff --name-only 6f34e289 62debeaf` (non-record files only):
  `harness-init/SKILL.md`, `bin/factory_config.py`, `docs/DECISIONS-INDEX.md`, `docs/DECISIONS.md`,
  `docs/SPEC.md`, `README.md`, `tests/unit/test-fleet-product-config.py`. Four of those are inside
  SC-04's fifteen; one is inside SC-01/SC-02's blob. Every panel grade over them was stale.

## SC verdicts

### SC-01 — `met` (automated, re-run)

T-01's `verify:` block cross-checked against `plan.yaml` T-01 by `yaml.safe_load` — **identical to
the block carried in the dispatch, character for character**. Run verbatim: **exit 0**.
Ordered markers, the discriminator: **DB=3 < FL=10 < SG=11** (`default_branch` at
`SKILL.md:3`, `factory/fleet.yaml` at `:10`, `.harness/<segment>/` at `:11`).
`templates/team-config.yaml` absent (the `!` conjunct passed). Tail of the block:
`test-hooks-install.py` printed 29 `PASS` lines and `EXIT=0`;
`check-instruction-paths.py` printed `scanned 62 file(s), 0 violation(s)`.

### SC-02 — `met` (automated, re-run)

`git show 62debeaf:.claude/skills/harness-init/SKILL.md | grep -nF`:

- `78:git config --get core.hooksPath || echo "(unset)"`
- `85:git config core.hooksPath .claude/skills/harness/hooks`

`python3 tests/integration/test-hooks-install.py` → `EXIT=0`, 29 `PASS`, 0 failures.

### SC-03 — `met` (inspection, re-cited at 62debeaf, one file at a time)

Six files, six citations, each read via `git show 62debeaf:<path>`:

| file | line | what it states |
|---|---|---|
| `bin/check-instruction-paths.py` | 12–15 | `MAIN_SESSION_ONLY` rationale is the anchor rule over a clone-relative `core.hooksPath`, not product ownership |
| `bin/check-state.sh` | 111 | `this clone is not an onboarded harness control plane. Run /harness-init in the control-plane clone.` (its other three remedies: `:287`, `:406`, `:2373`, all clone-scoped) |
| `bin/check-domain.sh` | 384–386 | `a product repository never carries one. Run /harness-init in the control-plane clone.` |
| `bin/upgrade-config.py` | 4–6 | docstring: a member's `harness.json` `must then be committed to the repository's default branch to be read at all` (remedies at `:192`, `:236`, both clone-scoped) |
| `bin/gh-sync.py` | 255–256 | skip message: `for a fleet member, that file lives in the member's own repository on its default branch` |
| `bin/layout_migration.py` | 123–131 | `MARKER` applicability: `Onboarding installs no bin/ into a product repository at all`; marker is `.harness/factory/fleet.yaml` |

None of the six was touched between 6f34e289 and 62debeaf, so the panel's read and mine agree — but
each was re-read at the new pin rather than inherited.

### SC-04 — `met` (inspection, re-cited at 62debeaf, one file at a time)

Fifteen files, fifteen citations, each `git show 62debeaf:<path>`. `†` = changed after the panel
read it, so this citation is new, not confirmatory.

| # | file | line | what it states |
|---|---|---|---|
| 1 | `.harness/harness/docs/SPEC.md` † | 134–135 | init `lands that repository's own harness.json on its default branch, registers it in the fleet, creates its` central tree (see also `:145`) |
| 2 | `.harness/harness/docs/BUILD.md` | 389 | `/harness-init` … `one file only, on that repository's default branch` |
| 3 | `.harness/harness/docs/DECISIONS.md` † | 6985 | `## DEC-220 — Onboarding is fleet registration plus one product-resident file` |
| 4 | `.harness/harness/docs/DECISIONS-INDEX.md` † | 220 | DEC-220 row: `nothing else enters a product repository` |
| 5 | `.harness/harness/docs/org.html` | 286 | `team-config.yaml` owner cell now reads `/harness-init · control plane only` |
| 6 | `README.md` † | 192 | the full ordered sentence: land `harness.json`, then register in `fleet.yaml`, then the central tree, `in that order (DEC-220)` |
| 7 | `.harness/README.md` | 18 | `a fleet member's, which must land on that repository's default branch` (not-onboarded definition at `:83-84`) |
| 8 | `templates/README.md` | 4 | `that repository's own harness.json, on its default branch — and everything else is` central |
| 9 | `templates/harness.json` | 2 | `_template`: instantiated as the control plane's own and as a member's own, `which must be committed to that repository's default branch` |
| 10 | `templates/team-config.yaml` | 3–5 | `instantiates this ONCE, as the control plane's own` … `a product repository never carries one` |
| 11 | `templates/BRIEF.md` | 1–2 | first draft written under `<HARNESS_FEATURE_TREE_ROOT>/.harness/<segment>/features/<FEAT>/BRIEF.md` — the central tree |
| 12 | `references/github-mirror.md` | 23 | `own harness.json on its default_branch, the file onboarding lands there` |
| 13 | `.claude/commands/harness.md` | 13 | not-onboarded = absent from `fleet.yaml`, config unreadable at default branch, or no central tree |
| 14 | `.claude/commands/harness-plan.md` | 19 | gate check includes `registration in .harness/factory/fleet.yaml` |
| 15 | `.claude/commands/harness-grilling.md` | 7–8 | answers seed `the repository's own harness.json — which must land on its default branch` |

**Weakest of the fifteen, stated plainly: #5, `org.html:286`.** It is a per-artifact ownership
table that never described onboarding as a procedure, so its citation discharges only the one-file
rule's *negative* half (`team-config.yaml` is control-plane only, which is exactly the false claim
this feature struck) and states neither fleet registration nor the one product-resident file.
Graded `met` because the file asserts nothing false and carries no room for the positive statement
— not because the citation is as strong as the other fourteen. Recorded so the grade is not read as
stronger than it is.

### SC-05 — `met` (automated, re-run)

`python3 tests/unit/test-fleet-product-config.py` → **exit 0, `18/18 checks passed`**. Both
directions in one run: `(b) the FIRST entry … is not ok and names repo and ref`, `(b) the SECOND
entry … is ok`, `(e) --check-product-configs exits 2 (EXIT_REFUSED) under a failing stub`,
`(e) … returns without SystemExit under an all-succeeding stub`, and
`(a) two declared repos, both succeed -> … ok count 2`. The redden-first proof for the exit-code
line is the build record (`notes/receipt-harness-backend-dev-*.md`); the two-direction assertion
itself is re-run here.

### SC-06 — `met` (automated, re-run)

`run-unit-tests.sh --kind unit` → **exit 0**, `pool: 8 workers, 34 files, 2.23s wall`.
Four `^FAIL ` lines appear (lines 957–962 of the run log) and **all four are inside
`test-factory-claim-mutation.py`'s by-design mutant output** — that file's own banner is
`----- test-factory-claim-mutation.py (exit 0, 0.35s) -----` and its verdict line is
`PASS test-factory-claim-mutation.py`. Graded on exit status, per the criterion, not on a FAIL grep.

### SC-07 — `met` (automated, re-run)

`run-unit-tests.sh --kind integration` → **exit 0**, `pool: 8 workers, 49 files, 69.30s wall`.
Grepped the whole run for a skip tied to a skill anchor: **no non-PASS skip/anchor line**;
`test-check-decision-anchors.py` passes including `ok - test_live_authority_anchors_all_resolve`,
and `PASS - product clone can read anchored systematic-debugging skill`. No case reports a skip for
a missing skill anchor.

### SC-08 — `met` (automated, re-run)

- `python3 .claude/skills/harness/bin/check-omp-port.py` → `OMP port surface: ok`, exit 0.
- `python3 .claude/skills/harness/bin/check-instruction-paths.py` → `scanned 62 file(s),
  0 violation(s)`, exit 0.

### SC-09 — `pending_uat`

Not met and not failed by me. Script written: `notes/uat-FEAT-56.md` (five steps, ~10 minutes).
Only the operator's stated PASS/FAIL settles it.

### SC-10 — `met` (automated, re-run)

`python3 -c "import yaml;yaml.safe_load(open('.claude/skills/harness/templates/team-config.yaml'))"`
→ **exit 0** (the file is identical to its 62debeaf blob, verified by `git diff --name-only`).

## REQ coverage — one line each

- **REQ-01** (SC-01, SC-09) — **covered pending uat.** SC-01's ordered-marker check is met at
  DB=3<FL=10<SG=11 and the struck copy instruction is absent; the judgement half is SC-09's.
- **REQ-02** (SC-02) — **covered.** Both command strings present verbatim at `SKILL.md:78,85` and
  the hooks-install suite green.
- **REQ-03** (SC-03) — **partly covered.** All six named sites state the central model, but
  `bin/check-state.sh:374` still asserts `COPIED INTO EVERY ONBOARDED PROJECT by /harness-init` —
  an executable site asserting the deleted model, outside SC-03's four-remedy scope for that file.
- **REQ-04** (SC-04, SC-10) — **partly covered.** All fifteen files carry a correct statement and
  the template parses, but `templates/harness.json:5` still says `check-state.sh is copied into
  every onboarded project` — inside T-05's own `files:` list, and the same claim is mirrored in this
  clone's live `.harness/harness.json:4`.
- **REQ-05** (SC-05) — **covered.** `--check-product-configs` names the unreachable member and exits
  2; 18/18 unit checks green at the pin.
- **REQ-06** (SC-06, SC-07, SC-08) — **covered.** Both suites exit 0 and no test was deleted at all
  (`git diff --diff-filter=D 4b5dbb23 62debeaf -- tests/` is empty), so the "deleted with its reason
  recorded" clause is vacuous; four integration files were amended in place (T-03).

## Letter-only — yes, in one shape

**SC-03 and SC-04 are met in letter while the claim they exist to retire survives in three live
files.** Both criteria grade by *one `file:line` per named file*; a file whose cited line is correct
passes even when a second line in the same file contradicts it. Concretely, at 62debeaf:

- `.claude/skills/harness/bin/check-state.sh:373-374` — `THE BOUNDARY IS PER-PROJECT CONFIG … This
  file is COPIED INTO EVERY ONBOARDED PROJECT by /harness-init`. False under the central model:
  `deploy.sh` is deleted (DEC-113) and nothing distributes `bin/`.
- `.claude/skills/harness/templates/harness.json:5` (`_panel_era_start_note`) — `check-state.sh is
  copied into every onboarded project, so this MUST be per-project`. **This file is in T-05's
  `files:` list and is SC-04 item #9**; the criterion's citation (`:2`) is correct, the file is not.
- `.harness/harness.json:4` — the same sentence, in this control plane's live config. Not named by
  any SC.

The *conclusion* each one supports (`panel_era_start` must be per-project) still holds under the
central model — a member's `harness.json` is instantiated per repository — so this is stale
reasoning, not a wrong value. Occurrences under `features/**` are record and must not be touched
(DEC-188). **Recorded only. No fix, no SC amended, no scope widened** — this is a residue for the
operator to route as a follow-up chore, not a gate on this ship.

## Emergent — one thing BRIEF never asked for

**Landing `harness.json` on a product's default branch is a trust delegation, and the rewritten
skill now says so** (`harness-init/SKILL.md:167-168` at 62debeaf: *"Landing this file delegates
control of what the factory reads for this member to whoever can push its default branch. Do not
register the member unless that trust is intended."*). **New** — no REQ, no SC and no non-goal in
BRIEF states it; it is a consequence DEC-174's no-disk-fallback rule makes reachable, surfaced
during the build. **Recommend:** the operator reads it as part of UAT step 3 and decides whether it
warrants its own decision entry. **Not adopted and not graded here** — an emergent criterion is not
mine to adopt.

Secondary, already covered: the V-7 stderr grammar (`factory: config: ` prefix, the
`repo@ref:path` triple named exactly once) is an operator-visible output contract BRIEF never
mentioned; it is asserted by two unit checks in `test-fleet-product-config.py`, so it needs nothing.

## V-8 — re-confirmed at 62debeaf, no test added

Read at the pin. `product_config_report` (`bin/factory_config.py:341-353`) is a bare
`for entry in fleet["repos"]` whose body ends in an unconditional `report.append(...)` — **no early
return, no `continue`, no skip path, no filter**. So `len(report) == len(fleet["repos"])` holds for
every input the public surface can produce, and the second disjunct of
`_check_product_configs`'s exit guard (`:478`, `or len(report) != len(fleet["repos"])`) is
**unreachable through the public surface**. Still not worth a test: the falsifiable half of the
invariant is already asserted three times in the unit suite (the `(a)/(d)`, `(b)/(d)` and `(c)/(d)`
`len(report) equals len(fleet['repos'])` checks, all green above), and the only way to redden the
guard's second disjunct is to reach into the module and stub the report builder — a test of the
stub, not of the code. **Confirmed still true, still not worth a test, nothing added.** Prior
statements: `notes/review-harness-qa-c0.md:83,97-101`,
`notes/receipt-harness-backend-dev-fix-code-eng.md:120-127`,
`notes/receipt-harness-dev-ops-simplify-simplification.md:49-57`.

## Open questions

- **Q1 (non-blocking):** the three stale `copied into every onboarded project` sites above. A
  follow-up chore, not a fix cycle — no SC grades them and no REQ fails outright.
- **Q2 (non-blocking):** whether the trust-delegation consequence earns its own decision entry.
