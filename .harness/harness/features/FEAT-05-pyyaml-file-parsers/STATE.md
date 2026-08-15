# STATE

## Current

- feature: FEAT-05-pyyaml-file-parsers
- squad: main-session (DEC-174 carve-out — the harness does not EXECUTE changes to its own
  enforcement layer through a team run whose gates are the thing being changed)
- status: build-complete, awaiting review

Phase `build` COMPLETE 2026-08-03. **All 17 tasks landed.** `review_sha` should be RE-PINNED
before the panel runs — `225cc98` was the baseline when the orchestrator was stood down, and
twelve commits have landed since.

**All four gates green:** `run-unit-tests.sh` 0 (11 suites), `check-docs.sh` 0,
`check-state.sh` 0, `gen-decisions-index.py --check` 0. Every `.harness/**/*.yaml` parses.

**Every open question is measured, none inferred.** Q3 (which hook copy fires), Q4 (session
identity), Q6 (which validate-digest.py governs) were all settled by probe, and two of my own
claims were disproven in the process — recorded in the receipts rather than quietly corrected.

**One criterion cannot be met by me:** SC-09 is `verify: uat` and stays `not_met` until the user
runs `notes/uat-bootstrap-escape-expiry.md`. Ship gates on it (`harness.json:244`).

## Landed

- **T-01 DONE.** PyYAML **6.0.3** importable from the resolved bare `python3`. Installed with `--user`
  at the user's instruction, mid-build — recorded as `PLAN.md` **Amendment 1**, which also supplies the
  clean SC-08/SC-09 simulation mechanism the BRIEF asked for: `PYTHONNOUSERSITE=1` makes PyYAML absent
  for exactly one invocation, no uninstall or container needed.
- **T-01 step 2, re-baselined post-approval.** `check-state.sh` exit **0**, **0** violations, **39**
  notes. Q3's stale exit-1 is discharged.
- **T-01 step 3.** `notes/receipt-baseline-run-inventory.md`. `parsed == declared` for all five —
  1/1, 4/4, 19/19, 15/15, **3/3**. No run is dropped today, so SC-13's "identical" holds and the
  SC-13-vs-SC-01 conflict branch does **not** fire.
- **T-02 RED as designed, and it is why the corpus defect was found at all.** It surfaced the invalid
  corpus on its first run, and it named the file and the parse error rather than failing opaquely, which
  is what made it chase-able instead of dismissable as an expected RED. Nine named tests,
  `run-unit-tests.sh` exit 1, no `MISCONFIGURED`, 9 pre-existing suites PASS.
- **T-03.** `harness_yaml.py`, now **9 of 9 green**.
- **T-05.** `cost-report.py` annotated per D-04, no conversion, no `import harness_yaml`.
- **The corpus repair.** Three `feature.yaml` files, receipt at
  `notes/receipt-orchestrator-yaml-data-repair.md`. Two mechanical defect classes: a multi-line plain
  scalar containing `: ` (illegal multi-line implicit key), and a sequence item opening with a backtick
  (a YAML reserved indicator). 27 items became folded `- >-` block scalars, 1 was quoted.
- **`team-config.yaml:18` APPLIED by the main session**, my candidate verbatim, 1 insertion /
  1 deletion. Candidate and evidence at `notes/receipt-orchestrator-team-config-fix-candidate.md`.
- **D-03 EQUIVALENCE PROVEN — build the hook conversions on this rather than re-deriving it.** OLD
  `collect()` (extracted verbatim from `check-domain.sh:107-125`) on the ORIGINAL file vs. NEW
  `manifest_domains()` on the CANDIDATE file, for **every** `name:` in the manifest: **19 agent names,
  0 mismatches**, `mine` and `shared` matching set-for-set, every glob a `str`.
- **Interface correction applied mid-run:** `require_or_bootstrap(root, payload=None)` reads the
  `HOOK_PAYLOAD` **env var, never stdin**. T-02's receipt had pinned a stdin fallback;
  `check-domain.sh:232-235` records the gate's first draft losing the payload exactly that way and
  passing everything. Read the module against the corrected interface, not the plan's.

