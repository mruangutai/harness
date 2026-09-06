# QA mutation pass — BUG-1308, cycle 1

**Verdict: both unproven refusal sites are load-bearing; VL-1 is confirmed as a demonstration gap
only (integration covers the wording, unit does not). No new coverage gap rises to must-fix; one
genuine adequacy gap is worth a note (cross-section op composition, untested).**

## 1. Baseline at the pin (review_sha `4c76f0f5`)

Both run with `env -u HARNESS_AGENT_TYPE` (G-07), from the worktree root.

- `--kind unit`: exit **0**, `^FAIL ` lines: **0**, `pool: 8 workers, 28 files` — matches contract.
- `--kind integration`: exit **0**, `^FAIL ` lines: **0**, `pool: 8 workers, 46 files` — matches contract.

`git status --porcelain` on the tracked worktree: empty before and after this session (one
untouched untracked file belonging to a sibling reviewer, `notes/review-harness-ui-reviewer-c1.md`,
not mine).

## 2. Mutation proofs

Mechanism: `git worktree add` a disposable copy at
`.claude/worktrees/harness/bug1308-mutwt` (pinned at `4c76f0f5`, per G-06 — Bash `cp`
scratch-copy is unreliable session to session), mutate the copy's
`.claude/skills/harness/bin/expertise-merge.py` in place, then point tests at it: unit via a
`/tmp` copy of `test-expertise-ops.py` with `BIN_DIR` redirected (the unit loader hardcodes
`MODULE_PATH`, no env override), integration via `EXPERTISE_MERGE_BIN=<mutant path>` (the
suite already supports this env var, line 9/35). Mutant worktree removed and the tracked tree's
`git status --porcelain` reconfirmed empty after every mutation.

### Site A — `expertise-merge.py:245`, `_check_proposal_ambiguity`'s `if key in seen:` (exit 11, two ops naming one target)

Mutant: replaced the raise with `if False: pass` — duplicate-key detection neutered, second op
silently wins.

- **KILLED** by unit `case_u6` ("MergeRefusal raised" — mutant runs to completion instead,
  merging silently: `{'Patterns': [('P-02', 'two')]}`).
- **KILLED** by integration `case14` sub-case (c) — `test-expertise-merge.py:562-566` all five
  assertions redden (exit code, AMBIGUOUS TARGET, id, section, reason=), plus the sha256
  no-write invariant at line ~566 also fails since the mutant now writes the file.

### Site B — `expertise-merge.py:159-165`, `_validate_verb`'s `if verb == "merge":` (exit 12, distinct from `_malformed`)

Three mutants, each restored via `git checkout` before the next:

- **(a) exit code changed 12 → 99**: **KILLED** by unit `case_u7` ("code is 12" reddens: got 99).
  (Integration's own case for the distill-contract accepted/rewritten-verb check also reddens,
  though that is a side effect of a different assertion, not this test's own target — not
  claimed as evidence for this mutant beyond the unit kill.)
- **(b) message reworded to drop the rewrite instruction** (`"MALFORMED OPS op=merge is not a
  supported verb."`): **KILLED** by unit `case_u7` ("line names the replace plus drop rewrite"
  reddens; code check still passes).
- **(c) branch removed entirely, falls through to the unknown-verb path** (`_malformed`, still
  exit 12 via the generic path): **KILLED** by unit `case_u7` — code stays 12 (masked), but the
  message check reddens because the fallback message is `"unknown op verb 'merge'; expected add,
  replace or drop"`, which does not contain the pinned substring. This is the mutant that proves
  the message assertion is load-bearing, not the code check: code alone would have let it survive.

All three Site B mutants killed. No surviving mutant at either site — **both refusal sites are now
proven, not merely assertion-strong.**

## 3. VL-1 disposition: CONFIRMED, and it is a demonstration gap, not a protection gap

Direct test: mutated Site A's raise to keep `code=11` but strip the message to a bare
`["duplicate op target"]` (no `AMBIGUOUS TARGET`, no id, no section, no `reason=`).

- Unit suite: **stayed fully green** — `case_u6` only asserts `e.code == 11`, never inspects
  `e.lines`. Confirms the premise: the unit half of this refusal pins code only.
