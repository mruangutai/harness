# Receipt — harness-backend-dev — altitude-eng

**RULING: D-11 STANDS, UNCUT — but D-12's union is NARROWED to its true consumer set, and T-04
SHRINKS for 3 of its 4 validator sweeps.** On the merits, and measured: three of the five
non-hook-bound scripts (`check-plan-routes.py`, `layout_migration.py`, and effectively
`validate-feature-json.py`) already execute **exclusively in CI** (`.github/workflows/tests.yml:101,153,231`,
each stamped "PROMOTED" against issue #133/DEC-183/FEAT-54 B-5) — a fresh full clone, never a linked
worktree, so the sparse-corpus problem this feature exists to close cannot occur on their live
execution path today. Only `check-state.sh` (`.claude/commands/harness.md:12`, "Run at every
`/harness entry`") and `board_lifecycle.py` (via `ship`, `gh-sync.py:2230`,
`DECISIONS.md:6193` "run once per feature, inside `ship`") execute **live, inside a feature's own
worktree**, and both must keep doing so: that is the only mechanism grading the ACTIVE in-flight
feature before it lands (contract fact 5). Moving audit *execution* off the worktree, as the design
comment literally proposed, would not remove any already-ruled mechanism (D-11/D-12 already make the
*read* git-anchored and invocation-site-independent) and would either duplicate what CI already does
(for the three CI-only scripts) or break `ship`'s own moment-of-shipping comparison (for
`board_lifecycle.py`) with no compensating benefit. **Not smaller** — see item 3's count.

## 1. Per-site classification (LOOKUP / AUDIT / third class)

**Whole-corpus, non-hook-bound (the D-11 five):**

| Site | Class | Why |
|---|---|---|
| `check-state.sh` (all per-feature INVs below) | **AUDIT, per-feature, live** | reads every feature's *own* record for self-consistency; runs live at `/harness entry` (`harness.md:12`) **and** in CI (`tests.yml:305`, "PROMOTED", FEAT-54 B-5) |
| `check-state.sh` INV-24 (`:1605-1704`) | **AUDIT, cross-feature** | two features cannot claim one fleet issue — needs the WHOLE set simultaneously, not reducible to one feature |
| `board_lifecycle.py` `_feature_dirs`/INV-26-class (`:472-477`, docstring names it "the SAME glob shape check-state.sh's own INV-24/INV-26 invariants read") | **AUDIT, per-feature, live (via `ship`)** | station-vs-plan comparison, one feature at a time, invoked from inside that feature's own worktree at ship time |
| `check-plan-routes.py` discovery (`:678-693`) | **AUDIT, per-feature, CI-only** | route/shape check per plan; `tests.yml:153` is its sole mechanical invocation ("NOTHING mechanical ran it" before promotion, `tests.yml:104`) |
| `check-plan-routes.py` INV-collision (`:798-861`) | **AUDIT, cross-feature, CI-only** | "TWO UNBUILT FEATURES MUST NOT CLAIM THE SAME `INV-NN`" (`:798`) — needs the whole corpus, same shape as INV-24 |
| `validate-feature-json.py` `discover_paths` (`:40-54`) | **AUDIT, per-feature, CI-only** | schema check per file; invoked directly in CI (`tests.yml:101`) plus its own unit test |
| `layout_migration.py` `_evidence` (`:180-202`) | **AUDIT, cross-feature, CI-only** | legacy-vs-migrated MIXED-state detection needs the corpus-wide ratio, not one feature; `tests.yml:231` |

