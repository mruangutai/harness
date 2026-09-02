# Plan-panel cycle 5 — scope reader (harness-code-reviewer)

FEAT-48-parallel-safe-suite · plan.yaml at HEAD 2a5cbada (confirmed via `git rev-parse HEAD` in
worktree) · read-only, plan.yaml byte-unchanged.

## VERDICT: PASS. Would sign.

The gating cycle-4 finding (PF-58719ff7, high) is closed by mechanism, not by prose, and verified
against the actual files in the worktree. Both cycle-4 med findings are closed. The satisfiability
sweep yields zero. The census-shape change survives the adversarial fifth-rot simulation. One new
med finding (T-07's supersession is not uniformly mechanical — see below) and one new low/advisory
finding (declared `files:` understates actual touch scope) are neither gating.

**Would sign: YES**, on the plan as it stands at 2a5cbada.

---

## 1. Cycle-4's eight findings, dispositioned at source

| id | cycle-4 severity | disposition | evidence |
|---|---|---|---|
| PF-58719ff7b430616b91b5a7cfe49bde10 | **high, gating** | **CLOSED, mechanism** | See §2 below — full re-derivation |
| PF-d6f80211bcb8f4748a2d54b8800e7b80 | med | **CLOSED, by fix** | D-10 rewritten (plan.yaml:142-267): "No count and no file list anywhere in this plan defines that scope" (plan.yaml:143-144). This is the operator-mandated re-plan itself |
| PF-2781572957dd1fed494c0b18fbba5155 | med | **CLOSED, by fix** | T-06 intent now reads: "THE CONTROL IS TAKEN INSIDE AN ISOLATED BIN COPY, AND THAT ROUTE IS NOT OPTIONAL... Use the mechanism T-01 already shipped" (plan.yaml, T-06 intent, SC-02 subsection) — no longer directs re-performing the hazard on the live tree |
| PF-fa5127af58944f09ad76a303015e2a6a | low, non-gating | **still open, unchanged, advisory-only** | fix_order rank 5 marked this advisory-only; T-06 still requires the "tree condition:" line pricing the ceremony (T-06 intent, SC-05 subsection) — same shape as cycle 4, no regression, not tasked for this cycle |
| PF-de766c578a1c31ed94ee0a8238402574 | low | **CLOSED, moot** | T-02's stale anchors are gone entirely: "there are no line anchors here on purpose, because the four this task carried in cycle 4 were stale within one cycle three times running" (T-02 intent) |
| PF-f44a92962d493af2d33d19c801183830 | low | **CLOSED, by fix** | T-03 intent now states discovered=59 at 2a5cbada — matches current HEAD, re-derived |
| PF-3c7fcaf3931a40ce1cb9ab1d5e3c8bb6 | low | **CLOSED, by fix** | T-05 intent now states "192 of 192 existing headings carry the em-dash and the last is DEC-209" at 2a5cbada — matches |
| PF-04e9f2759a20c919ed61d55f4306fda6 | low | **PARTIALLY CLOSED** | `BRIEF.md` fixed: new "## The FEAT-47 boundary — settled, and not an operator question" section (BRIEF.md:213-227) replaces the open-question framing. **Issue #1053's own `## Scope` section is still stale** — verified live via `issue://mruangutai/harness/1053`, its body still reads "Folded into **FEAT-47**". No task in this plan writes the GitHub issue body, so this residual is out of plan.yaml's scope; low, non-gating, flagged for the operator to close by hand or via `gh issue edit` |

**Net for cycle 4:** the one gating finding is closed; both med findings are closed; four of five lows are closed or moot; one low (SC-05 ceremony) is unchanged by design and one low (issue #1053 body) is a genuine residual outside this plan's write authority.

## 2. PF-58719ff7 (the gating high) — full re-derivation against the worktree

Verified each of the three cited site groups directly against source, not against prose:

- **`test-bash-write-guard.py:891-897`** (`_feat50_bash_mutant`, writes
  `.feat50-bash-write-guard-{pid}.sh` into `HERE`, live bin/): **owned via T-02's derived run
  set.** T-07 (`status: abandoned`, `depends_on: [T-02]`, `files: [test-bash-write-guard.py]`,
  plan.yaml:1254-1300) is exactly the shape T-02's verify block's `absorbed` computation requires
  — I hand-executed the logic (`plan.yaml:576-596`) against the live task list: `absorbed =
  {test-bash-write-guard.py}` (only T-07 qualifies: `status=='abandoned' and 'T-02' in
  depends_on`), and the subtraction `absorbed -= {files of live tasks}` removes nothing (no live
  task owns that basename). `run_set` is non-empty and includes it. Confirmed with a direct read
  of the live file at 891-897 — the site is still unfixed (expected: plan phase, code not yet
  written) and matches the shape T-02's intent describes.
- **`test-check-domain.py:3275-3289`** (`_feat50_mutant_between`, SITE B): **owned directly** —
  `files:` of T-01 lists `test-check-domain.py` (plan.yaml:307-309), and T-01's intent names this
  exact site and function by name.
- **`test-check-state.py:3584-3612`** (`case_inv32_era_guard_is_load_bearing`, writes
  `.check-state-inv32-era-mutant.sh`): **owned directly** — `files:` of T-02 lists
  `test-check-state.py`, and T-02's intent names ".check-state-inv32-era-mutant.sh" explicitly as
  one of the four sites in that file.

All three groups the cycle-4 finding named are now owned — two directly via `files:`, one via the
derived run set through T-07's supersession. `check-plan-routes.py` run live against this plan
(see §6) confirms 0 VIOLATION, so the derived-ownership route is not merely asserted in prose —
the actual verify-block arithmetic was executed by hand against the live task list and produces a
non-empty, correct `run_set`.

## 3. Satisfiability sweep — cycle 5 yield: **0**

Prior cycles: 2, 2, 0, 2. Swept all seven `verify:` blocks (T-01 through T-07, including the
retained-for-record T-07 block) for: unreachable assertions, assertions on something a predecessor
task deletes, and greps for strings the plan never requires anyone to write. Found none. Specific
checks performed:

- **T-02's derived-run-set logic** (the target named in the brief): hand-executed against the
  live task list (§2 above) — `absorbed` is non-empty, the subtraction removes nothing it
  shouldn't, `yaml` import is safe (pyyaml is already a load-bearing dependency of this repo's
  test suite — `test-feature-worktree.py`, `test-plan-merge.py` and eight others already `import
  yaml` unconditionally, several of them registered INTEGRATION_SCRIPTS), and the relative path
  `.harness/harness/features/FEAT-48-parallel-safe-suite/plan.yaml` the block opens exists from
  repo root, the CWD convention every verify block in this plan already assumes.
- **T-01's verify**: poll-thread + subprocess shape is internally consistent; the two case labels
  it greps for ("CRASHING schema module DENIES", "never written") — the first already exists
  verbatim in the live file at `test-check-domain.py:1482`, the second is a new case T-01's intent
  explicitly instructs the doer to add with that exact substring.
- **T-03's verify**: the `want` set of 10 historical sites is internally self-consistent with
  T-03's own intent narrative (2+6+2=10, matching basenames and line numbers named in the intent
  text), and `git show ea6f51f:...` resolves — confirmed `ea6f51f` exists as a real commit in this
  worktree's history.