- Integration suite: **reddened** exactly as VL-1 predicted — `test-expertise-merge.py:562-566`,
  four of five `case14: (c)` assertions fail (AMBIGUOUS TARGET, id, section, reason=); code and
  no-write checks still pass since code stayed 11 and my mutant never got past the exit path to a
  write.

So: a message-wording-only regression at this exit-11 site is caught, but only by the integration
half. **VL-1 is accurate as stated** — the token/section/id/`reason=` wording contract for this
site rests entirely on `tests/integration/test-expertise-merge.py:562-566`; the unit assertions at
`tests/unit/test-expertise-ops.py` (`case_u6`) are code-only. Since integration is part of the
required, green matrix at this pin, this is a **demonstration gap** (the unit suite alone doesn't
prove it) rather than a **protection gap** (nothing proves it) — carry it forward as `info`, not
`must_fix`.

## 4. Adequacy: SC-11 (concurrency) and SC-12 (multi-op composition)

**SC-11** — `tests/integration/test-expertise-merge.py:811` `case_concurrent_writers` (case18).
Matches the BRIEF spec verbatim: test holds the production lock itself via
`harness_merge.acquire`, spawns an `apply` child and an `ops` child, polls both for a 2.0s hold
window asserting neither exits, then verifies both apply cleanly to disjoint entries (P-09/P-10
added, P-07 replaced) after release.

- What it would **not** catch: two concurrent `ops` writers racing on the **same** target id
  (e.g., two replaces of `P-07`). Because the lock fully serializes, the second writer would
  simply overwrite whatever the first left — there's no compare-and-swap on original text, so
  this isn't a defect the mechanism claims to prevent (D-01..D-10 don't require it); flagging it
  is informational only, not a coverage gap against a signed requirement.
- More concretely: the test only exercises **two** concurrent children. A latent defect in
  `harness_merge.acquire`'s own queuing (e.g., a third waiter starved or a lock released to two
  waiters simultaneously) would not surface with only two contenders. This is pre-existing
  `harness_merge.py` machinery, out of this diff's scope (REQ-07 signs `apply` unchanged) — noted,
  not gating.

**SC-12** — `tests/integration/test-expertise-merge.py:899` `case_multi_op_composition` (case19,
CLI, forward order only) plus `tests/unit/test-expertise-ops.py` `case_u11` (both orders,
resolver-level) and `case_u12` (two drops). All three exercise exactly **two** ops, always
within **one section** (Patterns).

- Genuine adequacy gap, not covered anywhere in either suite: **no proposal in either suite spans
  two different sections in one call** (e.g., one op on `Patterns` and one on `Gotchas` together).
  `_apply_resolved`'s `set(ops_by_section) | set(adds_by_section)` iteration and
  `_check_proposal_ambiguity`'s `(section, target)` tuple key both exist specifically to make
  cross-section composition safe (an id repeated across two different sections must NOT collide),
  but nothing exercises that path. A regression narrowing the ambiguity key to bare `target`
  (dropping the section component) would ship silently — every existing case uses ids that are
  unique across sections by convention (`P-`, `G-`, `O-` prefixes never repeat), so no existing
  fixture would redden. This is the same class P-06 in my Expertise names: one triggering leg
  (same-section duplicate) is pinned, the other (cross-section, same id) is not.
- Also untested: **three or more** ops on distinct original indices in one call (both suites cap
  at two). `_rebuild_section` walks by id via a dict lookup, not by position, so an index-based
  regression is unlikely — but two ops is the minimum needed to prove order-independence at all,
  and a subtle cumulative-index bug (if one were ever introduced) could specifically cancel out at
  n=2 and only show at n=3. Not raised as a finding since nothing in the diff suggests
  index-based bookkeeping; noted for awareness only.

I did not write new permanent tests for either gap — neither is demanded by a signed SC, and a
scratch probe (below) is sufficient to characterize them for this dispatch.

**Scratch probe confirming the cross-section gap is real** (not run against tracked files, module
loaded directly from the pinned checkout, no writes):
```
secs = {"Patterns": [("X-01", "p")], "Gotchas": [("X-01", "g")]}   # SAME id, different sections
ops  = [{"op":"replace","target":"X-01","section":"Patterns","entry":"P2"},
        {"op":"replace","target":"X-01","section":"Gotchas","entry":"G2"}]
resolve_ops(secs, ["Patterns","Gotchas"], ops)
# -> succeeds cleanly, both sections carry their own X-01 with distinct text.
# Under a mutant _check_proposal_ambiguity keyed on bare `target` (no section), this
# would incorrectly raise AMBIGUOUS TARGET (11) for a legal proposal — the real
# risk direction: a correct proposal refused, not a bad one accepted. No test in
# either suite would catch that regression; every fixture avoids id reuse across sections.
```