## Open Questions

- **B1 — RESOLVED.** `team-config.yaml:18` applied; it was the **one and only** cause of the red gate.
  Severity worth keeping: ` ##` opens a comment **even inside a `[...]` flow sequence**, so the `[`
  never closed and the document died at line 23 — **every key from `orchestrator:` onward was
  unreachable**, nine top-level keys including the whole team roster. One unquoted `#` took out the
  entire manifest, and six regex readers never noticed because they never had to close the bracket. It
  was the routing wall's **fourth** recurrence (FEAT-03 Q13, FEAT-04 T-09, this feature's Q7).
- **B2 — RESOLVED** by BRIEF Amendment 1 (REQ-08 / SC-14).
- **B3 — the dangerous half is RETIRED. Derived twice independently, by me and by the main session,
  agreeing.** A worktree script running with a main-checkout `root`, writing `.pyyaml-bootstrap` outside
  T-10's `.gitignore` edit, is **impossible by construction**. `.claude/settings.json:23` invokes
  `${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/check-domain.sh`, and `check-domain.sh:64` sets
  `root="${CLAUDE_PROJECT_DIR:-}"`. **The same variable selects both the script and the root, so they
  cannot diverge**; the fallback at `:66-70` is `_derived`, computed from `BASH_SOURCE` at `:60-62`, so
  an unset or unreadable value makes the script self-locate to its own repo. **T-10 is not broken and
  the deadlock it exists to prevent stays prevented.**
- **B3, what remains.** Only *which value* `CLAUDE_PROJECT_DIR` takes, i.e. whether SC-05/SC-06/SC-08
  can be exercised before merge. All-or-nothing, so a wrong assumption is **loud rather than silently
  corrupting**. Two options: probe it, or mark those three `verify: after-merge` and review code rather
  than behaviour.
