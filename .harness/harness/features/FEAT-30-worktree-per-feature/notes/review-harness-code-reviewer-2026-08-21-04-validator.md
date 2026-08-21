# Code review — FEAT-30-worktree-per-feature — base 49c528a..a76d69a

**VERDICT: PASS.** Stage 1 (spec compliance, all 12 SCs) is satisfied with no scope creep, no
omission, and every `SC` marked `verify: inspection` (SC-06) cited with `file:line`. Stage 2 turned
up two novel medium findings and confirmed all four established ones — none reach `high`, none are
`must_fix`.

## Stage 1 — spec compliance

Every changed file traces to a `T-0N` task and its `REQ`. Spot-checked SC-02 (merge-base, not
branch name — `test-feature-worktree.py:244-250`), SC-05/SC-02c (16-agent grant parity —
`test-check-domain.py:1660-1837`), SC-07 (both routes: `feature-worktree.py:203-221` GATE 2 and
`bash-write-guard.sh` T-05's `remove`/`prune` extension), SC-08 (lock + union —
`expertise-merge.py`), SC-09 (179/0 unit, 213/0 integration, cited from
`runs/2026-08-21-01-validator/digest.md`, not re-run). No finding here.

**SC-06 (inspection), verified:** `harness-orchestrator.md:25` — "Your dispatch names an absolute
worktree path. That is your checkout for the whole run." (2 mentions, a rule not a mention).
`harness.md` section "0b. Cut the worktree" (7 mentions, names the CLI and the layout). Both pass.

**Commits since the last pin:** base..a76d69a contains five `[harness:human]` commits
(`bbee125`..`fbb3bc0`) — this is not new, it is DEC-174's carve-out working as designed: the
enforcement-layer tasks (T-03/T-04/T-05, and T-07/T-09's orchestrator-facing edit) are
`main-session-direct` by plan, so a human applied them and they inherit no prior review — which is
exactly why they are this review's job. All are in scope and were read.

## Stage 2 — established findings

**1. T-04's carve-out contradiction (not T-05's — see correction).** The contradictory instruction
lives in **T-04's** intent (`plan.yaml`, the block ending "DO NOT TOUCH bash-write-guard.sh line
545 ... it is already correct" immediately followed by the ask for a paired refuse case at the
same depth), not T-05's — T-05's own intent text is entirely about the HEAD-move rule and the
Bash-route forced-removal refusal and never mentions this carve-out. Confirmed by direct read of
`bash-write-guard.sh:687` (`if re.match(r"^\.claude/worktrees/", rel): continue`, unconditional,
depth-agnostic, pre-dating this feature) and of the delivered test,
`test-bash-write-guard.py:588-611` (`run_worktree_deep`'s docstring states the contradiction
first, then asserts the carve-out IS blanket rather than fabricating the impossible refuse case).
**Affirmed**, with one addition: this carve-out was already exactly this permissive before FEAT-30
(no segment count in the original regex either) — FEAT-30 did not widen the exposure, it only made
the widening it inherits *explicit and pinned* rather than untested. `enforcement-layer`, `info`,
does not gate.

