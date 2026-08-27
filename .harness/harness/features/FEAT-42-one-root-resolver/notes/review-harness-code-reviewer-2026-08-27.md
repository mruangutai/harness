# Code review — FEAT-42 one-root-resolver — 9d12e3a — code-reviewer

Scope per dispatch: resolver contract + call-site fail-open/closed audit + three named stale
comments + the case_20 exemption + SC-10 TDD evidence quality + the e51b814 lane question +
the check-domain.sh relative-path judgment. Read-only; DEC-174 barred me from editing ~30 of
the 80 files (all confirmed untouched here — `files_touched` below is this note only).

## Verdict: PASS, no must_fix. Findings below are backlog, ranked.

## Stage 1 — spec compliance

Every change traces to a `D-NN` in `plan.yaml`. No scope creep found. `resolve_root` /
`root_above` / `root_from_script` match D-01–D-04's contract exactly (`harness_boundary.py`
at 9d12e3a): `resolve_root` strict-raises with an override/derived-candidate message,
`root_above` walks with zero env reads, `root_from_script` is pure arithmetic with zero I/O —
confirmed by direct read, not by trusting the docstrings.

**Call-site contract check (item 1/2) — no defect.** Cross-checked all nine cutover sites
against what each one actually needs:
- Fail-CLOSED on unresolvable root (correct — these are refusal-shaped gates): `check-state.sh`
  (`:38-43`, exit 2, verified directly — the stale comment at `:1143` notwithstanding, see
  below), `check-plan-routes.py` (`:510-521`, `except ValueError: … sys.exit(2)`),
  `branch-create-gate.sh`, `gh-close-gate.sh` (per T-14/T-15 intent, not independently
  re-run but consistent with the QA gate's parity re-runs).
- Fail-OPEN by design, all pre-existing and cited (DEC-101 or the hook's own contract), none
  newly introduced: `check-domain.sh`/`bash-write-guard.sh`'s `_root()` uses `strict=False`
  deliberately to preserve DEC-101's "no manifest → enforcement OFF" carve-out (`check-domain.sh
  :127-154`); `dispatch-guard.sh` fails open on every branch **except** the missing
  `HARNESS-FEATURE` line, which is the one exit-2 branch — confirmed by direct read
  (`dispatch-guard.sh:100-165`), so the dispatch's framing of that one branch is accurate
  *as scoped to this file's own branches* (several other cutover files fail closed on
  unresolvable root independently — the "one fail-closed branch" claim is not a whole-feature
  claim and shouldn't be read as one); `validate-digest.py`'s `_root_or_none()` (`:791-802`)
  is `strict=False` + blanket `except Exception: return None`, explicitly a side-errand
  fail-open backstopped by `check-state.sh` INV-15; `inject-expertise.sh` uses `strict=True`
  (the default) but wraps the call so an unresolved root prints to stderr and **exits 0**,
  deliberately overriding T-16's own plan text — the override cites `DECISIONS.md:1503`,
  which I opened and confirms: "always exits 0 so it can never block a spawn." Legitimate,
  well-cited deviation, not a defect. `context-watch.py` and `post-merge-sweep.sh` use
  `root_from_script` (zero filesystem check, never raises) — matches the deleted functions'
  exact behaviour per T-08/T-09 intent, confirmed by reading both.
- Net effect vs. pre-feature: every fail-open here is either unchanged (DEC-101) or **strictly
  safer** than before (inject-expertise.sh previously silently injected the *wrong checkout's*
  Expertise via a pwd fallback; now it injects nothing and says so on stderr).

**Three stale comments (item 3) — all confirmed, and SC-01 structurally cannot catch any of
them.** Read at 9d12e3a:
- `check-state.sh:~1141-1143`: "`root` is CLAUDE_PROJECT_DIR or the cwd" — false; root comes
  from `harness_boundary.resolve_root` (`:38-43`).
- `check-plan-routes.py:~477`: "CLAUDE_PROJECT_DIR if it holds a readable manifest, else the
  root DERIVED from this file's location" — false; the actual precedence (confirmed at
  `:496-520`) is `harness_boundary.resolve_root`, reading `HARNESS_PROJECT_DIR` only.
- `validate-digest.py:~815`: "a hook whose cwd drifts (worktrees, unset CLAUDE_PROJECT_DIR)"
  — the function no longer reads that name at all (`_root_or_none()` at `:791`).

Confirmed why SC-01 (`test-no-distribution.py` case6) misses all three: `CHAIN_NAME =
"HARNESS" + "_PROJECT_DIR"` (`:358`) — the absence scan greps for the literal
`HARNESS_PROJECT_DIR` only. All three stale comments name `CLAUDE_PROJECT_DIR`, which SC-01
never scans for. **Finding (chore, low):** these are prose-only — the code at all three sites
is independently verified correct — but they will mislead the next reader of a gate script.
No presence/absence pair currently guards this class (DEC-169's own pairing rule doesn't
reach retired-name prose, only retired-name *code*). Worth a follow-up invariant or an
accepted-risk note; not blocking.

**Fourth instance of the same class (item 4) — found while checking the named exemption.**
`test-check-plan-routes.py`'s `case_20` docstring (`:1133-1136`) still asserts check-state.sh
"silently reports on the cwd. That is a real defect." At 9d12e3a that defect is fixed (T-12,
confirmed above: exit 2, not a silent fallback). The "exemption" itself isn't coded
skip-list logic — I read `case_20`'s body (`:1174-1204`): it's an emergent blind spot of a
source-text pattern (`.harness` literal + a filesystem predicate on the same logical line)
that check-state.sh's python-one-liner-in-a-heredoc never matched, before or after the
cutover, because the probe now lives inside `harness_boundary.MARKER`, not inline. So nothing
regressed and nothing is actively hidden — case_20 is stated in its own comments to be "a
cheap smoke check, not the guarantee" (case 21 is). **Finding (chore, low):** reword the
stale "real defect" justification; it's inert but will confuse the next person who reads it
looking for a live gap.

**SC-10 TDD evidence quality (item 5) — adequate as delivered, but the RED discipline is
weaker than it looks for 3 of 4 functions.** Read `receipt-harness-backend-dev-t01.md` and
`test-harness-boundary.py` directly. `run_case()` (`:231-238`) wraps each `case_X`; the first
call inside `case_marker_constant`, `case_root_from_script`, `case_resolve_root_strict` *and*
`case_root_above` throws `AttributeError` pre-implementation, so **none** of the four ever
exercised their internal `check()` assertions during RED — the reds only prove "the function
doesn't exist yet," identical to what an assertion-free stub would produce. The dispatch's
"only root_above is genuinely behavioural" claim doesn't hold for T-01's own receipt (I
checked; it's AttributeError there too) — it holds for a **different** receipt,
`receipt-harness-backend-dev-t02.md`'s `wayfind_directory_probe` case, which exercises
`root_above` *through wayfind's pre-existing `cfg()`* and produces a real assertion mismatch
(decoy vs. real root) before the fix. So: `root_above` alone got a genuinely discriminating
red (via T-02); `MARKER`, `root_from_script`, `resolve_root` never did, anywhere in this
build. This doesn't leave a live gap — the GREEN-phase `check()` calls are real, specific,
and independently re-run clean by QA (10/10) — but SC-10's own verify criterion
(`grep -E "FAIL.*$c"`) can't tell "didn't exist" from "exists and is wrong," so it would have
signed off identically on a red produced by a body-less stub. **Finding (low-med, chore):**
worth a decision on whether SC-10-style receipts should require a discriminating red (e.g. a
deliberately-wrong-but-present stub) for functions being extended in place, not just added.

**check-domain.sh's relative-path base (item 7) — judged correct to leave unfixed.** Read
`_show`/`_norm` at `:970-1010` (script line numbers shift ±1 from the note's citation but the
`os.path.abspath(path)`-against-cwd calls are exactly where the note says). Confirmed via
`notes/cwd-import-bypass-2026-08-27.md`'s "Still open" section and cross-checked the claim
that Claude Code only ever sends absolute `file_path` values. No `D-NN` or `DEC` states which
base a relative target should resolve against, and every other decision in this feature
(D-02, D-03) is built on "guessing a root is worse than refusing." Picking a base here now —
cwd, the resolved harness root, or the script's own directory — would be exactly that kind of
guess, made by an agent, on an enforcement gate's write-authorization path, with no decision
backing it and no way to test it (unreachable from production). **I would not fix this.**
If it ever becomes reachable (a new caller starts sending relative paths), that's the moment
to write the `D-NN` and the test — not before.

## Stage 2 — quality / process

**Mixed-lane commit `e51b814` (item 6) — DEC-174 was not fully honoured; med, not gating.**
Tagged `[harness:t-04,t-05,t-06]` — three TEAM-lane tasks, executed by `harness-backend-dev`.
Its diff (confirmed via `git show e51b814`) touches two files DEC-174 protects:
- `test-check-state.py`: a 2-line **comment-only** reword (`factory_config.harness_root()` →
  "factory_config's own root resolver"), functionally inert.
- `test-post-merge-sweep.py`: a **substantive** fixture change — renames the env var the
  fixtures set (`CLAUDE_PROJECT_DIR` → `HARNESS_PROJECT_DIR`) and adds MARKER-file writing to
  `case_dry_run_safety`'s fixture. This is real test-oracle behaviour, changed by the team
  lane, on a file the review dispatch's own protected list ("every `test-*.py` covering one")
  and AGENTS.md's "...gate scripts, or their tests" both cover.

The plan's own lane table is where this fell through: rows for `check-state.sh`,
`check-plan-routes.py`, etc. explicitly say "and its test file with it"; the row for
`post-merge-sweep.sh` doesn't carry that phrase, so nothing in the plan's own bookkeeping
would have flagged this commit as out-of-lane. The squad's own T-21 was later created
*specifically* for this failure mode on `test-check-state.py` ("a squad repairing its own
gate through the gate it just moved is exactly the path the carve-out closes") — but T-21
only repaired the substantive fixture logic already fixed correctly upstream in the T-12
lineage; the e51b814 comment-only edit and the test-post-merge-sweep.py functional edit were
never re-routed or re-verified by a main-session-direct task. QA independently re-ran and the
resulting content is correct, so there's no live defect — but the *process* violated the
binding constraint, undetected, and the lane table has a structural gap that would let it
happen again silently. **Recommend:** extend "and its test file with it" to every
`main-session-direct` row uniformly (not selectively), and/or add a mechanical check —
commit-tag-vs-files-touched — so this is answerable from the git log next time instead of
requiring a manual diff read like this one.

## Handed to security review, not covered here
`worktree_owner`'s pointer-parsing, `checkout_relative`, and the `.git` file-vs-directory
distinction in `harness_boundary.py` are threat-modelling surface (spoofed/malformed pointer
files) — noted for `harness-security-reviewer`, not assessed here.

## Summary of findings (ranked, none gating)
1. `test-post-merge-sweep.py` functional edit + `test-check-state.py` comment edit landed via
   team lane in a DEC-174-protected path (e51b814) — **med**, process/governance.
2. Three stale comments naming the retired `CLAUDE_PROJECT_DIR` chain
   (`check-state.sh:~1143`, `check-plan-routes.py:~477`, `validate-digest.py:~815`), plus a
   fourth in `test-check-plan-routes.py:1133-1136`'s case_20 docstring — **low**, chore, no
   presence/absence pair currently catches this class.
3. SC-10's red-receipt criterion accepts an `AttributeError`-only red as equivalent to a
   behaviourally discriminating one; 3 of 4 T-01 functions got the weaker kind — **low-med**,
   chore, GREEN assertions are real so no live gap today.
4. `inject-expertise.sh`'s stderr-discard on resolver failure loses the discard-notice detail
   that `check-state.sh`/`branch-create-gate.sh` preserve — **low**, minor consistency,
   acceptable given the hook's own "always exit 0, never block" contract.

```yaml
VERDICT: PASS
DIGEST:
  headline: Resolver consolidation is behaviourally sound at all nine call sites and every fail-open is pre-existing (DEC-101) or documented (DEC-101/DECISIONS.md:1503); no must_fix, but a real DEC-174 lane breach (e51b814) and four stale-comment/weak-red process gaps go to the backlog.
  severity_max: med
  findings: 4
  must_fix: []
  spec_violations:
    - { kind: mismatch, path: .claude/skills/harness/bin/test-post-merge-sweep.py, ref: DEC-174 }
    - { kind: mismatch, path: .claude/skills/harness/bin/test-check-state.py, ref: DEC-174 }
  reviewed: "ea71a1c..9d12e3a"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Should the plan's lane table extend 'and its test file with it' to every main-session-direct row (post-merge-sweep.sh currently lacks it), and should a commit-tag-vs-files-touched check exist so a DEC-174 breach like e51b814 is machine-detectable rather than requiring a manual diff read?", blocking: false }
    - { id: Q2, question: "Should SC-10-style receipts require a behaviourally discriminating red (not just an AttributeError) when extending an existing module in place?", blocking: false }
  files_touched: [.harness/harness/features/FEAT-42-one-root-resolver/notes/review-harness-code-reviewer-2026-08-27.md]
  expertise_update: []
artifact: .harness/harness/features/FEAT-42-one-root-resolver/notes/review-harness-code-reviewer-2026-08-27.md
```