- **T-04's verify**: traced each of the five `run_pool.py` legs (attribution, worker-count env
  override, clean/edit/new mutation-check legs, empty-dir refusal) against `run_pool.py`'s own
  spec in T-04's intent — each assertion matches an explicit behavioral commitment in the intent
  text, none references anything a predecessor task removes. `run-unit-tests.sh`'s root resolution
  is confirmed CWD-independent (`_SELF_BIN` derives from `BASH_SOURCE[0]`, not CWD —
  `run-unit-tests.sh:10-11`), so running it from the verify block's tempdir CWD is safe.
- **T-06's verify**: all five regexes over `measurements-parallel-suite.md` match literal line
  formats T-06's own intent instructs the doer to write verbatim (`control method:`, `control
  broken reads`, `post-fix broken reads`, `pool: … wall`, `tree condition:`).
- **T-05's verify**: the phrase list it requires inside the new DEC section is a subset of what
  T-05's own intent instructs the doer to write; `words >= 300` is achievable given the intent's
  bullet list.

No block found asserting something a predecessor deletes, and no orphan-REQ or nonexistent-REQ
trace: `grep -o 'REQ-[0-9]*' plan.yaml | sort -u` yields exactly REQ-01..REQ-08, matching
BRIEF.md's defined set one-for-one, with every REQ traced by at least one live task.

## 4. Fifth-rot simulation — verdict: **ABSORBED**

Scenario: tomorrow a sibling feature merges another mutant-idiom test file under
`.claude/skills/harness/bin/**`.

**If it lands after FEAT-48 ships** (the natural reading of "tomorrow"): no task fixes it — none
needs to. T-03's static invariant (`test-suite-independence.py`, registered `UNIT_SCRIPTS`, runs
on every push to an open PR per `.github/workflows/tests.yml`'s bare `pull_request:`) discovers it
unconditionally: its discovery walk is "every file matching `test-*.py` or `test_*.py`" under the
whole repo (plan.yaml:675, T-03 intent) — not a fixed list — and its taint rule (plan.yaml, T-03
intent, "THE RULE" subsection) applies per-file with no basename allowlist. A sibling's new mutant
idiom reddens **that sibling's own CI push**, at plan.yaml's designed seam, before merge.
Independently, T-04/T-06's runtime `--mutation-check "$BIN_DIR"` (plan.yaml:918-919, D-11) snapshots
every file under `bin/` by `(size, st_mtime_ns)` including untracked ones and flags anything that
"changed, vanished or APPEARED" — vector-agnostic, not keyed to any basename or count either.
Neither instrument reads a plan-authored list. **No numeral or basename in the plan becomes
false**: the "EIGHT sites in FOUR files" figure is explicitly marked "DATED, NON-BINDING... THIS
FIGURE SIZES THE WORK AND DOES NOT DEFINE IT" (D-10, plan.yaml:174-186) and nothing live reads it;
T-03's discovery floor of 50 is a different, unrelated number that a ninth site would only push
further above, never below.

**If it lands mid-build** (a sibling PR merging while FEAT-48's own tasks are still executing,
before T-03 is dispatched): T-02's intent explicitly authorizes and instructs absorption of "a
site in a FURTHER file under `.claude/skills/harness/bin/**`" (plan.yaml:531) — lane-resolved by
the glob, fixed in the same isolated_bin shape, named in the receipt. This is prose-level (a doer
must actually re-run the census and read this clause), not verify-block-enforced for a file
outside T-01/T-02's currently-known sites — **but** if a doer misses it, T-03's own verify (a
live-tree ZERO over the whole repo, not just T-01/T-02's declared files) legitimately reddens and
forces a fix before T-03 can land; that is explicitly the design ("a site either of them missed
reddens there, in CI" — D-10, plan.yaml:266-267), not a defect. **No new plan task is required in
either timing** — the operator's directive was carried out for the standing/future-facing half
without qualification, and for the mid-build half via an explicit (if prose-level) absorption
clause plus a real, unconditional backstop.

## 5. T-07 collapse — genuinely closes the ordering hole; one new med finding on enforcement

- **Ordering**: now a real DAG edge, not prose. T-03's `depends_on: [T-01, T-02]` (confirmed via
  direct YAML parse) is what makes T-03 unreachable until both land; T-07 does not need a
  `depends_on` entry naming it because T-02 subsumes its site.
- **REQ coverage**: T-07 traces REQ-01; T-01 and T-02 (both live, both traces `[REQ-01]`) already
  cover it — abandoning T-07 orphans nothing (confirmed via direct YAML parse of all seven tasks'
  `traces:`).
- **8 surviving mentions, confirmed as 7, not 8**: `grep -c 'T-07' plan.yaml` → 7 (6 inside D-10's
  prose plus the `id: T-07` line itself). The orchestrator's stated count of 8 is off by one — not
  a plan defect, but worth correcting in the record. All 7 are either explanatory ("why it existed"
  / "why it's superseded") or the abandoned task's own header; none instructs a doer to act on it.

**New finding (med, non-gating): T-07's supersession is not mechanically uniform across tooling.**
Ran `check-plan-routes.py .../plan.yaml` live in the worktree. It emits `0 violation(s)` (matches
the contract), but it **still computes and prints a `DEVIATION` line for T-07** —
`DEVIATION T-07 .claude/skills/harness/bin/test-bash-write-guard.py granted to
harness-backend-dev, harness-dev-ops but declared main-session-direct` — identical in shape to the
six live tasks' lines. This tool does not special-case `status: abandoned` at the task level (its
own `legal_task_statuses()` accepts it as a legal *value*, but nothing skips route-checking for
it). Non-gating here because `DEVIATION` never contributes to `total_violations` (confirmed:
`total_violations=0` despite 7 DEVIATION lines) — the consequence is cosmetic. But it is direct,
mechanical evidence that "abandoned" is **not** uniformly treated as dead by this repo's own
tooling; `build.yaml`'s `steps_from:` block explicitly defers task-set selection to "the
ORCHESTRATOR's decision, made before dispatch and not restated as config" (`build.yaml`, `steps_from`
comment) — i.e., no config-level filter on task `status` exists there either. Reliance for a
reliable skip rests on (a) the well-established, broadly-tested convention that `abandoned` is
`factory_config.TERMINAL_MARKER` used identically at the feature level throughout this codebase,
and (b) T-07's own prominent refusal prose ("DO NOT DISPATCH THIS TASK... Nothing below is an
instruction"). Both are real but neither is a verified mechanical guard for the *task-level* case
specifically (as opposed to the well-tested *feature-level* case). Recommend, non-blocking: the
orchestrator/eng-lead dispatching this plan's build should explicitly confirm at dispatch time that
T-07 is excluded from `build.yaml`'s task expansion, since no gate currently proves it mechanically.

## 6. The write-once consequence — files: understates T-02's touch scope

Confirmed: T-02's declared `files:` is exactly `[test-check-state.py, test-feature-worktree.py]`
(direct YAML parse) — it does **not** list `test-bash-write-guard.py`, which T-02 will physically
edit via the absorbed-run-set mechanism. This is deliberate and extensively documented (D-10's
"OWNERSHIP IS NO LONGER SPLIT BY FILE" section, plan.yaml:212-232; T-02's own intent, plan.yaml:526).

**Ruling: SIGNABLE.** Two independent reasons:

1. **Write authorization does not come from `files:` at all.** Read `check-domain.sh` directly:
   its `--resolve` / hook-time authorization is computed from the manifest domain grant
   (`main-session-direct` under the DEC-174 carve-out, covering the whole
   `.claude/skills/harness/bin/**` glob) — it never consults a task's per-file `files:` list. D-10's
   claim ("lanes: keys on that GLOB and not on individual files... every test file beneath it is
   already lane-resolved") is verified true against the actual gate script, not merely asserted.
   The write is authorized regardless of what `files:` says.
2. **Completeness is proven by the verify block's derivation, not by the `files:` field.** T-02's
   verify computes its `run_set` from `plan.yaml`'s own ownership graph and checks it directly — it
   does not trust `files:` to be exhaustive.

**Residual risk (low, advisory, non-gating):** a build-cycle code reviewer running Stage 1
(spec-compliance) against T-02's diff, if they diff only against `files:` rather than reading
T-02's intent narrative, could misflag the `test-bash-write-guard.py` edit as scope creep. The plan
mitigates this by requiring the doer to "NAME the addition in the receipt" (T-02 intent), giving the
reviewer a pointer, but nothing forces the reviewer to read the intent rather than the `files:`
field alone. Recommend the build-cycle review dispatch note this explicitly. Not gating this plan
review — it is a review-time process risk, not a plan defect, and the plan already does everything
short of removing the reviewer's own judgment burden.

## 7. Orchestrator measurements — re-verified, not adopted

- `approval: {status: pending}` — confirmed via direct YAML parse.
- top-level `status: plan` — confirmed.
- `panel.cycle: 4` — confirmed unchanged (this is cycle 4's record; cycle 5's value lives in this
  digest, not in the file, matching stated convention).
- DAG — confirmed exactly: T-01 `[]`, T-02 `[T-01]`, T-03 `[T-01,T-02]`, T-04 `[T-03]`, T-06
  `[T-04]`, T-05 `[T-06]`, T-07 `[T-02]` station `abandoned`.
- `check-plan-routes.py` — ran live: **7 DEVIATION, 0 VIOLATION, exit 0**. Confirmed exactly.
- `D-10.because` — 7397 chars (confirmed via `len()`), **9 paragraphs via 8 embedded `\n`**
  (confirmed via parse: each of the 8 ALL-CAPS section headers is preceded by exactly one literal
  newline, the expected YAML folded-scalar behavior for a blank line in source — not a flattening
  defect). Read start-to-finish: it is coherent, connected prose across its 9 sections, not garbled
  or truncated.
- One correction to the shared context: **"Remaining T-07 mentions repaired: 19 → 8" should read
  → 7** (see §5). Minor, does not change any disposition above.

## Open questions

None blocking. One non-blocking observation carried into the digest: T-07's tooling non-uniformity
(§5) is worth an eng-lead confirmation at build-dispatch time, not a plan re-write.