**2. T-03's red proof is inert at HEAD.** Confirmed by tracing `worktree_owner` and
`checkout_relative` (`harness_boundary.py`): `WORKTREES_SEGMENT` is consulted only inside
`worktree_owner`'s `legitimate` computation, never inside `checkout_relative`'s core walk (which
finds the checkout via the git pointer file, independent of the constant's value). The 16+16
grant-parity cases (`test-check-domain.py:1660-1837`) exercise only paths physically nested inside
the fixture root, where `select_base` always resolves `base = abs_root` regardless of
`legitimate` — so mutating `WORKTREES_SEGMENT` cannot touch the mechanism those 32(+ related)
cases depend on; it only reddens the handful of legitimacy/out-of-place cases, which is enough to
flip the verify's exit code non-zero without exercising what T-03's own intent says the mutation
must prove ("only possible if the in-worktree half of every pair really is exercising the worktree
path"). **Affirmed as T-04 working as designed, not a regression** — the shipped behavior is
correct and a real break in `checkout_relative` (mutate it to `return None`) does redden the
grant-parity cases, per the operator's own count. What is genuinely stale is the *signed verify
clause*, which discriminates on the pre-T-04 mechanism and happens to still pass by an
accident of collateral damage. `enforcement-layer`, `low`, does not gate. Remedy if picked up:
re-sign T-03's verify against `checkout_relative`, not `WORKTREES_SEGMENT`.

**3. F-ALT-1 (REFUSE_ON_DIRTY / REQUIRE_LANDED / UNION_APPLY) — refutation checked, holds.** I
traced all three flags by hand rather than re-executing the mutation (my Bash access is
write-denied on every write-shaped command, including in scratch — `bash-write-guard.sh` refused
even an `rm -rf` under `/private/tmp/...` with "harness-code-reviewer is READ-ONLY", so I could not
build a mutated copy on disk to re-run against). Static trace: `REFUSE_ON_DIRTY=False` and
`REQUIRE_LANDED=False` each skip an entire gate block wholesale (`feature-worktree.py:212-224` and
`:229-260`), which the SC-07 dirty-tree cases and the SC-04 landed/differs cases
(`test-feature-worktree.py`, `case_landed_refuse_then_allow`, `case_landed_differs`,
`case_dirty_tree_refuse`) directly exercise; `UNION_APPLY=False` takes the whole-file-overwrite
`else` branch (`expertise-merge.py:172-175`), which `case_divergent_text` and `case_cap_overflow`
(exit 7 / exit 8) directly depend on going through the `if UNION_APPLY:` branch to trigger. All
three are reachable, behaviorally covered, non-vacuous. **Refutation confirmed**: coverage is
behavioural, not by-name, and that is a legitimate answer to "is there a checked-in proof."
`squad-appliable`, `info`, does not gate. Flagging the limitation on my own re-run rather than
silently trusting: this is inherited, not independently re-measured by me.

**4. `expertise-merge.py:37` accepts `[A-Za-z]{1,3}` where `check-expertise.sh:44` requires
`[A-Z]{1,3}`.** Confirmed byte-for-byte. Failure scenario: a distilling agent's scratch entries
file carries a lowercase or mixed-case id (typo, or a model producing `- ab-01: ...`);
`expertise-merge.py apply` parses it as a valid entry (`ENTRY_RE` matches), cap-counts it, and
writes it to the actual `.harness/expertise/<agent>.md` file with exit 0 and `ADDED ab-01` on
stdout — a clean success signal. The only thing that later catches this is a **manual** step:
`harness-distill/SKILL.md` item 4 instructs the agent to separately run `check-expertise.sh <file>`
and fix violations before returning. There is no automatic call from `expertise-merge.py` into
`check-expertise.sh`, so a distilling agent that returns without running item 4 leaves a
format-invalid entry live in a file injected into every future spawn of that persona. Narrowing
`expertise-merge.py`'s regex to match would be the fix, not a regression, since it is the *merge
tool* that is over-permissive relative to the *format contract's own checker* — the same file
already keeps its `CAPS` dict in cross-checked agreement with `check-expertise.sh`'s (via
`test-expertise-merge.py`'s case 8, per the file's own header comment) but never did the same for
`ENTRY_RE`. `squad-appliable`, `med`, does not gate (mitigated by the manual SKILL.md step, and no
observed instance in the shipped file).

## Stage 2 — new findings

**5. `expertise-merge.py:111-135` `compute_union` silently drops one of two entries that share an
id within a single proposal file.** Conflict detection compares only `eid in base_by_id` (the
file-on-disk); a **second** occurrence of the same id inside the *proposal itself*, with different
text, is checked only against `seen` (line 134) and is silently discarded — no `CONFLICT` line, no
non-zero exit, and the final `ADDED <eid>` line looks like a clean success reporting only the
surviving entry. Concrete trigger: a distilling agent's own scratch file accidentally reuses an id
across two different new entries (a plausible authorial slip, not a two-writer race — the
lock/base-comparison path already correctly catches the true concurrent-writer case, which is what
SC-08 actually specifies). This is the exact failure mode the tool's own docstring says it exists
to prevent ("a loud refusal beats a second silent loss") — it just does not prevent it for this one
shape of duplicate. **Corroborates `F-C` from `runs/2026-08-21-02-eng/digest.md`** (the eng
simplify pass already flagged `compute_union`'s `seen` dedup as untested and declined to add a
test, since a test addition was out of scope for that step) — this is the same gap, independently
re-derived, with the concrete failure scenario the eng note did not spell out. Not previously
tested (`test-expertise-merge.py` has no duplicate-id-within-one-proposal case; grepped, zero hits
for "duplicate"). `squad-appliable`, `med`, does not gate (narrow trigger, single-run scope, no
cross-run data loss).

**6. `feature-worktree.py:229-261` GATE 3 (`REQUIRE_LANDED`) passes silently when the artifact
directory exists but contains zero files.** `os.path.isdir(artifact_abs)` guards against a missing
directory (tested: `case_no_artifact_directory`, exit 5), but if the directory exists and is empty
— or has been emptied by some prior edit while the directory itself survives — `os.walk` at line
238 iterates zero times, `landed_fail` never becomes `True`, and `cmd_remove` proceeds straight to
`git worktree remove` with no stdout at all from GATE 3 and no signal that "landed" was never
actually checked for any content. Concrete scenario: `.harness/harness/features/<id>/` is created
(e.g. scaffolded, or its contents removed by an in-flight edit) but never populated before `remove`
is invoked — SC-04's own wording ("the check names the paths it verified") has nothing to name and
says nothing, while the removal happens anyway. Not covered by any existing case — grepped
`test-feature-worktree.py` for "empty"/zero-file variants of GATE 3, zero hits; the three GATE-3
cases present are missing-directory, one-file-unmerged, and one-file-merged. `squad-appliable`,
`med`, does not gate (in practice a feature that reaches `remove` has almost always written
BRIEF.md/plan.yaml/etc. into that directory well before then, so the trigger is narrow, but the gap
is real and untested).

## What I could not do

My Bash access denies every write-shaped command unconditionally for this role (confirmed live:
`rm -rf` under my own scratchpad, outside the repo, was refused with "harness-code-reviewer is
READ-ONLY"). Findings 3 and, partially, 5/6 are corroborated by static code trace rather than by
re-running a mutation, unlike the operator's own measurements cited in the dispatch. Where that
matters I said so inline rather than presenting a traced conclusion as an executed one.