- **B4 — RESOLVED 2026-08-03 by measurement.** Session identity IS reachable in a genuine
  `PreToolUse` subprocess: 21 fires show the payload carries only `agent_type`/`tool_input`/
  `tool_name` (so `_resolve_identity`'s first two entries are dead here) while
  **`CLAUDE_CODE_SESSION_ID` is present at 36 chars** — the chain's third entry, verified
  end-to-end against the module. **The bootstrap escape is implementable as designed; SC-08
  and REQ-05 need no redesign.** Receipt: `notes/receipt-main-session-q4-session-identity.md`.
  T-09's "extra question" is resolved with it — the env var is read straight from `os.environ`,
  so the `:97` call site needs no `HOOK_PAYLOAD` addition. The verify-method defect in T-09
  stands as a finding (`RESOLVED VIA: mechanism-unknown` satisfied its greps while the
  criterion was unmet) even though the underlying question is now answered.
- **B4, superseded text kept for provenance —** it read: T-09's probe **never executed** on a genuine
  hook fire. That is **not** the plan's ESCALATE branch, which requires positive proof the block ran.
  All three of T-09's verify greps pass while its criterion is unmet — `RESOLVED VIA:
  mechanism-unknown` satisfies the grep. **Read the receipt, not the greps: this is a verify-method
  defect, not a pass.** My diagnosis — a `root`-resolved append raising into `except Exception: pass`
  because the main checkout has no `FEAT-05-pyyaml-file-parsers` directory — holds **only if `root` is
  the main checkout**, which per the coupling above happens only when the MAIN script is running. So B4
  and B3 resolve together. PLAN T-09 constraint 2's "the `notes/` directory already exists (verified)"
  was verified against the **worktree only**.
- **B5 — right, and MOOT.** `PLAN.md` carries no task for SC-14. Since the main session builds it
  directly under DEC-174, no pm task is needed: the BRIEF amendment is the spec.

## Two rulings LANDED, 2026-08-03 — both were mine to raise, neither mine to decide

**RULED: the FEAT-03 / FEAT-04 repair STANDS.** The user ruled it in scope; recorded in BRIEF
Amendment 1 so a reviewer does not read it as drift. My reasoning was accepted — SC-02 and SC-13 read
the whole `.harness/features/*/` tree, so those files sit inside this feature's evidence path.

**One correction to my own claim, accepted.** I said the repair was "proven semantically neutral three
ways." A **data-level equality proof is impossible by construction** for FEAT-03 and FEAT-04: the
pre-repair files cannot parse, so there is no before-state to compare against. My load-bearing evidence
is narrower than I framed it — it is that the T-01 run-inventory receipt **diffs to zero rows**, which
is what keeps SC-13's baseline valid rather than silently stale, plus top-level keys identical before
and after. Lead with the diff, not with a parse comparison. (The before==after equality assertion I
*did* run applies only to FEAT-05's later block-scalar hardening, by which point that file already
parsed.)

**RULED: the corpus-validity gate is APPROVED and the BRIEF is amended.** `BRIEF.md` Amendment 1 adds
**REQ-08** and **SC-14**. The feature is now **8 REQs, 14 SCs**. Binding constraints on SC-14:

- `verify: unit`. Walks every `.harness/**/*.yaml`, `safe_load`s each, **fails naming file, line and
  column**.
- **It MUST be listed in `run-unit-tests.sh`'s `SCRIPTS` array.** A test the runner does not invoke
  gates nothing — issue #5's exact failure mode.
- **It must be shown RED against a deliberately malformed fixture, then GREEN on the repaired
  corpus.** An always-green validity gate is indistinguishable from no gate.
- A `PreToolUse` hook was considered and **REJECTED** as over-engineering — no new mechanism, no
  `harness.json` change, no per-write latency. Do not reintroduce it.

## Carried forward

- **T-11 must use the `--user` form of `INSTALL_COMMAND`**, not D-07's original string. D-07's omission
  of `--user` was a defect: without it pip writes into Homebrew-managed `site-packages`, which
  Homebrew's own PEP 668 message warns "can result in a broken Homebrew installation."
- **T-10 must complete before T-12.**
- **D-09 stands.** `check-state.sh:113`'s `review_sha: none` fail-open is deliberately not fixed; T-16
  files the issue.
- **SC-09 is `verify: uat`** and `harness.json:244` is `blocking_when_uat_criteria_exist`, so ship gates
  on a human hand-running T-16's script. No agent can satisfy it.
- **Q6 — CORRECTED, because the earlier wording here over-claimed.** What is **verified** is that the
  two copies of `validate-digest.py` **differ**: the main checkout has 0 `GATE_FIELDS`, this worktree
  has 2. **Which copy the `SubagentStop` hook actually executes is NOT measured.** Per the B3 coupling
  above it resolves whichever way `CLAUDE_PROJECT_DIR` points, and that value remains unmeasured — so
  whether DEC-173's widened schema was in force for agents spawned here is **unknown, not established**.
  Digests in this feature were encoded against the OLD contract as a deliberately conservative choice,
  which is safe under either resolution. The previous sentence asserting the hook "resolves the main
  checkout's copy" was an over-claim and is retracted.

## Backlog nit — not fixed here

`check-domain.sh:59` says "walk up five levels" and `:62` walks up **four** (`../../../..`). Four is
correct — `bin` → `harness` → `skills` → `.claude` → root. **The comment is stale, not the code.** It
matters because a future reader "correcting" the code to match the comment would break the root
derivation both hooks depend on. The main session is fixing it while in that function.

## Cost

**$240.82 of a $120 budget** — 2.0x nominal, overrun accepted at signature, not raised. Cost is
reported, never gated (DEC-134).

**The nominal figure overstates the feature.** Runs 02-04 are attributed by **cumulative delta** on
`cost-report.py`'s whole-session total, so run 04's $148.82 absorbs main-session work that is not
FEAT-05 build cost: the DEC-171/172/173 reversals, commit `225cc98`, a decisions audit, the BRIEF
amendment, the manifest fix and two commits. **The true overrun is materially less than 2.0x and nobody
can say exactly what it is.** A cleaner attribution is not available, and a fabricated split would be
worse than a caveated overstatement.

`cycles_used` stays at **1**. eng-lead reported four spawns and **zero send-backs**, so no rework cycle
was consumed; the existing 1 counts the plan-phase rework.
