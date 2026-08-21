# Security review — FEAT-30 containment audit — a76d69a

**Headline:** the HEAD-move question the operator asked about is a signed, tested, pre-existing
coverage class and SC-03 survives it as literally worded — but the diff's own new
`expertise-merge.py` + its T-07 wiring create a fresh, demonstrated `high` gap: invoking it via Bash
is invisible to `bash-write-guard.sh`'s write-pattern vocabulary, so (a) any governed agent can
overwrite *any other agent's* Expertise file or *any other path* with zero domain check, and (b)
**reviewers — contractually read-only, "any write pattern denied outright, no path analysis" — can
write arbitrary content to arbitrary files through it**, which is also the literal mechanism
`harness-distill/SKILL.md` now instructs every reviewer to use for their own distillation. All
measurements below were taken live against the pin (`CLAUDE_PROJECT_DIR` set, payloads piped
through the real hook).

## F1 — HIGH — enforcement-layer — must_fix
**`bash-write-guard.sh`** (write-pattern vocabulary at lines 380–482, unchanged by this diff) does
not recognize `python3 .../expertise-merge.py apply --file <path> --entries -` (or
`feature-worktree.py`) as a write at all — `findings` stays empty and the guard exits 0 before ever
reaching the domain walk *or* the reviewer read-only check (`bash-write-guard.sh:617,628`).
Demonstrated:
- `harness-documentor` (docs-only domain) → `expertise-merge.py apply --file
  .harness/expertise/harness-security-reviewer.md` → **exit 0**. Also against `--file src/main.py`
  → **exit 0**. Both would be denied instantly over the Write tool or over a plain `echo > `.
- `harness-security-reviewer` (read-only role) → the same invocation → **exit 0**, while a plain
  `echo pwned > src/main.py` from the same agent correctly exits 2 ("READ-ONLY... no path
  analysis").

This is not merely a pattern-vocabulary gap the diff happened not to close — this diff **created**
the standard workflow that walks every agent into it: T-06 built the tool, T-07 rewired
`harness-distill/SKILL.md` so every agent, reviewers included, is told to reach it via exactly this
Bash shape at every feature-close distillation (`harness-distill/SKILL.md:29-32`). The
"reviewer read-only, no path analysis" simplification in the guard's own header comment
(`bash-write-guard.sh:13-14`) is falsified by the very tool this diff ships. `check-domain.sh` never
sees it either (`Write|Edit` matcher only). `feature-worktree.py` shares the same blind spot but its
own internal `REFUSE_ON_DIRTY`/`REQUIRE_LANDED` gates bound an unauthorized `remove` call's blast
radius; `expertise-merge.py` has no analogous self-check on who is calling it or what `--file`
targets — it trusts the caller completely. No test in `test-bash-write-guard.py` exercises either
tool's invocation shape. Remedy is most naturally in `bash-write-guard.sh` (recognize invocations of
these first-party CLIs and extract `--file`/destination for the existing domain walk); a
complementary, squad-appliable fix is for `expertise-merge.py` to require and validate an
`--agent`/env-sourced identity against `team-config.yaml` itself.