**Hook-bound (contract fact 1's nine registrations) and other named sites:**

| Site | Class | Why |
|---|---|---|
| `merge-gate.py:132-142` `feature_for(branch)` | **LOOKUP** | "which feature owns this branch" — needs the whole set for the anti-double-claim property (`:172-174`); hook-bound (PreToolUse Bash), immediacy essential — blocks THIS merge |
| `check-domain.sh:1898-1923` `_hardlink_plan` | **THIRD CLASS — path-only identity lookup, not reducible to either given class.** It resolves `(st_ino, st_dev)` identity, which git can never supply at any ref (arch-eng receipt Q5a, `harness_boundary.py` has no inode concept). It is not an AUDIT (no self-consistency claim — it answers "which plan.yaml IS this hardlink", a single-target question) and not a plain LOOKUP either (a git-resolved LOOKUP like `feature_for` could in principle answer from history; this one structurally cannot). Ruling: **a LOOKUP with a path-provider constraint** (D-04's own framing) — same shape as `feature_for` (needs the corpus set to search), but D-04 already forces it path-only; no new class name is needed, D-04 covers it |
| `check-domain.sh:1069` `SWEEP_GLOBS`/`_SWEEP_PATTERNS` (`:1052-1069`), consumed `:2147-2151` | **AUDIT, bounded, hook-bound, immediacy essential** | "was this specific just-written file shape-compliant" — bounded by a high-water mtime mark (`:1070-1078`), never a cold full-corpus resweep; cannot move to CI (the entire point is to catch a bad write AT WRITE TIME); already CONVERTED under T-06 (framefix-eng), unaffected by this ruling |
| `check-domain.sh:752`/`:780` `feature_checkout_guard`/`claim_checkout_guard` | **LOOKUP** (worktree/claim-set resolution, not a corpus-record audit) — hook-bound, DENIES, immediacy essential; already corrected by T-17/D-15 |
| `check-domain.sh:2150` worktree report tier | **LOOKUP** (same identity question as above, REPORTS not DENIES) — already corrected by T-17/D-15 |
| `branch-create-gate.sh:89` flow existence (`ls -d "$root/.harness/harness/features/${flow}*"`) | **LOOKUP, single-target** | "does feature X exist", not a corpus sweep — one name match, no cross-feature correlation; hook-bound (PreToolUse Bash), already ruled by T-16 |
| `quarantine.py`, `feature_json_write.py`, `feature_schema.py`, `factory_decompose.py`, `feature-worktree.py`, `layout_fixtures.py`, `harness_boundary.py` | **genuinely single-feature / path-logic / fixture-only** | unchanged from arch-eng receipt Q1 (`notes/receipt-harness-backend-dev-arch-eng.md:13-19`), re-verified at the cited lines; no reclassification |
| `inject-expertise.sh`, `validate-digest.py`, `dispatch-guard.sh` | **out of corpus-reader scope** | each resolves at most one feature from a path/text field and enumerates nothing (`BRIEF.md:83-84`) |
| `gh-close-gate.sh`, `plan-sign-gate.sh` | **out of corpus-reader scope** | carry no feature-record path at all (`BRIEF.md:85-86`) |

## 2. Execution location + enforcing instrument, per AUDIT

**The five relocated scripts split by their measured invocation site, not by a new self-refusal
mechanism:**

| Script | Executes | Enforcing instrument | In-flight feature grading |
|---|---|---|---|
| `check-state.sh` | live at `/harness entry` **and** CI | D-11's relocation (`root = corpus_root(cwd)`) + D-02's intrinsic refusal; git-anchored read makes the OUTCOME invocation-site-independent (measured, item 4) | D-12's cwd-union, invoked because the check runs inside the feature's own worktree — this IS why it must stay reachable there |
| `board_lifecycle.py` | live, inside the shipping feature's own worktree (`ship`) | same as above | same — `ship` is the moment the union matters most |
| `check-plan-routes.py` | **CI only, today** (`tests.yml:153`) | D-02's intrinsic refusal as pure insurance against a future ad hoc worktree run; CI is always a full checkout (REQ-10), so relocation is inert-but-harmless there | **not needed** — CI has no in-flight-feature concept; cross-feature INV-collision check (`:798-861`) is about LANDED features only |
| `validate-feature-json.py` | **CI only, today** (`tests.yml:101` + its own unit test) | same as above | not needed, same reason |
| `layout_migration.py` | **CI only, today** (`tests.yml:231`) | same as above | not needed, same reason |

**Hazard (a), hook-bound audits, addressed per site:** `check-domain.sh`'s SWEEP_GLOBS report tier
is the only genuinely hook-bound AUDIT-shaped site; it is bounded-mtime, immediacy-critical, and
already CONVERTED under T-06 (framefix-eng digest #2) — it was never a candidate for CI relocation
and this ruling changes nothing about it. `check-state.sh`/`board_lifecycle.py` are NOT
hook-registered (contract fact 2), so "a hook cannot be told to run elsewhere" does not apply to
them; their invocation sites are a command file (`harness.md:12`), a CI workflow step, and a Python
call inside `gh-sync.py ship` — all three are ordinary process launches the harness already controls,
not `${CLAUDE_PROJECT_DIR}`-bound hooks.

**Hazard (b), immediacy:** for `check-state.sh`/`board_lifecycle.py`, no loss — nothing moves, they
keep running live. For the three CI-only scripts, no loss either, because they were never running
live to begin with (measured above); this feature does not change their invocation site, only makes
their behaviour correct IF ever run ad hoc inside a worktree.

**Contract fact 5, discharged:** the active in-flight feature is graded by `check-state.sh` at its
own `/harness entry` and by `board_lifecycle.py` at its own `ship`, both invoked from inside that
feature's worktree, both using D-12's cwd-union. Nobody else grades it, and nobody needs to — moving
either off the worktree would leave the in-flight feature ungraded until CI/next-landing, which is
the exact regression the dispatch says fails the bedrock rule's availability half. This ruling does
not do that; it keeps both live.

**Rated alternatives, per the dispatch's list:**

| Instrument | Rating | Why |
|---|---|---|
| Self-refusal on `worktree_owner()` at script top | **rejected** | there is nothing to refuse — the git-anchored read is correct from inside a worktree; a self-refusal would break the live feedback these two scripts exist to provide, for no safety gain |
| Scope split: local mode (active feature only) vs. repo-wide mode | **rejected as a new mechanism** | already achieved for free — D-12's union already scopes the in-flight feature's OWN entry locally, while the rest of the sweep reads the ref-resolved (repo-wide) set; a second explicit mode would duplicate this |
| CI job | **already exists** for 3 of 5 (measured); **advisory-only, not adopted** for `check-state.sh`/`board_lifecycle.py`, because it cannot replace the live invocation (contract fact 5) — it could *additionally* run, but the marginal value is a rounding error against the measured per-invocation cost (item 4: ~17-40 ms) |
| Prose in a command file | **rejected as sole instrument** | `harness.md:12`'s prose already names the command; the enforcing instrument is the git-anchored read, not the sentence pointing at it (same reasoning D-13 already applied to dispatch declarations) |

## 3. Reader ledger, re-derived by task

| Bucket | Tasks | Detail |
|---|---|---|
| UNNECESSARY | none | no already-ruled task's mechanism is invalidated by the altitude answer |
| SHRINKS | **T-04** | drop the `bases[feat]`/cwd-union scaffolding for `check-plan-routes.py`, `validate-feature-json.py`, `layout_migration.py` (3 of its 4 sweeps) — they run CI-only (measured, `tests.yml:101,153,231`) and have no in-flight-feature concept to union in. Keep the full union only for `board_lifecycle.py`, the fourth, which runs live at `ship`. **D-12** is rescoped in the same motion: its union applies to `check-state.sh`, `board_lifecycle.py`, `merge-gate.py`, `check-domain.sh` — the four consumers reachable from inside a live worktree — never to the three CI-only validators |
| UNCHANGED | T-01, T-02, T-03, T-05, T-06, T-07, T-08, T-09, T-10, T-11, T-13, T-14, T-15, T-16, T-17 | D-11's relocation, D-15's three-site fix, D-04's provider split, the frame-line rulings (framefix-eng) and the denial-tier widening (denialtier-eng) all stand as already ruled |
| NEW | none as a task; **one new decision** (see below) | no CI wiring, no dual-mode split script is added — the "smaller" alternative the operator invited turned out to already be true for 3 of 5 scripts by existing practice, not by new work this batch adds |

**New decision needed (D-16, for pm to transcribe):** *choice:* D-12's caller-side union applies
only to `check-state.sh`, `board_lifecycle.py`, `merge-gate.py` and `check-domain.sh` — the four
consumers a live agent invokes from inside its own worktree — and not to `check-plan-routes.py`,
`validate-feature-json.py` or `layout_migration.py`, which execute exclusively in CI today
(`.github/workflows/tests.yml:101,153,231`) and therefore never see an in-flight feature to union in.
*because:* CI runs a fresh full checkout (REQ-10's identity-behaviour case), so `corpus_root(cwd)`
already resolves to a complete tree with nothing sparse to work around; building the union path into
these three sweeps anyway would be dead code exercised by no live caller, the same "no closed set"
reasoning D-02 already applies to per-site opt-in refusals. If a future change makes any of the three
runnable from inside a live worktree, this decision is the one to revisit.

**Count, and the "smaller" answer:** 0 tasks removed, 0 tasks added, 1 task (T-04) narrowed, 1
decision (D-12) rescoped, 1 decision (D-16) added recording why. Comparing this to "fail-closing
fifteen sweeps in place" (D-11's own rejected alternative, ~25 independently-maintained branches, 21
inside `check-state.sh` alone): this altitude answer is smaller than THAT alternative, same as D-11
already was — but it is **not smaller than the currently-signed-off plan** (D-11+D-12+T-03/T-04 as
written pre-this-batch). It is a refinement inside the same task, not a cut. Stated plainly per the
operator's invitation: the altitude change does **not** hold in the form "the worktree stops reading
the corpus for audit purposes entirely" — for `check-state.sh` and `board_lifecycle.py` the worktree
must keep reading it, because nothing else grades the in-flight feature; for the other three, the
worktree was never really reading it live in the first place, so there was nothing to stop.

## 4. LOOKUP ruling (`merge-gate.py feature_for`) — measured

**Ruling: resolve the corpus SET through git (a single enumeration), read CONTENT locally at the
owner root.** Never route every candidate through a per-record `git show`. Measured on this host,
`/Users/molchairuangutai/GitHub/harness` at `HEAD`, N=20 (after 1 warm-up), 79 `feature.json` records
(`/tmp/measure_lookup.py`, not committed):

| Shape | Mechanism | mean | p50 |
|---|---|---:|---:|
| A — per-record `git show <ref>:<path>` × N | the "route every candidate through `corpus_read`" shape cycle-1's PF-fbf676b warned about | 930.27 ms | 926.69 ms |
| B — single `git ls-tree` enumeration + local `open()` of every resolved `feature.json` | enumerate through git, read content locally at the owner root | 16.69 ms | 16.79 ms |
| C — candidate-narrowed: plain `glob.glob` + `open()`, no git subprocess at all | what `merge-gate.py:134` does TODAY, pre-change | 2.29 ms | 2.26 ms |

Shape A confirms D-11's own figure (13.69 ms × N ≈ 930 ms/79 ≈ 11.8 ms/record here; both runs are the
same order of magnitude and both land at roughly "about a second," matching PF-fbf676b's ~1.2 s
estimate at 88 features). Shape B is 56× cheaper than A and costs less than the denial-tier hook's
own measured 18.5–23.6 ms interpreter floor (denialtier-eng digest) — noise against a cost the hook
already pays. Shape C is cheapest but is what today's code does BEFORE this feature, reading straight
off a checkout that will become sparse.

**Which prior position is superseded, and in what part:** cycle-1's Q4 ruling (narrow `merge-gate` to
avoid the ~1.2 s cost, PF-fbf676b) is **superseded in its mechanism, not its motive.** The motive —
don't pay shape A's cost — was and remains correct. The mechanism it chose — narrow the SCOPE to one
candidate feature, sacrificing the anti-double-claim property the operator now insists on — was the
wrong remedy for that motive, because shape B delivers the same avoidance of shape A's cost (16.69 ms,
not 930 ms) while keeping the full-corpus correctness property intact. **`feature_for` therefore
enumerates the corpus set via `corpus_features(provider="history")` (a single git-anchored
enumeration, so a sparse worktree cannot silently undercount) and reads each resolved `feature.json`
with a plain local `open()` at the resolved owner root** (never sparse, D-03) — not `corpus_read`'s
history-first `git show` per file, which would reproduce shape A. This is a genuine third position,
distinct from both prior rulings: it keeps D-11-era completeness (unlike the narrowed shape) and
avoids D-11-era cost (unlike routing through `corpus_read`). T-05's intent needs this exact wording;
"keeps `corpus_read` for ref provenance" (planfix-eng ruling #4) is corrected to name shape B, not a
per-record `corpus_read` call.

## 5. D-02 consequence — paste-ready

**Append to D-02's `because:`, verbatim, no edits needed:**

> Because every corpus read that resolves through git enumerates a fixed ref, and git has no partial
> view of a ref it can resolve, the short-corpus state — a reader whose corpus root resolved
> correctly and which still saw fewer feature directories than the corpus set — cannot arise on a
> read path that goes through git. The intrinsic refusal in `corpus_features` is therefore insurance
> against a reader that reaches for the filesystem instead of git, not the mechanism that makes the
> corpus complete: it is a seatbelt, and it stays, because a reader can still be written or
> miswritten to bypass the corpus API entirely (D-05's own residual names exactly this bypass), and
> when that happens the refusal is the only thing that still fires. But the reason a correctly-written
> reader never sees a short corpus is git's completeness at the resolved ref, not this refusal, and
> the record should say so rather than leave the refusal looking load-bearing for a state its own
> correct callers cannot reach.

**Criteria to re-scope, so each grades something reachable:**

| Criterion | Current shape | What it should grade instead |
|---|---|---|
| **SC-04** | asserts the short-corpus `N of M` refusal fires for "every corpus-sweeping reader the reader ledger classifies," including `check-domain.sh` (T-06) | exclude `check-domain.sh` by name, exactly as merge-gate.py is already excluded (`BRIEF.md:148-151`) — planpanel2 finding 3 already proved this fixture is structurally unreachable under D-04's `provider="path"` binding for that reader, since path-mode enumeration has no independent "should be there" side (framefix-eng ruling #1). `check-domain.sh`'s provider=path sweep is graded instead by SC-15's four outcome clauses, which test denial/report behaviour directly rather than synthesizing an N-of-M state that provider=path cannot produce |
| **REQ-04** | states the refusal as the corpus-root-short predicate, unqualified | add one sentence pointing at D-02's now-stated residual: the refusal is the last-line defence for a reader that bypasses the git-anchored API, not a state a correctly-calling reader can reach — same wording, no new mechanism |
| **SC-05** | the no-corpus-root/no-resolvable-ref refusal path | unchanged — this is exactly the "corpus root or ref itself could not be resolved" case D-02's seatbelt legitimately guards; nothing about the git-completeness argument touches it |
| **SC-09** | reader inventory instrument, OPEN by design | unchanged by D-02's wording; separately, its ledger description should note T-04's SHRINK (3 of 4 validators drop the union) so a reader of SC-09 does not expect union behaviour where none exists |
| **SC-14** | frame-line presence/content | unchanged — frame emission is orthogonal to the completeness argument; already ruled by framefix-eng |

## Sources

`plan.yaml` (tasks/decisions/panel), `BRIEF.md`, `notes/receipt-harness-backend-dev-arch-eng.md` (Q1
reader ledger, reused for the un-reclassified sites), `runs/planpanel2-validator/digest.md` (finding
3, SC-04/T-06), `runs/planfix-eng/digest.md` (rulings 4/7, LOOKUP tension), `runs/framefix-eng/digest.md`
(frame rulings, SWEEP_GLOBS conversion), `runs/denialtier-eng/digest.md` (interpreter floor,
denial-tier measurement methodology reused for item 4's comparison baseline). Source files read
directly with citations: `check-state.sh` (INV enumeration, 828 lines read), `merge-gate.py:119-194`,
`check-domain.sh` (:739-818, :1039-1078, :1889-1933, :2139-2163), `branch-create-gate.sh` (full),
`check-plan-routes.py` (:669-693, :798-861), `validate-feature-json.py` (:1-54),
`board_lifecycle.py` (:461-483), `layout_migration.py` (:179-202), `.github/workflows/tests.yml`
(:75-311), `.claude/commands/harness.md:12`, `.harness/harness/docs/DECISIONS.md:6193-6220`.
Peer facts (invocation/CI-placement inventory) cross-checked against, not duplicated from,
`CorpusPlan.AltitudeRuling.AltitudeInvocation`'s receipt at
`notes/receipt-harness-dev-ops-altitude-eng.md`.

## Return contract

```yaml
VERDICT: PASS
DIGEST:
  headline: "D-11 stands uncut: three of the five relocated scripts already execute CI-only (measured in .github/workflows/tests.yml), so the altitude question is answered by existing invocation practice, not new work — T-04 SHRINKS (drop the cwd-union for its 3 CI-only sweeps, keep it for board_lifecycle.py), D-12 is rescoped to name its true 4-consumer set, one new decision (D-16) records why, and merge-gate.py's LOOKUP is measured and re-ruled: enumerate through git (16.69ms), read content locally at the owner root — never per-record git show (930ms) and never the narrowed single-candidate shape that broke the anti-double-claim property. Items 1-5 in full above the Sources section."
  tests_added: 0
  suite: pass
  task: none
  files_touched: [".harness/harness/features/FEAT-58-corpus-outside-worktree/notes/receipt-harness-backend-dev-altitude-eng.md"]
  blocked_on: none
  open_questions:
    - { id: Q1, question: "D-16 (new) and the D-12 rescoping both need pm to fold into plan.yaml; neither changes any task's traces:, but D-16 should sit adjacent to D-12 in the decisions list. Confirm pm takes both in the same pass as the other pending must_fix items from planfix-eng/framefix-eng/denialtier-eng.", blocking: false }
    - { id: Q2, question: "T-04's SHRINK (dropping cwd-union for check-plan-routes.py/validate-feature-json.py/layout_migration.py) is contingent on those three staying CI-only invocations. If a future change wires any of them into a live per-agent path (e.g. a pre-flight check inside /harness entry), D-16 says to revisit — should T-04's intent carry that contingency explicitly, or is D-16 sufficient as the trigger record?", blocking: false }
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-58-corpus-outside-worktree/.harness/harness/features/FEAT-58-corpus-outside-worktree/notes/receipt-harness-backend-dev-altitude-eng.md
```
</content>