## 5. Per-file record (all seven named files)

1. `.claude/skills/harness/bin/expertise-merge.py` — read in full at the pin (561 lines; NOTE:
   this repo's `read`/`grep` tool index was stale for this file and returned a cached 293-line
   pre-checkout summary on the first two calls — worked around with `sed`/`grep` via bash
   directly against the checked-out bytes for every citation in this note). Yielded: the two
   mutation targets (`:159-165`, `:245`), `resolve_ops` and its five helper functions, `cmd_ops`.
2. `tests/unit/test-expertise-ops.py` — read in full (293 lines, 16 cases). Yielded: `case_u6`,
   `case_u7` as the two cases mutation-probed above; confirmed `case_u11`/`case_u12` are the two-op,
   single-section ceiling for SC-12's unit half.
3. `tests/integration/test-expertise-merge.py` case11..case20 — read case14 (`:520-566`), case15,
   case18 (`:811-885`), case19 (`:899-935`), case20 header. Yielded: case14(c) as the wording
   contract for VL-1, case18/case19 as the SC-11/SC-12 CLI evidence.
4. `.claude/skills/harness-distill/SKILL.md` — diffed `origin/main..4c76f0f5`. Yielded: T-03's
   contract realignment (`add | replace | merge | drop` vocabulary, `merge` named as authoring-only,
   the six refusal codes listed, the `ops` invocation shape) — matches the code exactly, no drift.
5. `.harness/harness/docs/SPEC.md` §5.3 — diffed. Yielded: the `ops` subcommand section citing
   `_validate_target_section:170-178`, `_rebuild_section:269-283`, `_resolve_all:254-266`,
   `_check_caps:310-317`, `_validate_verb:157-167`, `cmd_ops:484-533`. Cross-checked every one of
   these line numbers against `grep -n '^def '` on the pinned file — all six are accurate to
   within the function's actual start line; the two refusal-table ranges (`:203-212` MISSING
   TARGET, `:213-251` AMBIGUOUS TARGET) span both raise sites correctly (`_resolve_replace_or_drop`
   at 203 and `_check_proposal_ambiguity` at 240). No documentation defect found.
6. `.harness/harness/docs/DECISIONS.md` DEC-219 — read the added entry. Yielded: matches the
   mechanism-as-designed section of this dispatch verbatim (section+id keying, one base snapshot,
   order-independent rebuild, `merge` refused as authoring-only, three new refusal codes). No
   discrepancy against the shipped code.
7. `.harness/harness/docs/DECISIONS-INDEX.md` — read the added row (`DEC-219 @6901 [...]`).
   Yielded: the ruling summary matches DEC-219's own text; `@6901` line anchor checked against
   `DECISIONS.md`'s actual heading line for the entry — consistent.

## Findings

| id | severity | scenario | file:line |
|---|---|---|---|
| F-01 | info | Unit `case_u6` pins exit-11 code only for the proposal-duplicate-target site; a message-wording-only regression there is invisible to the unit suite alone (confirmed by direct mutation) and relies solely on integration `case14:(c)`. Demonstration gap, not protection gap — integration is required and green. | `tests/unit/test-expertise-ops.py:90-97` vs `tests/integration/test-expertise-merge.py:562-566` |
| F-02 | info | No test in either suite composes ops across two different sections in one proposal; a regression narrowing `_check_proposal_ambiguity`'s key from `(section, target)` to bare `target` would wrongly refuse legal same-id-different-section proposals, undetected by any existing fixture (all fixtures use section-prefixed, globally-unique ids). | `.claude/skills/harness/bin/expertise-merge.py:240-249` |

Neither is `must_fix`: F-01 is already covered by the required integration kind; F-02 is a
plausible-but-unexercised edge with no signed SC demanding it and no evidence of an actual
regression risk in the diff (the key is correctly section-qualified today).
