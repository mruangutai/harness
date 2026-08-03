# PLAN — FEAT-05 PyYAML file parsers

**BLUF.** One new shared module (`bin/harness_yaml.py`) and its test file, **helper first**, then four
non-hook conversions, a typed-value sweep with its own verify, a session-identity probe, and only then
the two hooks — each followed immediately by its launch-consolidation, because the conversion measurably
regresses an every-write hook, and the sweep's second half (T-17) after them, because the hooks are not
walkable until they are converted. **Seventeen tasks.** Three paths (`.gitignore`,
`templates/gitignore.snippet`, `harness-init/SKILL.md`) have **no agent owner** and are `main-session`
steps sitting *inside* the spine, not after it; T-01 additionally mixes a main-session machine action
with two **orchestrator**-owned writes — see `## Routing wall`.

Two things measured during planning that the BRIEF and the eng consult did not have:

1. **`cost-report.py` has zero YAML reads.** Its only state.yaml touch (`:189`) is a line-preserving
   *writer*. So does `gh-sync.py:200`. D-04 rules that writers stay line-based, which narrows REQ-01's
   second clause — raised as Q1 so the user sees the narrowing at signature.
2. **The census the BRIEF rests on was taken with a pattern that omits `re.sub`.** Re-run whole
   (`re.(search|findall|match|finditer|sub|split|compile)`) the six files hold **50** regex calls, of
   which **23 convert and 27 stay**. `## Regex census` is the reviewer's answer key for SC-03; SC-03's
   parenthetical ("the only regex calls remaining in `check-state.sh` are the two out-of-scope
   non-YAML ones") undercounts by five and is raised as Q2.
3. **SC-13 was checked, and it holds.** SC-13 ("identical run set") and SC-01 ("the conversion recovers
   dropped runs") would conflict outright if any run in this tree were already being dropped. Run
   against the pre-change parser's own two regexes, `parsed == declared` for all five features
   (1/1, 4/4, 19/19, 15/15, 1/1) — no run is dropped today, so SC-13 stands as written. T-01 step 3
   writes that listing to a file so SC-13's "reviewer cites both listings" has something to cite.

Baseline pinned at `37a8a66`. `prototype_required: false` — product-lead's reaffirmed ruling: `bin/`
scripts, two hooks, one `SKILL.md`, no end-user surface. No design work is planned.

## Decisions

**Numbering map — read this before cross-referencing the eng consult.** This plan's `D-NN` numbers are
its own and do **not** align with eng-lead's residual list. The correspondence, so a reviewer following
the dispatch's citations lands on the right paragraph:

| eng-lead | here | subject |
|---|---|---|
| D-01 | **D-01** | gitignore chain |
| D-02 | **D-02** | duplicate-key detector survives |
| D-03 | **D-10** | consolidation as regression mitigation |
| D-04 | **D-09** | `review_sha: none` fail-open |
| D-05 | **D-08** | third typed-value class |
| D-06 | **D-12** | SC-04 receipt |
| D-07 | **D-03** | `manifest_domains()` extraction |
| D-08 | **D-13** | the `read:` tightening |
| — | **D-04**, **D-05** | new here: writers stay line-based; the regex census |
| E4 / Q3 | **D-06** | no bootstrap escape for `check-state.sh` |
| E1 / Q4 | **D-07** | the two-line install command |

- **D-01: the `.harness/.pyyaml-bootstrap` ignore rule lands in BOTH
  `.claude/skills/harness/templates/gitignore.snippet` AND this repo's own `.gitignore`, and the
  upgrade path names a `merge-gitignore.sh` re-run.** Verified at source: `gitignore.snippet:7` ignores
  only `.harness/features/*/runs/**` under `.harness/`, and `:4-6` states everything else there is
  committed on purpose; this repo's own `.gitignore:1-20` carries the same rule set and no marker line.
  `merge-gitignore.sh:6-9` states a dirty tree halts a team run with `BLOCKED`. So an untracked marker
  file dirties the tree and **deadlocks the next team run on every checkout that pulls this** — the
  marker is written by the very hook that fires when the run starts. `merge-gitignore.sh` reads its rule
  list from the snippet and is idempotent (`:44-51`), so an existing checkout recovers by re-running it;
  that re-run must be named in the upgrade path, not left to be discovered. *Trade-off accepted:* the
  snippet's rule count changes, so `merge-gitignore.sh --check` goes red on every already-initialised
  project until it is re-run. That is the intended loud signal, not a regression.
  *Rejected — `$TMPDIR` for the marker.* It dodges the gitignore change entirely, but a tmp clear or a
  reboot silently re-grants the escape. A permanent bypass by neglect is precisely the failure mode
  this feature exists to design against.

- **D-02: `check-domain.sh`'s duplicate-key detector SURVIVES the conversion, and the shared loader
  RAISES on a repeated key. `yaml.safe_load` is never called directly on state.yaml content.**
  Measured: `check-domain.sh:285` extracts top-level keys by regex and `:287` detects duplicates,
  rendering a DEC-156 denial. `yaml.safe_load` collapses duplicate keys silently, last wins (dev-ops
  probe 5a, output `{'id': 'second'}`, no raise). A task worded "remove all YAML regex from
  `check-domain.sh`" makes a builder delete a working fail-closed check and replace it with a
  fail-open — the exact defect class this feature exists to remove. The loader is a `SafeLoader`
  subclass overriding `construct_mapping` to raise `ConstructorError` on a repeat (dev-ops probe 5d:
  raises on `id: first / id: second`, leaves normal mappings unaffected, combines with the
  timestamp-resolver strip in one class). The detection **strengthens**: it currently sees only
  column-0 duplicates and will then see nested ones too.
  Two consequences the builder must handle, and neither is optional:
  1. the block catches `ConstructorError` and renders the **existing** DEC-156 denial message verbatim,
     so the user-visible output does not change for the case that already worked;
  2. a `state.yaml` Write whose content is **not valid YAML** now raises where the regex silently found
     no keys. That must **deny with a parse-error message**. This is a **new blocking outcome, not a
     regression** — recorded here so a reviewer does not read it as one.
  *Trade-off accepted:* `check-domain.sh:280` says `KEEP IN SYNC with CHECKPOINT_KEYS in
  check-state.sh`. After this decision the two twins diverge by **mechanism** (raising loader vs. regex
  scan) while the key *vocabulary* stays in sync. The comment must be updated to say exactly that, or
  the next reader syncs them back and re-opens the fail-open.

- **D-03: the manifest domain walk moves into the shared module as
  `manifest_domains(manifest_path, agent) -> (mine, shared)`, and BOTH call sites are converted to use
  it.** Verified duplicated: `check-domain.sh:105-126` (`collect()`) and `bash-write-guard.sh:248-263`
  are the same logic, and this conversion would otherwise rewrite that line-scan as a dict walk **by
  hand, in both files**. Divergence here is security-relevant, not cosmetic: `bash-write-guard.sh`
  exists because an agent already routed around `check-domain.sh` (DEC-151), so the two hooks
  disagreeing about what a domain *is* re-opens that hole. *Trade-off accepted:* the two hooks gain a
  hard dependency on a third file; if `harness_yaml.py` is deleted or unreadable both hooks fail closed,
  which is the correct direction of failure.

- **D-04: the conversion is scoped to YAML *reads*. Writers stay line-based, and this narrows REQ-01's
  second clause.** Measured, and it changes the task list: **`cost-report.py` reads no YAML at all.**
  Its two regex calls are `:112` (a path-munge `re.sub`, not YAML) and `:189` (`^cost:`, inside
  `patch_state_cost`, a line-preserving in-place rewrite of a run's `state.yaml`). `gh-sync.py:200`
  (`save_recorded`) is the same shape — a `re.sub` that excises and re-emits the `github:` block.
  Round-tripping either file through `safe_load`/`safe_dump` **strips every comment and reorders every
  key**, and this repo's `state.yaml` and `feature.yaml` files carry load-bearing inline comments (e.g.
  `FEAT-05/feature.yaml:6-10`, `FEAT-04/feature.yaml:9`). `check-domain.sh:275-298` also validates
  `state.yaml` by top-level key on Write, so a reformatting writer would start tripping the hook it
  shares a repo with. **Rule: a script that only writes a YAML file keeps its line operations; a script
  that reads values out of one converts.** *Trade-off accepted, stated plainly:* REQ-01's literal text
  says "no hand-rolled YAML key/value regex is left behind in those scripts", and under this decision
  two remain — `cost-report.py:189` and `gh-sync.py:200`. Both are writers, both are recorded in the
  census, and neither can silently void an invariant (the Problem statement's failure mode), because
  neither produces a value any check consumes. **Raised as Q1** so the user sees the narrowing rather
  than inheriting it.

- **D-05: `## Regex census` below is the answer key SC-03's reviewer cites against, and SC-03's
  parenthetical is a measured undercount.** SC-03 states the only regex calls remaining in
  `check-state.sh` are two. Measured at `37a8a66`, `check-state.sh` holds **17** regex calls, of which
  **7** legitimately survive: six parse **markdown** (`:46 :47 :50` read `## Approval` in `PLAN.md`;
  `:76 :78` read `T-NN` in `PLAN.md`; `:89` reads `T-NN` in `STATE.md`) and one is the BRIEF-exempted
  `CHECKPOINT_KEYS` scan. Converting markdown parsing to a YAML parser is not a coherent instruction, so
  SC-03's *operative* sentence — "Reviewer cites each remaining regex call in the six files by
  `file:line` and classifies it" — is what this plan is built to satisfy. **Raised as Q2** as a BRIEF
  amendment for the user, not silently reinterpreted.
  Anchor drift worth naming, since two upstream artifacts repeat it: the BRIEF and the eng dispatch both
  cite `CHECKPOINT_KEYS` at `:279`. Measured, the set is declared at `check-state.sh:277-288`, its regex
  scan is at `:302`, its duplicate check at `:303` and its unknown-key check at `:308`. Cite the
  measured anchors.

- **D-06: `check-state.sh` gets NO bootstrap escape. Ruled: no.** (E4 / eng Q3, settled here as the
  BRIEF's deferred item required.) `check-state.sh:11-12` documents that it gates the **orchestrator**
  and exits 1, not a PreToolUse hook — so refusing to open the `/harness` door blocks no recovery. The
  repair is one printed `pip` command in a shell, which needs no harness. The two hooks need the escape
  because they gate the **writes**, and writes are what a repair inside the tool requires.
  **The consequence, stated plainly rather than left implicit:** on a PyYAML-less machine, the two hooks
  permit writes for exactly one session while the `/harness` door refuses to open — so during that
  session the recovery path is *editing files outside the harness*, or better, running the printed
  install command. That asymmetry is deliberate: the two guards protect different things, and an
  unbounded escape on the orchestrator gate would buy nothing, because an orchestrator that cannot read
  state cannot safely act on it either. *Trade-off accepted:* a user who ignores the printed command and
  keeps working will hit a hard `/harness` block before they hit a write block.

- **D-07: the install command is two printed lines, gated on the named PEP 668 error text and never on
  exit status. The older-pip branch is `[reasoned, unverified]`.** (E1, plus Q4 ruled here.) Exactly:

  ```
  python3 -m pip install pyyaml
  # if that fails with "externally-managed-environment" (PEP 668, e.g. Homebrew/Debian):
  python3 -m pip install --break-system-packages pyyaml
  ```

  `python3 -m pip`, never bare `pip`: four `python3` interpreters are on this PATH (verified,
  `which -a python3`), each with its own pip. A bare `||` fallback is wrong — it fires on any nonzero
  exit (network, missing pip, permissions), not specifically on PEP 668, so an unrelated failure would
  trigger a confusing second attempt. Dry-run verified: `pip --user` produces the *identical*
  `externally-managed-environment` error and does not escape PEP 668; `--break-system-packages
  --dry-run pyyaml` succeeds cleanly on Homebrew's pip 26.1.1.
  **Q4, ruled and recorded as a known-unverified branch, not as tested:** the reason the plain install
  must be attempted *first* is that `--break-system-packages` is unknown to pip < 23.0.1 and raises "no
  such option" there. **No pip that old exists on this machine to prove it against** (Homebrew 26.1.1,
  `/usr/bin` 24.1.1), so the ordering rests on documented pip history, not on a local observation.
  Recorded as `[reasoned, unverified]` in the source comment beside the string, so a future reader
  does not mistake it for a measured constraint. It is not worth blocking on: the ordering is harmless
  if the reasoning is wrong.
  *Rejected — pipx* (installs applications into isolated venvs, so the library is not importable by an
  arbitrary `python3`; also not installed here, so `[reasoned]`). *Rejected — a venv*, unless it is on
  PATH for the hook subprocess, which the BRIEF's interpreter constraint forbids. **Bare `python3` off
  PATH stays as the interpreter policy.**

- **D-08: the typed-value walk rule — `str()` at the consumer for any value used as a path component,
  an identifier, or a dict key. The bool/int/float resolvers are NOT stripped; the timestamp resolver
  IS.** `safe_load` returns typed values where the regex returned strings, and there are **three**
  hazard classes, not the two the BRIEF names:
  1. **int** — `check-state.sh:120` calls `cu.isdigit()` on `cycles_used`, which becomes an `int` and
     raises `AttributeError`. Verified at source.
  2. **date** — a bare date-shaped scalar becomes `datetime.date` (dev-ops probe 5b). Run ids like
     `2026-07-31-01-product` carry trailing text and stay `str`; a bare `2026-07-31` would not.
  3. **bool/float/all-digit** — YAML 1.1 also coerces `on`/`off`/`yes`/`no` to `bool`, an all-digit
     abbreviated commit SHA to `int`, and a `1e10`-shaped one to `float`.
  **Do not strip the bool/int/float resolvers.** `schema_version` and `cycles_used` genuinely want
  ints, and stripping them would trade one silent breakage for another. The **timestamp** resolver IS
  stripped in the shared loader (dev-ops probe 5c: a `SafeLoader` subclass with
  `tag:yaml.org,2002:timestamp` removed returns `2026-07-31` as `str`, normal mappings unaffected), so
  SC-10's date regression becomes structurally impossible in one place rather than fixed by vigilance
  at N consumers. The `str()` rule is defence in depth for the consumer who forgets. *Trade-off:* a
  downstream caller that actually wants a `datetime` must parse it itself. Nothing in this repo does.

- **D-09: `check-state.sh:113`'s `review_sha: none` fail-open is DEFERRED, not fixed here, and is filed
  as a GitHub issue in the same pass.** `:113` tests `not val("review_sha")`, but `feature.yaml` holds
  the literal string `review_sha: none` (verified, `FEAT-05/feature.yaml:6`), and PyYAML's null resolver
  matches `~`, `null`, `Null`, `NULL` and empty — **not** lowercase `none`. So it is a truthy string
  under both the regex and `safe_load`, INV-6 passes on a feature with no pinned SHA, and the conversion
  changes nothing about it.
  **I ran the discriminating check rather than reasoning about the cost.** Across all five
  `feature.yaml` files, every feature carrying a `squad: validator` run also carries a real SHA
  (`FEAT-01 a606d7a..9b07cfc`, `FEAT-02 d9b16e53…`, `FEAT-03 e68ba00`, `FEAT-04 363b539`); only
  `FEAT-05` holds `review_sha: none`, and it has **no validator run recorded**. So fixing D-09 today
  would fire **zero** new violations — it is cheap, and that is *not* the reason to defer.
  **The load-bearing reason is evidence integrity.** SC-02 and SC-13 exist to prove the conversion
  changed *nothing* behaviourally — same exit code, same violation set, same run inventory. A
  deliberate semantic change inside `check-state.sh` in the same ship makes those two criteria unable
  to distinguish "the conversion was faithful" from "the conversion broke something and the semantic
  fix masked it". Second reason: no REQ covers it, so fixing it is scope the user did not sign. Third:
  `FEAT-05`'s own validator run lands *during this feature's build*, and a newly-firing INV-6 at that
  moment wedges the `/harness` door on the self-hosted machine mid-build. **Filed, not forgotten** —
  T-16 opens the issue. *Trade-off accepted:* the fail-open survives one more ship.

- **D-10: the launch consolidation is regression mitigation, not polish, and it is a separate task
  immediately after each conversion.** dev-ops re-measured the **full governed hook path** (synthetic
  payload, `agent_type: harness-backend-dev`, `Write`, in-domain path, all four Python blocks confirmed
  to run) at **80.63ms/iter** over 100 iterations — **not** the 23.7ms the grilling recorded, which was
  the no-`agent_type` one-launch early exit at `check-domain.sh:48`. Converting the blocks at `:97` and
  `:235` each adds an `import yaml` (~12ms apiece), pushing an **every-write** hook to roughly 105ms
  [estimated]. Merging `check-domain.sh`'s four launches into one measured 17.94ms on a simplified proxy
  and is estimated at 25-35ms for a real merge [dev-ops: lower bound — the proxy omits glob-regex
  compilation and `safe_load`]. So the merge does not make the hook faster than today by accident; it
  is what keeps this feature from shipping a ~30% latency regression on the hottest path in the tree.
  **Separate task, same owner, immediately after** — separate so a reviewer can check behaviour
  equivalence without a restructure confounding the diff on the most safety-critical script in the
  tree; immediately after so the regression never ships. `bash-write-guard.sh` gets the same 2-to-1
  merge at lower priority (~17ms).

- **D-11: `glob_to_re` and `matches` stay duplicated. They do not change in this conversion.** Verified
  duplicated (`check-domain.sh:160-196` == `bash-write-guard.sh:265-287`, including the `re.compile`
  at `:182` / `:278`). Sharing them is a separate refactor on the two most safety-critical scripts in
  the tree, it is not required by any REQ here, and widening the diff makes the D-03 change harder to
  review. Stated as scope discipline so a builder does not take the shared module as licence.

- **D-12: exactly ONE `try: import yaml / except ImportError:` exists in the whole tree, in
  `harness_yaml.py`, and it parses nothing — it exits or grants.** This is SC-04's receipt. Six
  scattered guarded imports would read to a reviewer as six fallback paths, which is exactly what SC-04
  and the BRIEF's no-fallback constraint forbid; one, in a module whose only job is the dependency
  policy, reads as the policy. Naming it here pre-empts the reviewer misreading the module's own try
  as the forbidden fallback.

- **D-13: the `read:` tightening is a fix that will read like a regression, and it ships anyway.** The
  domain walk's read-only filter is today `"read: true" not in s` — a substring test on the raw line
  (`check-domain.sh:122`, `bash-write-guard.sh:260`). A manifest written `read: yes`, `read: True` or
  `read:true` does not match it, so the path lands in `mine` and the agent may write a read-only path:
  a live fail-open. After `safe_load` all three resolve to `True` and the path is correctly excluded,
  so the conversion **newly blocks** writes that pass today. Measured in this repo: all 16 `read:`
  occurrences in `.harness/team-config.yaml` are the canonical `read: true`, and every one is on
  `{ path: ".", read: true }`, which `matches()` already rejects unconditionally
  (`check-domain.sh:187`). **Zero entries change classification here.** It is recorded because a
  downstream project's manifest is not covered by that measurement, and a downstream user who suddenly
  cannot write a path needs to find this paragraph.

## Regex census — the answer key for SC-03 (D-05)

Measured at `37a8a66` with `grep -nE 're\.(search|findall|match|finditer|sub|split|compile)'` — the
wider pattern, because the census every upstream artifact rests on omitted `re.sub` and therefore never
saw `gh-sync.py:200`. **50 calls: 23 convert, 27 stay.** A reviewer satisfying SC-03 cites this table
and confirms each row at final state.

| File | CONVERT (YAML reads) | STAY, and why |
|---|---|---|
| `check-state.sh` | `98` `108` `109` `237` `293` `297` `316` `394` `398` `399` — **10** | `46 47 50` markdown `## Approval` in PLAN.md · `76 78` markdown `T-NN` in PLAN.md · `89` markdown `T-NN` in STATE.md (BRIEF-exempt) · `302` the `CHECKPOINT_KEYS` scan (BRIEF-exempt; set at `277-288`, dup at `303`, unknown at `308`) — **7** |
| `check-domain.sh` | `112` `119` → `manifest_domains()` (D-03) · `285` → raising loader, **detector at `287` survives** (D-02) — **3** | `157 248` worktree path rewrite · `182` `glob_to_re` compile (D-11) · `263 275 300 321` rel-path routing — **7** |
| `bash-write-guard.sh` | `252` `257` → `manifest_domains()` (D-03) — **2** | `112` heredoc scan · `185` redirect scan · `278` `glob_to_re` compile (D-11) · `298 306` path routing — **5** |
| `gh-sync.py` | `181` `184` `186` `188` `190` `193` — `load_recorded()` reads `feature.yaml`'s `github:` block — **6** | `128 135 153 157 159` markdown BRIEF/PLAN parsing · `200` `save_recorded` **writer** (D-04) — **6** |
| `cost-report.py` | **0** — it reads no YAML (D-04) | `112` path-munge `re.sub` · `189` `^cost:` in-place **writer** (D-04) — **2** |
| `upgrade-config.py` | `91` `yaml_names` · `98` `yaml_version`, both read `team-config.yaml` — **2** | none — **0** |

## Tasks

### T-01 — make PyYAML importable by the hooks' `python3`, and re-pin the baseline

- owner: **main-session** for step 1 (a machine action, no repo write) · **harness-orchestrator** for
  steps 2 and 3, which write `feature.yaml` and a note under `.harness/features/**` — the
  orchestrator's domain (`team-config.yaml:28`). See `## Routing wall`
- change_type: config
- traces: REQ-03, D-07
- depends_on: —
- absorbs: —

**This is the self-hosting prerequisite and it is first for a reason.** Verified on this machine right
now: `which -a python3` resolves to `/opt/homebrew/bin/python3` first, and
`python3 -c 'import yaml'` raises `ModuleNotFoundError: No module named 'yaml'`. Land a converted hook
before this task and every agent write on the build machine takes the bootstrap escape once and then
**blocks — including the write that would fix it.** BRIEF:63-65 states this as a hard constraint.

1. Run D-07's first line; if it reports `externally-managed-environment`, run the second.
2. Re-measure the `check-state.sh` baseline. **The BRIEF's SC-02 baseline is stale:** run today,
   `check-state.sh` exits **1** with one VIOLATION (`FEAT-05-pyyaml-file-parsers/BRIEF.md has no
   '## Approval' section`) plus 42 INV-8 notes — the grilling's "exit 0, zero violations" predates this
   feature's own BRIEF and PLAN. The BRIEF violation clears when the main session signs (the PLAN adds
   a second until then), and the two FEAT-05 orphaned-run-dir notes clear when the orchestrator records
   runs 02 and 03. Record the **post-approval** exit code and violation count in `feature.yaml` under
   `baseline:` as `baseline_exit:` and `baseline_violations:`.
3. **Write the pre-change run inventory to a file.** `check-state.sh` prints no run listing, so SC-13's
   "reviewer cites both listings" has nothing to cite unless one is produced deliberately. Run exactly
   this, redirected to
   `.harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-baseline-run-inventory.md`:

   ```
   python3 - <<'PY'
   import re, glob
   for fy in sorted(glob.glob('.harness/features/*/feature.yaml')):
       t = open(fy).read()
       r  = re.findall(r"\{\s*id:\s*([^,]+),\s*squad:\s*([^,]+),\s*verdict:\s*([^\s},]+)", t)
       r += re.findall(r"^\s*-\s*id:\s*(\S+)\s*\n\s*squad:\s*(\S+)\s*\n\s*verdict:\s*(\S+)", t, re.M)
       declared = len(re.findall(r"^\s*-\s*(?:\{\s*)?id:", t, re.M))
       print(f"{fy}  parsed={len(r)}  declared={declared}")
       for i, s, v in r:
           print(f"    {i.strip()}  {s.strip()}  {v.strip()}")
   PY
   ```

   These are the **pre-change parser's own two regexes**, so the listing is what the old code sees, not
   an approximation of it. Measured during planning: `parsed == declared` for all five features
   (1/1, 4/4, 19/19, 15/15, 1/1), so **no run is being dropped today and SC-13's "identical" holds as
   written.** If a future re-run shows `parsed < declared`, SC-13 needs amending before T-07 lands —
   it and SC-01 would then be in direct conflict, since SC-01 asserts the conversion *recovers* runs
   the old parser drops.

verify: `python3 -c 'import yaml; print(yaml.__version__)'` → prints a version, exit 0. And
`grep -c 'baseline_exit\|baseline_violations' .harness/features/FEAT-05-pyyaml-file-parsers/feature.yaml`
→ 2 (0 at `37a8a66` — discriminating). And
`grep -c 'parsed=' .harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-baseline-run-inventory.md`
→ 5.

### T-02 — tests for `harness_yaml.py`, written first

- owner: harness-backend-dev
- change_type: logic
- traces: REQ-01, REQ-04, REQ-05, REQ-06, D-02, D-03, D-08, D-12
- depends_on: T-01
- absorbs: —

Create `.claude/skills/harness/bin/test-harness-yaml.py` — `python3`, plain `assert` plus a `main()`
returning exit 0/1, matching the shape of `.claude/skills/harness/bin/test-check-state.py`. **Nine
tests, these names:**

1. `test_duplicate_key_raises` — `load_str("id: first\nid: second\n", "t")` raises the module's
   duplicate-key error; `load_str("a: 1\nb: two\n", "t")` returns `{"a": 1, "b": "two"}`. Both
   directions, so the loader cannot pass by always raising (D-02).
2. `test_nested_duplicate_key_raises` — a repeat inside a nested mapping also raises. The regex it
   replaces saw only column-0 duplicates; this pins the strengthening.
3. `test_bare_date_scalar_stays_str` — `load_str("d: 2026-07-31\n", "t")["d"] == "2026-07-31"` and
   `isinstance(..., str)`. Asserts the timestamp-resolver strip (D-08).
4. `test_int_and_bool_resolvers_are_not_stripped` — `cycles_used: 3` → `int`, `schema_version: 2` →
   `int`, `x: yes` → `True`. The negative half of D-08: the strip is surgical, not blanket.
5. `test_manifest_domains_matches_the_regex_walk_on_the_real_manifest` — call
   `manifest_domains(".harness/team-config.yaml", a)` for each of `harness-backend-dev`,
   `harness-dev-ops`, `harness-pm`, `harness-documentor` and assert the returned `(mine, shared)`
   tuples equal the sets the pre-change `collect()` logic produced, inlined into the test as a fixture.
   This is the D-03 equivalence proof and it must be written **before** either hook is touched.
6. `test_manifest_domains_excludes_non_canonical_read_true` — a temp manifest with `read: yes` and
   `read: True` entries: both land in neither `mine`; the same entries written `read: no` do land in
   `mine`. Pins D-13's tightening as intended behaviour, not an accident.
7. `test_bootstrap_marker_lifecycle` — with a `tempfile.TemporaryDirectory()` project root and a forced
   "yaml missing" state: first call writes the marker and grants; a second call with the **same**
   resolved identity grants **silently** and blocks nothing; a call with a **different** identity
   blocks; a call whose marker write fails (read-only dir) blocks. Four cases, four asserts (E3).
8. `test_marker_self_unlinks_when_yaml_imports` — with a marker present and `yaml` importable, calling
   `require_or_die()` removes the marker and returns normally. Then assert that a bare
   `python3 -c 'import harness_yaml'` (via `subprocess`) with a marker present leaves the marker **on
   disk** — the module's only import-time behaviour is the single `import yaml`.
9. `test_exactly_one_guarded_import_in_the_tree` — grep `.claude/skills/harness/bin/*.py` and `*.sh`
   for `except ImportError` and assert exactly one hit, in `harness_yaml.py`. This is D-12's receipt as
   a standing test, so SC-04 cannot silently rot after ship.

Then, as a numbered step of this task and not a footnote: **edit
`.claude/skills/harness/bin/run-unit-tests.sh` and add `"test-harness-yaml.py"` to the `SCRIPTS`
array.** The runner's drift detector exits **2** on any `test-*.py` under `bin/` absent from that list,
so skipping this makes the whole unit gate exit 2 rather than run.

verify: `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh; echo $?` → output
contains `FAIL test-harness-yaml.py`, contains no `MISCONFIGURED` line, and the exit code is **1** — the
red state. Exit 2 means the `SCRIPTS` edit was missed; exit 0 means the tests test nothing.

### T-03 — the shared module `harness_yaml.py`

- owner: harness-backend-dev
- change_type: logic
- traces: REQ-01, REQ-03, REQ-04, REQ-05, REQ-06, D-02, D-03, D-07, D-08, D-12
- depends_on: T-02
- absorbs: —

Create `.claude/skills/harness/bin/harness_yaml.py`. Python stdlib plus PyYAML. **Its only import-time
behaviour is the single `import yaml` inside the single `try`** — no marker read, no marker write, no
file I/O, no module-level mutable state, no caching. Lifetime is per-process; every caller is a
short-lived hook or CLI script.

Public interface, exactly these six names:

- `INSTALL_COMMAND` — the two-line string from D-07, with the `[reasoned, unverified]` note on the
  older-pip ordering in a comment beside it. **One source of truth**, shared with `harness-init`'s gate
  text (T-11 quotes this constant's content, it does not re-author it).
- `load_file(path)` — read and parse a `.yaml` file with the module's loader. Raises the module's own
  parse error, carrying the path, on malformed YAML.
- `load_str(text, where)` — the same for in-memory content; `where` is a label used in the error.
- `manifest_domains(manifest_path, agent) -> (mine, shared)` — D-03. Walks the parsed manifest and
  returns two lists of path globs: `mine` = paths under the entry whose `name:` equals `agent`, **minus**
  any entry whose `read` key resolves truthy (D-13); `shared` = paths under the `shared:` section.
  Behaviour must equal the pre-change `collect()` for every agent in this repo's manifest — T-02 test 5
  is that proof. **Every returned glob is `str()`-coerced** (D-08).
- `require_or_die()` — for `check-state.sh` and the plain `.py` scripts. If `yaml` imported, unlink the
  bootstrap marker if it exists and return. If not, print the missing-PyYAML message and
  `INSTALL_COMMAND` to stderr and exit non-zero. **No bootstrap escape** (D-06).
- `require_or_bootstrap(root)` — for the two hooks. If `yaml` imported, unlink the marker if present
  and return. If not, resolve the session identity and apply the four cases below.

**The loader** is one `SafeLoader` subclass with two overrides (dev-ops probe 5c/5d confirm both work
and combine): `yaml_implicit_resolvers` rebuilt without `tag:yaml.org,2002:timestamp` (D-08), and
`construct_mapping` raising `ConstructorError` on a repeated key (D-02). Nothing else is stripped.

**Session identity, resolved in this order and nowhere else:** payload `session_id` →
`transcript_path` filename stem → `CLAUDE_CODE_SESSION_ID` → `CLAUDE_CODE_BRIDGE_SESSION_ID`. **If none
resolves, fail CLOSED and print `INSTALL_COMMAND`.** The asymmetry is the whole design: an unbounded
grant is a permanent silent bypass and is unrecoverable; a hard block is loud and the user fixes it
with one command outside the tool. Never grant an escape you cannot bound.

**Marker: `<root>/.harness/.pyyaml-bootstrap`, one file shared by both hooks** — two markers means two
install messages per session and two lifecycles to keep in sync. Four cases, and they are the whole
lifecycle:

| Marker state | Action |
|---|---|
| absent | write the marker recording the resolved identity, print `INSTALL_COMMAND` on **stderr**, **allow** (SC-08) |
| present, identity **matches** | **allow silently** — SC-08 requires *no* write blocked in that session, so a "used ever" latch is wrong |
| present, identity **does not match** | **block** (SC-09). Expiry is **by construction**: a new session's id can never match a recorded one |
| marker write **fails** (read-only checkout) | **block**. An escape that cannot be bounded is not granted |

**Honest limit, recorded not hidden:** `harness-dev-ops` is exempt from `bash-write-guard.sh` entirely
(`:33`), so it can delete the marker and re-trigger the escape. The escape expires by construction on
the honest path; a deliberate deletion sits inside the trust boundary DEC-85 already accepts.

verify: `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh; echo $?` → exit **0**,
output contains `PASS test-harness-yaml.py` and no `MISCONFIGURED` line.

### T-04 — convert `upgrade-config.py`

- owner: harness-backend-dev
- change_type: logic
- traces: REQ-01, D-04, D-08
- depends_on: T-03
- absorbs: —

Rewrite `yaml_names` (`:91`) and `yaml_version` (`:98`) in
`.claude/skills/harness/bin/upgrade-config.py` to take a **path** and use
`harness_yaml.load_file`, returning the agent `name` values and the `schema_version` from the parsed
mapping. Both are reads of `team-config.yaml`; both convert. `python3 script.py` already puts the
script's directory on `sys.path[0]`, so a plain `import harness_yaml` works with no `PYTHONPATH`
change. Call `harness_yaml.require_or_die()` once at entry. Apply D-08: `str()` every returned name.
Delete the docstring at `:85-87` that reads "no YAML library exists here" — it is now false, and a
stale comment asserting the opposite of the code is how the next author re-hand-rolls one. Update the
two call sites at `:176-177`.

Create `.claude/skills/harness/bin/test-upgrade-config.py` with three tests: names extracted from the
real `.harness/team-config.yaml` equal the pre-change list (inlined as a fixture); `schema_version`
returns an `int`; a manifest whose `name:` value is all digits is returned as `str`, not `int` (D-08).
**Add `"test-upgrade-config.py"` to `run-unit-tests.sh`'s `SCRIPTS` array** — same exit-2 drift trap
as T-02.

verify: `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh; echo $?` → exit 0 with
`PASS test-upgrade-config.py`; and
`grep -cE 're\.(search|findall|match|finditer|sub|split|compile)' .claude/skills/harness/bin/upgrade-config.py`
→ **0** (2 at `37a8a66` — discriminating).

### T-05 — record that `cost-report.py` needs no conversion

- owner: harness-backend-dev
- change_type: docs
- traces: REQ-01, D-04
- depends_on: T-03
- absorbs: —

`cost-report.py` is named in REQ-01, and the honest finding is that it **reads no YAML**. Do not invent
a conversion. Instead:

1. Add a short comment above `patch_state_cost` (`.claude/skills/harness/bin/cost-report.py:170`)
   stating that `:189`'s `^cost:` match is a **line-preserving writer**, that it deliberately does not
   round-trip through a YAML parser because `safe_dump` would strip the file's comments and reorder its
   keys, and that `check-domain.sh:275-298` validates `state.yaml` by top-level key on Write — citing
   D-04 by name so a future sweep does not "finish the job".
2. Add the same one-line note beside `:112`, marking it a path-munge, not YAML.
3. Do **not** add `import harness_yaml` — the script parses no YAML, so a `require_or_die()` here would
   make PyYAML a prerequisite of cost reporting for no benefit.

verify: `grep -c 'D-04' .claude/skills/harness/bin/cost-report.py` → at least 2 (0 at `37a8a66` —
discriminating); and `grep -n 'yaml.safe_load\|import yaml\|import harness_yaml'
.claude/skills/harness/bin/cost-report.py` → no output.

### T-06 — convert `gh-sync.py`'s `load_recorded`, and audit `test-gh-sync.py`'s labels

- owner: harness-backend-dev
- change_type: logic
- traces: REQ-01, REQ-06, D-04, D-08
- depends_on: T-03
- absorbs: #12

**Part A — the conversion.** Rewrite `load_recorded` (`.claude/skills/harness/bin/gh-sync.py:178-195`)
to `harness_yaml.load_file` the feature's `feature.yaml` and read the `github:` mapping from the parsed
dict, replacing the six regexes at `:181 184 186 188 190 193`. Preserve the exact return shape:
`{"milestone": int|None, "parent": int|None, "parent_origin": str|None, "attached": [str],
"issues": {str: int}}`. Apply D-08 — `attached` entries and `issues` keys are identifiers, so `str()`
them; `milestone`/`parent`/`issues` values are `int()`d, and a `parent: none` resolves to the **string**
`"none"` under PyYAML (lowercase `none` is not in the null resolver), so it must be normalised to `None`
exactly as the old `^\s*parent:\s*(\d+)` non-match did. Update the section comment at `:176` — it
currently reads "text ops — no yaml dependency". Call `require_or_die()` at entry. **Leave
`save_recorded` (`:200`) alone** — D-04: it is a writer, and its `re.sub` stays.

**Part B — SC-11, issue #12.** Read every `check(...)` label in
`.claude/skills/harness/bin/test-gh-sync.py` and confirm each invokes the subcommand its label names.
Issue #12 is filed **unverified**; confirm or refute it. If a label misdescribes its invocation, fix the
label (or the invocation, whichever is wrong) and say which. If every label is accurate, record that as
the refutation with the line numbers checked — a refutation is a valid outcome and closes #12 as
`not planned`, not as fixed.

**Part C — tests.** Extend `.claude/skills/harness/bin/test-gh-sync.py` with two tests: a `feature.yaml`
whose `github:` block carries a **trailing `#` comment** on `parent:` and `milestone:` is read
correctly (the #11 defect class, in this file); and a `feature.yaml` with **no** `github:` block returns
the all-`None` default rather than raising.

verify: `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh; echo $?` → exit 0 with
`PASS test-gh-sync.py`; and
`grep -nE 're\.(search|findall|match|finditer)' .claude/skills/harness/bin/gh-sync.py` → exactly the 5
markdown lines `128 135 153 157 159` and nothing in the `176-196` range (6 hits in that range at
`37a8a66` — discriminating).

### T-07 — convert `check-state.sh`, closing issue #11

- owner: harness-backend-dev
- change_type: logic
- traces: REQ-01, REQ-02, REQ-07, D-05, D-08
- depends_on: T-03
- absorbs: #11

`.claude/skills/harness/bin/check-state.sh` is a bash wrapper around one Python heredoc (`:17`). It is
the **only** in-scope script lacking a `_selfdir`: it derives everything from `root` (`:14-15`), which
can be wrong. Give it a `_selfdir` computed from `BASH_SOURCE` exactly as `check-domain.sh:60-61` and
`bash-write-guard.sh:38-39` do, and prepend it to `PYTHONPATH` on the existing `python3` invocation:

```
PYTHONPATH="$_selfdir${PYTHONPATH:+:$PYTHONPATH}" python3 - "$root" <<'PY'
```

**Preserve an inherited `PYTHONPATH`; never overwrite it.** SC-08's harness shadows `yaml` via
`PYTHONPATH`, and a flat assignment destroys that test. Call `harness_yaml.require_or_die()` at the top
of the heredoc.

Convert exactly the **10** calls the census names: `98` (`val()` on `feature.yaml`), `108` + `109`
(the runs list — **this pair is issue #11**), `237` (`phase:`), `293` `297` `316` (`state.yaml`
`status:`/`cost:`/`host:`), `394` `398` `399` (the `feature.yaml` `github:` block). Replace `val(k)`
with a lookup on the parsed mapping. Replace the two `runs` regexes with `data.get("runs") or []` —
**both** inline `{ id: …, squad: …, verdict: … }` and block form are the same parsed list to PyYAML, so
the dual-regex hack disappears rather than being ported.

**Do not touch the 7 survivors** — `46 47 50 76 78 89` parse markdown, and `302` is the BRIEF-exempted
`CHECKPOINT_KEYS` scan (D-05). **Do not fix `:113`'s `review_sha: none` fail-open** — D-09 defers it
deliberately, and fixing it here destroys SC-02's and SC-13's ability to prove the conversion was
faithful.

Extend `.claude/skills/harness/bin/test-check-state.py` with three tests:
1. `test_run_with_trailing_comment_on_id_is_read` — a `feature.yaml` fixture whose run entry carries
   `id: 2026-08-02-01-product  # note` **and** a second whose `squad: validator  # note`. Assert both
   runs appear in the parsed run set and that INV-6/7/8 are evaluated against them. Assert the
   **identical fixture** drops the run under the pre-change regex, inlined in the test as a literal, so
   the test shows the defect and the fix side by side (SC-01).
2. `test_cycles_used_as_int_does_not_raise` — `cycles_used: 3` parses to `int` and INV-7 evaluates
   without an `AttributeError` from `.isdigit()` (SC-10, `check-state.sh:120`).
3. `test_date_shaped_run_id_stays_str` — a run whose `id:` is the bare scalar `2026-07-31` joins to its
   run directory as `"2026-07-31"`, not a `datetime.date` (SC-10, D-08).

verify: `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh` → exit 0 with
`PASS test-check-state.py`; then `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/check-state.sh;
echo $?` → the exit code and violation count recorded at T-01 step 2, unchanged (SC-02); then produce
the **post-change** run inventory — the same per-feature `id / squad / verdict` listing, emitted from
the converted parser — and `diff` it against
`.harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-baseline-run-inventory.md`'s indented run
rows. **Zero differing run rows** (SC-13). Both listings are then real artifacts the reviewer cites,
rather than something improvised at review time.

### T-08 — the typed-value consumer sweep

- owner: harness-backend-dev
- change_type: logic
- traces: REQ-06, D-08
- depends_on: T-04, T-05, T-06, T-07
- absorbs: —

**Its own task with its own verify, deliberately — a reminder repeated inside six conversion tasks is
what lets a consumer be missed.** Nothing inside a conversion task forces a walk of *every* consumer of
a parsed value; this task is that walk, and it runs after the four non-hook conversions and **before**
the hooks.

Walk **every** consumer of a value returned by `harness_yaml.load_file` / `load_str` /
`manifest_domains` across the three converted non-hook scripts: `check-state.sh`, `gh-sync.py`,
`upgrade-config.py`. (`cost-report.py` converts nothing — D-04 — so it has no parsed consumers.)
**The two hooks are NOT in this task's scope and are not deferred to a reminder inside it:** they do not
exist in converted form yet, and their sweep is **T-17**, which runs after T-15 and extends this same
receipt. For each consumer here, classify the value's use and apply the rule:

**Any value used as a path component, an identifier, or a dict key gets `str()` at the consumer.**
Values used as numbers (`schema_version`, `cycles_used`, `milestone`, issue numbers) stay typed — D-08
is explicit that the int/bool/float resolvers are **not** stripped, because those consumers genuinely
want ints.

Three named regressions must each be shown handled, by `file:line`:
- `check-state.sh:120` — `.isdigit()` on `cycles_used`, which is now an `int`.
- a run `id` that is a bare date-shaped scalar, joined into a directory path.
- an all-digit abbreviated commit SHA in `review_sha`/`pinned_sha`/`base_sha`/`head_sha`/`tip_sha`,
  which YAML 1.1 resolves to `int` and which is then compared or printed as a string.

Write the walk out as a table in
`.harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-harness-backend-dev-typed-value-sweep.md`
— one row per consumer: `file:line`, the key, the parsed type, the use class, the action taken. That
receipt is SC-10's inspection evidence and the reviewer's checklist.

verify: `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh` → exit 0; and a
`python3 - <<'PY'` script asserting **two mechanically decidable** properties — (a) walking every
`feature.yaml` and `state.yaml` in this repo through `harness_yaml.load_file`, **no** value anywhere in
any parsed tree is a `datetime.date` or `datetime.datetime` (this is the resolver strip, provable from
the data alone); and (b) for **every** agent name in `.harness/team-config.yaml`, every glob in both
lists returned by `manifest_domains` satisfies `isinstance(g, str)`. Prints `SWEEP OK`, exit 0.
"Used as a path component" is a property of the *consumer*, not of the file, so it is **not** asserted
by this command — the receipt table below is where that judgement is recorded and reviewed. And
`grep -c '^| ' .harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-harness-backend-dev-typed-value-sweep.md`
→ at least 10 rows — the **non-hook** total. T-17 raises the required count to the final total.

### T-09 — probe the hook's session identity, BEFORE the fail-closed hooks land

- owner: harness-backend-dev
- change_type: scaffolding
- traces: REQ-05, D-06
- depends_on: T-03
- absorbs: —

**eng-lead Q1: no session identifier is confirmed to reach a PreToolUse hook subprocess.**
`CLAUDE_CODE_SESSION_ID` was observed in a **Bash-tool** subprocess, not a hook one, and the raw payload
key set was never captured. `require_or_bootstrap`'s whole design rests on one of the four chain
entries resolving.

Add **one temporary guarded block** immediately after
`.claude/skills/harness/bin/check-domain.sh:242` (the `sys.exit(0)` closing the `HOOK_PAYLOAD`
try/except, so `d` is parsed and `root` — `sys.argv[2]`, `:238` — is in scope), so there is **no stdin
plumbing and no `settings.json` edit**. The probe **appends to a file; it does not print to stderr.**
A PreToolUse hook is a subprocess of Claude Code, not of the writing agent, so the agent cannot put a
`2>` redirect on it — and the task's own `verify:` requires the observation to land in a receipt file
regardless, so a file append strictly dominates. Write it exactly like this:

```python
try:
    _pp = os.path.join(root, ".harness/features/FEAT-05-pyyaml-file-parsers/notes/"
                             "receipt-harness-backend-dev-hook-identity-probe.md")
    with open(_pp, "a") as _pf:
        _pf.write("- payload %s | env %s\n" % (
            sorted(d.keys()), sorted(k for k in os.environ if k.startswith("CLAUDE"))))
except Exception:
    pass
```

Three constraints on that block, each load-bearing:

1. **The `try/except Exception: pass` is not optional.** `print` to stderr cannot raise; `open(..., "a")`
   can (missing dir, read-only tree). This block sits inside the **state-shape gate** — the same Python
   block that renders the DEC-156 duplicate-key denial at `:285-287`. An uncaught exception here aborts
   the block and the duplicate-key check silently stops firing for the life of the probe. A probe that
   fail-opens the write gate is worse than no probe.
2. **Path resolved from `root`, absolutely, in mode `"a"`.** The hook subprocess's cwd is not guaranteed
   to be the project root, so a relative path lands somewhere unpredictable; the probe fires once per
   governed Write, so it appends. The path is inside `harness-backend-dev`'s receipt grant
   (`team-config.yaml:158`, `receipt-harness-backend-dev-*.md`) and **is the receipt itself** — there is
   no separate temporary capture file to clean up. The `notes/` directory already exists (verified), so
   the `except` should never fire; if it does, the probe writes nothing and the `RESOLVED VIA:` half of
   the `verify:` is what catches the silence. Do not read an empty file as "no identifier reached the
   hook" — that is the ESCALATE branch below and it needs a successful append to be claimed.
3. **The literal text `sorted(d.keys())` must appear in the block.** The cleanup half of this task's
   `verify:` greps for exactly that string; rewrite it another way and the cleanup check stops
   discriminating.

Trigger one real Write from a governed agent, **read the appended lines back out of that file**, then
**remove the probe block**. Then annotate the same file: the observed payload keys, the observed
`CLAUDE_*` environment variables, and **which** of the four chain entries actually resolved.

**Explicit stop-and-report branch — do not treat silence as success.** If **none** of `session_id`,
`transcript_path`, `CLAUDE_CODE_SESSION_ID`, `CLAUDE_CODE_BRIDGE_SESSION_ID` reaches the hook
subprocess, then **SC-08 and REQ-05 are unsatisfiable as written**: there is no way to bound the escape
to one session, and D-03's fail-CLOSED-on-no-identity rule means the hooks would block on every
PyYAML-less machine with no escape at all. In that case **stop, do not start T-12, and return
`ESCALATE`** with the observed key set. The escape needs redesign and that is a plan change, not a
build decision.

verify: `grep -c 'RESOLVED VIA:'
.harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-harness-backend-dev-hook-identity-probe.md`
→ 1 (the path is named in full, not via `$_`, which is not reliable in a non-interactive shell); and
`grep -c 'sorted(d.keys())' .claude/skills/harness/bin/check-domain.sh` → **0** (the probe block is
removed). Both must hold: a receipt with the block still in the hook means the probe was not cleaned up.
The receipt is the capture file, so exactly one probe artifact may exist: `ls
.harness/features/FEAT-05-pyyaml-file-parsers/notes/ | grep -c 'hook-identity-probe'` → **1**. **Grep
the full `hook-identity-probe`, not the bare word `probe`** — measured, `notes/` already holds
`receipt-harness-dev-ops-pyyaml-probe-2026-08-02.md`, so a bare `probe` grep returns 1 today and 2 on a
correct build, and would fail the task for succeeding.

### T-10 — the gitignore chain, both files, plus the upgrade path

- owner: **main-session** — no agent domain grants `.gitignore` or `.claude/skills/harness/templates/**`; see `## Routing wall`
- change_type: config
- traces: REQ-05, D-01
- depends_on: T-03
- absorbs: —

**Must land before T-12.** The first converted hook on a PyYAML-less checkout writes the marker, and an
untracked marker dirties the tree, and a dirty tree halts the next team run with `BLOCKED`
(`merge-gitignore.sh:6-9`).

1. Add `.harness/.pyyaml-bootstrap` to `.claude/skills/harness/templates/gitignore.snippet`, inside the
   `# --- harness ---` block (currently `:1-14`), with a one-line comment naming it the one-session
   PyYAML bootstrap marker.
2. Add the **same** rule to this repo's own `/Users/molchairuangutai/GitHub/harness/.gitignore` — it is
   self-hosted, its harness rules sit at `:1-20`, and it carries no such line today. Two files, one
   rule; omitting either is the deadlock.
3. Name the upgrade path in the `harness-init` `--upgrade` section: an existing checkout that pulls this
   change must re-run `.claude/skills/harness/bin/merge-gitignore.sh .`. It is idempotent (`:44-51`),
   and it reads its rule list from the snippet, so `--check` will correctly go red on every
   already-initialised project until it is re-run.

verify: `grep -c 'pyyaml-bootstrap' .claude/skills/harness/templates/gitignore.snippet .gitignore` →
`1` for each file (0 for each at `37a8a66` — discriminating); then
`.claude/skills/harness/bin/merge-gitignore.sh . --check; echo $?` → **0**.

### T-11 — the seventh prerequisite in `harness-init`'s HARD GATE

- owner: **main-session** — no agent domain grants `.claude/skills/harness-init/SKILL.md`; see `## Routing wall`
- change_type: docs
- traces: REQ-03, D-07
- depends_on: T-03
- absorbs: —

Edit `.claude/skills/harness-init/SKILL.md`:

1. `:38` — the heading `### 1. Install the six prerequisites — HARD GATE, do this first` becomes
   **seven**. The word "six" also appears at `:3` (the frontmatter `description`), `:48`, `:49` and
   `:236`; update **all five** or the count contradicts itself in the file that enforces it.
2. Inside step 1's bash block (`:40-44`), add the probe — a **check**, not an install:
   `python3 -c 'import yaml' 2>/dev/null && echo OK || echo MISSING`.
3. Below it, add the STOP text: if it prints `MISSING`, **STOP** and print D-07's two-line install
   command verbatim. Quote the content of `harness_yaml.INSTALL_COMMAND` — do not re-author the string;
   D-07 makes the module the single source of truth, and two hand-maintained copies of an install
   command is the divergence class this feature exists to remove.
4. Add one sentence recording the division of labour eng-lead named: **the init gate is the loud, early
   check; `check-domain.sh` is the authoritative one.** The init check runs in the user's interactive
   shell, and that shell's PATH is not proven identical to the hook subprocess's — so the hook
   self-reports `MISSING` from inside its own environment on first invocation, which is the same code
   path the bootstrap escape already needs. That makes the init gate an early warning rather than a
   thing that can be silently wrong.
5. Add the T-10 step-3 `merge-gitignore.sh` re-run to the `--upgrade` section.

**Do not add `requirements.txt`, `pyproject.toml` or `package.json`** at repo root. None exists today
(verified at `37a8a66`), and adding one would be the first dependency manifest in a files-only repo,
which the BRIEF's constraints forbid. SC-07's second half guards this feature against its own
regression.

verify: `grep -c 'seven prerequisites' .claude/skills/harness-init/SKILL.md` → at least 1, and
`grep -ciw six .claude/skills/harness-init/SKILL.md` → **0** (**5** at `37a8a66`, at `:3 :38 :48 :49
:236` — discriminating, and measured with `-w` because a narrower phrase grep returns 3 and would pass
with `:3` and `:48` unfixed); and
`grep -c "import yaml" .claude/skills/harness-init/SKILL.md` → at least 1; and
`ls requirements.txt pyproject.toml package.json 2>&1 | grep -c 'No such file'` → 3.

### T-12 — convert `check-domain.sh`

- owner: harness-backend-dev
- change_type: logic
- traces: REQ-01, REQ-04, REQ-05, D-02, D-03, D-08, D-11, D-13
- depends_on: T-08, T-09, T-10
- absorbs: —

**RECOVERY NOTE — read before you start. This repo is self-hosted and this script gates every agent
write.** A bug here wedges every agent write on this machine **including the write that would fix it**,
and DEC-171 am.1 deliberately removed the fail-open that used to absorb exactly that. Before your first
edit: (a) confirm `python3 -c 'import yaml'` succeeds — T-01 is a hard prerequisite; (b) note that
`.claude/settings.json` names this script by path, so **renaming or moving it silently disables
enforcement**; (c) if you wedge yourself, the recovery is `git checkout --
.claude/skills/harness/bin/check-domain.sh` run from a **Bash** tool call — `harness-dev-ops` is exempt
from `bash-write-guard.sh` (`:33`), and `check-domain.sh` is a Write/Edit hook, so a `git checkout`
restores the file without passing through the broken gate. Write that command down before you begin.

Prepend `PYTHONPATH="$_selfdir${PYTHONPATH:+:$PYTHONPATH}"` to the **existing** heredoc invocations at
`:97` and `:235`. `_selfdir` is already computed at `:61` — no new process, no new variable.
**Preserve an inherited `PYTHONPATH`; never overwrite it** (SC-08's harness needs it, and this is not
an SC-05 violation: SC-05 forbids the *tester* setting `PYTHONPATH`; the script setting it internally
is the hook's own behaviour). Call `harness_yaml.require_or_bootstrap(root)` at the top of each
converted block.

Convert exactly **three** call sites (census):
- `:112` and `:119` — delete `collect()` (`:107-126`) entirely and call
  `harness_yaml.manifest_domains(manifest, agent)`. D-13's tightening is inherited, not re-implemented.
- `:285` — parse `content` with `harness_yaml.load_str(content, rel)` inside a `try`. **The duplicate
  detector at `:287` SURVIVES** (D-02): catch the loader's duplicate-key error and render the
  **existing** DEC-156 denial message with the offending key(s), exit 2. Catch a general parse error
  separately and **deny with a parse-error message naming the path and the YAML error** — a new
  blocking outcome, deliberate, not a regression. The `ALLOWED` set at `:281-284` becomes a check of the
  parsed mapping's top-level keys.

**Do not touch the 7 survivors** — `157 248 263 275 300 321` are rel-path routing and `182` is
`glob_to_re`'s compile (D-11). **Do not share `glob_to_re`/`matches`.** Update the comment at `:280`:
after D-02 the twins diverge by **mechanism** (raising loader vs. regex scan) while the key
**vocabulary** stays in sync — say exactly that, or the next reader syncs them back and re-opens the
fail-open.

Extend `.claude/skills/harness/bin/test-check-domain.py`: a permitted write is allowed and a forbidden
write is blocked **in one invocation context** (SC-05's paired assertion — either outcome alone is also
produced by an allow-all escape or a block-all fail-closed, and only a real manifest parse produces the
pair); a `state.yaml` Write with a duplicate top-level key is blocked with the DEC-156 message; and a
`state.yaml` Write with malformed YAML is blocked with the parse-error message.

verify: `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh` → exit 0 with
`PASS test-check-domain.py`; and
`grep -nE 're\.(search|findall|match|finditer|sub|split|compile)'
.claude/skills/harness/bin/check-domain.sh` → exactly 7 hits at `157 182 248 263 275 300 321` (10 at
`37a8a66` — discriminating).

### T-13 — merge `check-domain.sh`'s four Python launches into one

- owner: harness-backend-dev
- change_type: logic
- traces: REQ-07, D-10
- depends_on: T-12
- absorbs: —

**Regression mitigation, not polish** (D-10). Measured today at **80.63ms/iter** over the full governed
path; T-12 pushes it to roughly 105ms [estimated] on an **every-write** hook.

Merge the four launches at `.claude/skills/harness/bin/check-domain.sh:35, 74, 97, 235` into one
`python3` invocation that reads `HOOK_PAYLOAD` once and performs the agent extraction, target
extraction, domain check and state-shape gate in sequence. **Behaviour must be identical**, including
every early exit: the `agent`-absent exit at `:41`/`:48`, the non-`Write`/`Edit` exits, the exit-2
denial codes and every stderr message byte-for-byte. This task is deliberately separate from T-12 so a
reviewer can check behaviour equivalence without a restructure confounding the diff on the most
safety-critical script in the tree — do not fold any T-12 change into it, and do not change any
message text.

The RECOVERY NOTE in T-12 applies here unchanged.

verify: `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh` → exit 0 with
`PASS test-check-domain.py` (the same test file, unchanged, is the equivalence proof); and
``grep -cE "python3 -c '|python3 - .*<<'PY'" .claude/skills/harness/bin/check-domain.sh`` → **1**
(**4** at `37a8a66` — discriminating; a bare `grep -c python3` returns 5 and is wrong, because `:232`
is a comment that names the interpreter); and a 100-iteration timing of
the full governed path recorded in the task's DIGEST beside the 80.63ms baseline. **Cost is reported,
never gated (DEC-134)** — the timing is evidence, not a pass/fail threshold.

### T-14 — convert `bash-write-guard.sh`

- owner: harness-backend-dev
- change_type: logic
- traces: REQ-01, REQ-04, REQ-05, D-03, D-08, D-11, D-13
- depends_on: T-13
- absorbs: —

**RECOVERY NOTE — same wedge, different tool surface.** This hook gates `Bash`-issued writes and exists
because an agent already routed around `check-domain.sh` (DEC-151). If you break it, `harness-dev-ops`
is exempt from it entirely (`:33`), so a dev-ops-owned `git checkout --
.claude/skills/harness/bin/bash-write-guard.sh` recovers the file. Write that command down before you
begin. Do **not** land this before T-12 and T-13: converting the anti-bypass hook while the primary
hook is mid-conversion means a single mistake blocks both write surfaces at once.

Prepend `PYTHONPATH="$_selfdir${PYTHONPATH:+:$PYTHONPATH}"` to the existing heredoc invocations at
`:24` and `:48`. `_selfdir` is already computed at `:39` — **note it is computed AFTER the `:24`
launch**, so either move the `_self`/`_selfdir` computation above `:24` or leave `:24`'s launch
unconverted (it only reads `agent_type` from JSON and parses no YAML; the census does not list it).
Call `harness_yaml.require_or_bootstrap(root)` at the top of the `:48` block. **Preserve an inherited
`PYTHONPATH`.**

Convert exactly **two** call sites (census): `:252` and `:257` — delete the inline domain walk
(`:248-263`) and call `harness_yaml.manifest_domains(manifest, agent)`. This is the security-relevant
half of D-03: after this task both hooks compute domains from the same function, and the walks cannot
diverge.

**Do not touch the 5 survivors** — `112` (heredoc scan), `185` (redirect scan), `278`
(`glob_to_re` compile, D-11), `298` and `306` (path routing).

Extend `.claude/skills/harness/bin/test-bash-write-guard.py` with SC-06's paired assertion: a permitted
`bash`-issued write is **allowed** and a forbidden one is **blocked**, in the hook's own invocation
context. Both are required — either alone is also produced by an allow-all escape or a block-all
fail-closed.

verify: `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh` → exit 0 with
`PASS test-bash-write-guard.py`; and
`grep -nE 're\.(search|findall|match|finditer|sub|split|compile)'
.claude/skills/harness/bin/bash-write-guard.sh` → exactly 5 hits at `112 185 278 298 306` (7 at
`37a8a66` — discriminating).

### T-15 — merge `bash-write-guard.sh`'s two Python launches into one

- owner: harness-backend-dev
- change_type: logic
- traces: REQ-07, D-10
- depends_on: T-14
- absorbs: —

The same 2-to-1 merge, at lower priority (~17ms). Merge `:24` and `:48` into one invocation reading
`HOOK_PAYLOAD` once. Behaviour identical, including the `harness-dev-ops` exemption at `:33`, the
`harness-*` prefix filter and every exit-2 message. The T-14 RECOVERY NOTE applies unchanged.

verify: `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh` → exit 0 with
`PASS test-bash-write-guard.py` (the same unchanged test file is the equivalence proof); and
``grep -cE "python3 -c '|python3 - .*<<'PY'" .claude/skills/harness/bin/bash-write-guard.sh`` → **1**
(**2** at `37a8a66` — discriminating; a bare `grep -c 'python3 '` returns 3, because `:98` is a
docstring line naming the interpreter, and `:145` lists it as a data feeder).

### T-16 — the SC-09 UAT script, and the D-09 follow-up issue

- owner: harness-pm
- change_type: docs
- traces: REQ-05, D-09
- depends_on: T-14
- absorbs: —

**Ship is gated on this.** `.harness/harness.json:244` sets `"uat":
"blocking_when_uat_criteria_exist"`, and SC-09 is `verify: uat`. Naming the script now means the gate
is not discovered at ship.

Write `.harness/features/FEAT-05-pyyaml-file-parsers/notes/uat-bootstrap-escape-expiry.md`, per the
`harness-uat` protocol, with these numbered steps the user executes by hand:

1. In a scratch clone (never the working checkout), make `yaml` unimportable from the resolved
   `python3` — a directory on `PYTHONPATH` containing a `yaml.py` that raises `ImportError` is the
   shape SC-08's harness already uses, and the BRIEF's note at `:131-135` says explicitly that this is
   not an SC-05 violation.
2. Start a **new** Claude Code session in that clone. Trigger one agent Write. **Expected:** the write
   is **permitted**, the two-line install command appears on stderr, and `.harness/.pyyaml-bootstrap`
   exists.
3. Trigger a **second** Write in the **same** session. **Expected:** also permitted, **silently** — no
   second install message. (A "used ever" latch would fail here, and it would also fail SC-08.)
4. **Exit and start a genuinely new session** in the same clone, PyYAML still absent. Trigger a Write.
   **Expected: BLOCKED**, with the install command printed. This is SC-09 and it is the only step no
   test kind can create honestly.
5. Install PyYAML, trigger one Write. **Expected:** permitted, and `.harness/.pyyaml-bootstrap` is
   **gone** — the marker self-unlinks once `import yaml` succeeds.
6. `git status` in the clone. **Expected:** clean at every step above — D-01's ignore rule holding.

Mark the script `status: ready`. **Do not mark it passed** — only the user runs it, and SC-09 stays
`not_met` until they do.

Then file the D-09 follow-up: `gh issue create` titled "check-state.sh:113 — `review_sha: none` is a
truthy string, so INV-6 passes on an unpinned feature", body citing `check-state.sh:113` and
`FEAT-05/feature.yaml:6`, and recording that FEAT-05 deferred it deliberately to keep SC-02/SC-13 able
to prove the conversion faithful.

verify: with `U=.harness/features/FEAT-05-pyyaml-file-parsers/notes/uat-bootstrap-escape-expiry.md`,
`grep -c 'status: ready' "$U"` → 1 and `grep -cE '^[0-9]\.' "$U"` → at least 6 (the path is bound to a
variable rather than relying on `$_`, which is not reliable in a non-interactive shell); and
`gh issue list --repo mruangutai/harness --state open --search 'review_sha'` → at least 1 hit.

### T-17 — the typed-value sweep, second half: the two hooks

- owner: harness-backend-dev
- change_type: logic
- traces: REQ-06, D-08
- depends_on: T-15
- absorbs: —

**This task exists because T-08 could not cover the hooks and a parenthetical reminder inside T-08 is
not a schedule.** T-08 ran before `check-domain.sh` and `bash-write-guard.sh` were converted, so their
parsed-value consumers were not walkable then. They are now. Without this task the two hooks' consumers
are **never** swept — and they are the two scripts where a typed-value surprise blocks or permits a
write rather than printing a wrong number.

Run **exactly the T-08 walk**, same rule, over the converted `.claude/skills/harness/bin/check-domain.sh`
and `.claude/skills/harness/bin/bash-write-guard.sh`: every consumer of a value returned by
`harness_yaml.load_str` / `load_file` / `manifest_domains`, classified by use, with
**`str()` at the consumer for any value used as a path component, an identifier, or a dict key**;
numeric consumers stay typed (D-08).

Two hook-specific regressions must each be shown handled, by `file:line`:
- every glob returned by `manifest_domains` before it reaches `glob_to_re`/`matches` — a non-`str`
  glob raises inside `re.escape`/`re.compile` and, in a fail-closed hook, that is a **block on every
  write**, not a wrong answer;
- every top-level key of a parsed `state.yaml` compared against the `ALLOWED` set at
  `check-domain.sh:281-284` — a key that YAML resolves to `True`/`int` (e.g. `on:`, `no:`) is no longer
  the string the set holds, and would be reported as an unknown key.

**Extend the same receipt** —
`.harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-harness-backend-dev-typed-value-sweep.md`
— appending the hook rows under a `## Hooks (T-17)` heading rather than starting a second file. One
receipt is SC-10's single inspection evidence; two would let a reviewer cite the half that looks best.

**One new test, because `change_type: logic` maps to `always: [unit]` and this task must not discharge
that with a re-run of an already-green assertion.** Add to `.claude/skills/harness/bin/test-check-domain.py`:
`test_yaml_truthy_top_level_key_is_reported_by_name` — a `state.yaml` Write whose top-level key is
`on:` (YAML 1.1 resolves it to `True`, not the string `"on"`) is denied as an **unknown key, named in
the message**, and does not raise inside the `ALLOWED` comparison at `check-domain.sh:281-284`. Only
the hook-side `str()` coercion this task applies makes it pass. No `SCRIPTS` edit is needed — the file
is already in `run-unit-tests.sh`.

**Do not re-run T-08's sweep script as this task's evidence.** Both properties it asserts (no
`datetime` in any parsed tree; every `manifest_domains` glob is `str`) are module-level and already
green after T-08, so it passes whether or not the hooks were touched — non-discriminating here, by the
same standard applied throughout this plan.

verify: `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh` → exit 0 with
`PASS test-check-domain.py`, including
`test_yaml_truthy_top_level_key_is_reported_by_name` (absent and therefore failing before this task —
discriminating); and
`grep -c '^| ' .harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-harness-backend-dev-typed-value-sweep.md`
→ **at least 14** rows — the **final** total, at least 4 above T-08's non-hook 10, so a receipt left
unextended fails here (discriminating); and
`grep -c '## Hooks (T-17)' .harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-harness-backend-dev-typed-value-sweep.md`
→ 1.

## Ordering — the dependency spine, encoded in `depends_on`, restated here for the orchestrator

```
T-01 (PyYAML on the hook interpreter, main-session)
 └─ T-02 (helper tests, red) ─ T-03 (harness_yaml.py, green)
      ├─ T-04 upgrade-config    ┐
      ├─ T-05 cost-report note  ├─ the four non-hook steps, parallel-safe
      ├─ T-06 gh-sync (+#12)    │
      ├─ T-07 check-state (#11) ┘
      ├─ T-09 identity probe  ── main-session-adjacent, must finish before T-12
      ├─ T-10 gitignore chain (main-session), must finish before T-12
      └─ T-11 harness-init gate (main-session)
 └─ T-08 (typed-value sweep, non-hook half) ← after T-04..T-07, before the hooks
      └─ T-12 check-domain ─ T-13 consolidate ─ T-14 bash-write-guard ─ T-15 consolidate
           ├─ T-16 UAT script + D-09 issue          (depends_on T-14)
           └─ T-17 typed-value sweep, hook half     (depends_on T-15, same receipt as T-08)
```

**Four orderings are load-bearing and a builder may not reorder them:**

1. **T-01 before everything.** PyYAML is not importable from this machine's resolved `python3` today
   (verified). A converted hook landing first wedges the build machine.
2. **The hooks are LAST.** T-12 and T-14 gate every agent write; a bug in either wedges the write that
   would fix it, and DEC-171 am.1 removed the fail-open. Converting the four non-hook scripts first
   means the shared module is proven by four callers before it gates anything.
3. **T-09 and T-10 before T-12.** T-09 can invalidate the escape design outright (its stop-and-report
   branch), and T-10 prevents the marker from deadlocking the next team run on a dirty tree.

4. **T-17 after T-15, and the sweep is not finished until it lands.** The typed-value walk is split
   across two tasks only because the hooks do not exist in converted form when T-08 runs. Skipping
   T-17 leaves the two write gates as the only unswept consumers in the feature — the inverse of the
   risk ordering everywhere else in this plan.

T-04, T-05, T-06 and T-07 all depend only on T-03 and touch disjoint files — they are parallel-safe.
T-08 depends on all four.

**Ownership serialization.** `.claude/skills/harness/bin/**` is granted to **both** `harness-backend-dev`
(`team-config.yaml:155`) and `harness-dev-ops` (`:197`), so the domain hook cannot keep two writers
disjoint there. eng-lead flagged the split as a divergence hazard on exactly the files this feature
shares. **Route the helper and all six conversions to ONE specialist — `harness-backend-dev` — and do
not split them.** The three main-session tasks touch different files (`.gitignore`,
`templates/gitignore.snippet`, `harness-init/SKILL.md`), so no shared write arises.

## Routing wall — the orchestrator needs this before it dispatches

**Two kinds of routing problem, and they are not the same.** *(a) Three paths have no agent owner at
all* — verified against `.harness/team-config.yaml`, nothing in the manifest grants `.gitignore`,
`.claude/skills/harness/templates/**`, or `.claude/skills/harness-init/SKILL.md`. `harness-dev-ops`
holds `.github/**`, `Dockerfile`, `.harness/harness.json`, `.claude/skills/harness/bin/**`,
`stack.md`, its receipts, expertise and observations (`:194-202`) — **and none of those three paths**.
This is the same wall FEAT-03 hit at its Q13 and FEAT-04 hit at its T-09/T-10. *(b) T-01 writes two
paths that ARE owned — by the orchestrator, not by main-session.* That is a wrong-tier row, not an
unowned one, and the earlier "none" in this table hid it.

| Task | Paths, and who may write them |
|---|---|
| T-01 | step 1 `pip install` — a machine action, no repo write, **main-session**. step 2 `.harness/features/FEAT-05-pyyaml-file-parsers/feature.yaml` and step 3 `.harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-baseline-run-inventory.md` — both **owned by the orchestrator** under its blanket `.harness/features/**` grant (`team-config.yaml:28`), so **the orchestrator records them**, not main-session |
| T-10 | `.gitignore` · `.claude/skills/harness/templates/gitignore.snippet` — **no owner**, main-session |
| T-11 | `.claude/skills/harness-init/SKILL.md` — **no owner**, main-session |

**On the T-01 receipt filename:** `receipt-baseline-run-inventory.md` deliberately matches **no**
`receipt-harness-<agent>-*` pattern, because no agent writes it. The orchestrator's grant is a blanket
path, not a receipt pattern, so the name is legal as written — **do not re-file it** under a
specialist's prefix, which would misattribute a pre-build measurement to a builder.

**Consequence the orchestrator must plan around: SC-07 and D-01 cannot go green until the main session
acts, and T-10 sits INSIDE the spine — it must complete before T-12.** Do not schedule the
main-session steps as a post-build tidy-up; T-12 is blocked on T-10.

## Verification gaps carried forward from the BRIEF

- **SC-09 rests on `uat` and nothing else.** No test kind in `harness.json` can honestly create a
  genuinely new session on a PyYAML-less machine. Until the user runs T-16's script, the **expiry** of
  the bootstrap escape is not proven; SC-08 proves only that the first session is permissive.
  `harness.json:244` makes this **ship-blocking**.
- The `cmd: null` kinds (`functional`, `integration`, `component`, `ui`, `eval`, `typecheck`) do not
  bind here: this feature's surface is `.claude/skills/harness/bin/*`, which the `unit` kind's detect
  glob matches directly (`.claude/skills/harness/bin/test-*.py`) and whose runner exists.

## Test matrix note

Per `.harness/harness.json` `test_matrix`: `logic` → `always: [unit]`, and `config`/`docs`/`scaffolding`
→ `always: []`. Eleven of the seventeen tasks are `logic` and each carries unit tests, which is why the
test names are specified in the tasks rather than left to the implementer. `unit`'s runner is
`.claude/skills/harness/bin/run-unit-tests.sh` and its detect glob covers `bin/test-*.py`, so every test
this feature writes is inside the gate. **The `SCRIPTS` array in that runner must be edited in the same
task that adds a test file** — its drift detector exits **2**, which reads as a broken gate rather than
a failing test.

## Budget

`per_feature_usd` 120, unraised. Two runs already spent (~$48, relayed — not a figure I measured), so
the build phase inherits roughly $72. Seventeen tasks is a large list for that remainder; the four
parallel-safe non-hook conversions (T-04..T-07) are where a squad can compress it. **Cost is reported,
never gated (DEC-134).**

## Glossary

`.harness/codebase/glossary.md` does not exist at `37a8a66`. This feature pins two terms worth keeping —
the **bootstrap escape** (a one-session-wide permit granted by a hook when PyYAML is absent, bounded by
a recorded session identity) and the **census** (the file:line classification of every regex call in a
converted script, the reviewer's answer key for an absence criterion). Both are defined in this plan at
their point of use, and creating a two-entry glossary is worse than an absent one. Recorded so a
reviewer does not read the omission as an oversight.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-03
note: |
  Signed together with BRIEF.md in one bundled signature; that note carries the Q1/Q2/Q3
  amendments and the Q7 and budget rulings, and they bind this plan too.

  Load-bearing for the build, and NOT to be re-litigated by a member: T-10 and T-11 are
  MAIN-SESSION steps. No agent holds `.gitignore`, `templates/**` or `harness-init/SKILL.md`.
  An agent that finds itself blocked on one of those paths must ESCALATE, never work around it
  (`harness-digest-dev`'s boundary rule).

  D-06 stands: `check-state.sh` gets no bootstrap escape, deliberately, with the consequence
  written into the plan.

  Q4 is UNRESOLVED and is accepted as such: session identity inside a `PreToolUse` hook
  subprocess is unconfirmed. T-09 probes it in-band and carries a stop-and-report ESCALATE
  branch. If nothing resolves, SC-08 and REQ-05 are unsatisfiable as written and the escape
  needs redesign — that is a return to the user, not a member's improvisation.

  Q6 is a HARNESS DEFECT the build must not trip over: the `SubagentStop` validator resolves
  `${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/validate-digest.py`, which in a worktree is
  the MAIN CHECKOUT's copy, not this one. Verified: main has 0 `GATE_FIELDS`, this worktree has
  2. So every digest produced in this worktree is judged by the main checkout's rules, and
  DEC-173's widened schema is NOT in force for agents until this branch merges. Do not diagnose
  a rejected-but-correct digest as an agent error.