## F2 — MED — enforcement-layer — advisory (not must_fix; residual, not a regression)
**The literal-token HEAD-move parser** (`bash-write-guard.sh:136-221`) is bypassed by anything whose
git invocation isn't the head token of a shell segment. Demonstrated for `harness-orchestrator`
(D-04's no-exemption case): `git checkout main` → exit 2 (blocked, correct); `python3 -c
"import subprocess;subprocess.run(['git','checkout','main'])"` → exit 0; `g=git; $g checkout main`
→ exit 0; `eval 'git checkout main'` → exit 0. The `git --git-dir=` undecidable case fires only when
no subcommand follows at all, exactly as designed.

This is the **same casual-shape-filter class DEC-85/DEC-151 already accept** for the writes rule,
now extended by T-05 to HEAD-moves — the task's own intent text says so explicitly ("This guard is a
casual-shape filter by DEC-151, and refusing the undecidable case is the direction that entry
already chose," `plan.yaml` T-05). **SC-03 as literally worded** ("An attempt... is REFUSED and says
why. The test drives the refusal and proves it can pass when it should") is **not falsified**: it is
scoped to the test's own driven scenarios, not to a claim of completeness against obfuscation, and
those scenarios are green (179/0, 213/0 per operator's measurement).

What is new: the blast radius. Before this diff, the accepted casual-shape residual protected
against a stray file edit inside one checkout, recoverable via git; now it is one of the two legs
holding up cross-worktree containment (SC-01/SC-01b) for concurrently-running, cross-repository
features — a HEAD move mid-run corrupts every other agent standing in that checkout for the
duration of the window, which is harder to characterize after the fact than a file diff. I found
**no equivalent "post-run tree audit"** for HEAD position specifically (`check-state.sh` has none;
the only audit of this shape on record is the one-shot, manual DEC-153 bypass audit, not a running
gate) — so the detective control that makes the writes-side residual tolerable does not clearly
extend here. Residual risk is from a **cooperative-but-frustrated agent** reaching for a wrapped
retry after a literal refusal (the exact shape DEC-153's own incident narrative documents for the
write case) more than from a deliberate adversary — worth the operator's attention, not a gate
failure.

## F3 — MED — enforcement-layer — advisory (in-tree part signed; escape-outside-tree unassessed)
`.claude/worktrees/` blanket carve-out (`bash-write-guard.sh:687`, unchanged by this diff): matching
purely on the **textual, non-realpath'd** path, run *before* `classify()`. The "any governed agent
may write any file under any worktree" half is explicitly signed (DEC-153) and pinned by
`test-bash-write-guard.py::run_worktree_deep` — not a new finding, assessed and dismissed.

Not covered by that signature or that test: a symlink placed inside a worktree pointing outside
`.claude/worktrees/` (e.g. at the main checkout's hard-protected files). Since the carve-out's
regex match runs on the literal `rel` with no `os.lstat`/`realpath`, unlike `classify()`'s own
symlink-resolving `real()`, and a `>` redirect always follows a symlink at the OS level, a governed
agent (or the `.git`-pointer walk, or a checked-in symlink) could redirect the carve-out's blanket
allowance to a target entirely outside the accepted scope. I verified the guard's decision is
filesystem-content-blind (identical exit 0 for an existing vs. a nonexistent leaf path) but did not
plant a live symlink — I hold a read-only role, and the only live worktree fixture (`FEAT-31`) is
explicitly off-limits. Symlink *creation* itself is also outside the guard's write-pattern
vocabulary (`ln` is not a detected pattern), so planting one is itself undetected. DEC-153's text
frames the accepted risk as "a stray edit inside a disposable checkout" — this would be an edit
landing outside it, which the decision does not appear to have considered.

## F4 — LOW — squad-appliable (`expertise-merge.py`)
`expertise-merge.py:37`'s `ENTRY_RE` (`[A-Za-z]{1,3}-\d+`) is looser than `check-expertise.sh:44`'s
(`[A-Z]{1,3}-\d+`). Traced the actual consequence rather than assuming: `check-expertise.sh` does
**not** silently fold a lowercase-id line into the previous entry — it explicitly flags it ("entry
lacks the '- XX-NN: ' id prefix") and still counts it toward the section cap, so its own gate stays
fail-closed. The practical defect is narrower than a bypass: `expertise-merge.py` can successfully
merge and write a lowercase-id entry that `check-expertise.sh` will then report FAIL on the very
next run — a correctness/consistency wart between two copies of the same shape rule, not a silent
gate defeat. Fix: import or mirror `check-expertise.sh`'s regex exactly, the same discipline this
file already applies to the `CAPS` dict (its own docstring names the CAPS-agreement test as
deliberate; the id regex was not given the same treatment).

## Assessed and dismissed (no finding)
- `harness_boundary.worktree_owner`/`checkout_relative`/`classify`'s malformed-`.git`-pointer path
  is fail-closed: live-tested with a garbage-byte pointer file → `(dir, None, False)`; both
  `check-domain.sh` and `bash-write-guard.sh` test `owner_root is None` / `unparsed` and exit 2.
- Sibling-checkout-prefix confusion (`/workspaces/widget-other` vs. `/workspaces/widget`) and `..`
  traversal are both closed via `commonpath`/`realpath`, verified live against `select_base`'s
  `inside()` helper and `harness_boundary.real()`.
- `feature-worktree.py`: `subprocess.run(["git", ...])` throughout, never `shell=True` — no
  injection surface. `--id` is regex-validated (`^(FEAT|BUG)-[0-9]+[a-z0-9-]*$`) before any use in
  `create`; unvalidated in `remove`, but GATE 1 anchors removal to `git worktree list
  --porcelain`'s own real paths, so a malicious `--id` cannot escape to an arbitrary directory.
  `--repo`'s `owner/repo` form resolves against `fleet.yaml`'s declared entries (operator-authored)
  before any subprocess use.
- No secrets/credential-shaped strings found across the full diff (docs, SPEC.md, SKILL.md,
  orchestrator.md, harness.md included).

## Out of scope, not re-raised
Issue #626; FEAT-26/28/31; the two already-known `test_kinds` glob/runner mismatches;
`check-state.sh`'s FEAT-30 INV-26 rows; the qa gate.

## Open questions
- Q1 (non-blocking): should `expertise-merge.py` accept an `--agent` identity and self-validate
  `--file` against `team-config.yaml`, as a second line of defense independent of
  `bash-write-guard.sh`'s pattern list? Recommend yes, but it is a design call for whoever owns the
  enforcement layer under DEC-174, not mine to decide.
- Q2 (non-blocking): does a "post-run tree audit" for HEAD position exist anywhere outside a
  one-shot manual audit? I could not find one; if none exists, F2's residual risk is uncompensated
  rather than caught post-hoc the way the write-side residual is.
