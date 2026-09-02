# Receipt — harness-dev-ops — FEAT-51 panel fix (F-2 containment, F-3 grade)

**BLUF: both findings fixed. `cmd_adopt` now realpaths `--file`, parses it against a single
shared containment regex (`_quarantine_containment`) also used by `cmd_discard`, and refuses
(exit 2) anything off-shape. `cmd_adopt` regraded 3→4 via two extractions
(`_adopt_target`/`_refuse_adopt`/`_adopt_payload`). All 26 pre-existing checks plus 8 new
checks (4 new cases) pass; no existing assertion was weakened.**

## F-2 — containment

Shared helper `_quarantine_containment(realpath)` at
`.claude/skills/harness/bin/quarantine.py:48` replaces `_QUARANTINE_CHILD_RE` and the old
`_canonical_target_for`-in-`cmd_adopt` arithmetic. Shape enforced:
`<root>/.harness/<repo>/features/<feature>/quarantine/<one writer dir>[/<basename>]`,
anchored (`$`), matched against `os.path.realpath`. `cmd_discard` requires `basename is
None` (target is exactly the writer dir); `cmd_adopt` requires a basename that's a member of
`inflight_registry.CANONICAL_ARTIFACTS` (imported, not restated), and derives `canonical`
from the parsed `(repo, feature)`, never by `..`-walking.

**No existing assertion was weakened.** Fixing the printed `ADOPTED` line required a design
choice, not a test change: `_adopt_target` now returns both the plain abspath (`given`,
used for reads and the `ADOPTED ... FROM ...` message) and its realpath (`resolved`, used
only for the containment parse and the refusal's `resolved to:` line) — because realpath on
macOS normalizes `/var` → `/private/var`, and the pre-existing case1/case3 message
assertions expect the caller's own (non-realpath) path echoed back.

### RED proof (against `/tmp/quarantine-prefix.py`'s sibling copy, `QUARANTINE_BIN` pointed
at an unmodified pre-fix `quarantine.py` copied into the bin dir so its `harness_boundary`
sibling import resolved)

- **Case 9** (outside any quarantine dir): `exits 2` assertion — FAIL on old code.
  `plan-merge.py`'s own `require_destination` happened to refuse it (`REFUSED: ... is not a
  plan.yaml under a features directory`), but for a reason unrelated to quarantine.py's own
  containment — old `quarantine.py` itself never checked. Canonical stayed unchanged only
  because plan-merge's downstream guard caught this specific case by coincidence.
- **Case 10** (feature-A-quarantine symlink onto feature B): **both** `exits 2` and
  `feature B's canonical feature.json is byte-unchanged` FAIL on old code — old code printed
  `ADOPTED .../FEAT-99-fixture/quarantine/feature.json FROM .../quarantine/writer/subdir/
  feature.json`, exit 0, and genuinely overwrote feature B's `feature.json`. This is the
  live containment hole the panel found, reproduced end to end.
- **Case 11** (nested one dir too deep under `quarantine/`): `exits 2` FAIL — same
  plan-merge-side-effect refusal as case 9, not a real quarantine.py refusal.
- **Case 12** (symlink inside a legal quarantine dir escaping via realpath): `exits 2` FAIL —
  old code adopted through the symlink (`ADOPTED .../plan.yaml FROM .../quarantine/
  harness-backend-dev-12345678/plan.yaml`), exit 0. (The two byte-unchanged assertions in
  this case happened to pass on old code too — plan-merge's union-merge of the escape file's
  garbage content round-tripped to byte-identical output; the `exits 2` assertion is the
  discriminator.)

## F-3 — grade

Measured with `python3 .agents/skills/harness/bin/code-grade.py .claude/skills/harness/bin/
quarantine.py`.

| | cyclomatic | cognitive | ABC | driver | grade |
|---|---|---|---|---|---|
| before (baseline) | 7 | 10 | 22.5 | cognitive+abc | **3 (FAIL)** |
| after containment only (before extraction) | 6 | 9 | 22.7 | abc | 3 (FAIL) |
| after extracting `_adopt_target`/`_refuse_adopt`/`_adopt_payload` | 4 | 3 | 9.8 | abc | **4 (PASS)** |

Every other function in the file is grade 4 or 5 (full listing in the tool's own output;
`PASSING: 13`, no `FAIL` lines).

## Verify

```
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-51-claude-code-lifecycle-safety
python3 .agents/skills/harness/bin/test-quarantine.py; rc=$?; echo "rc=$rc"
```
→ 34 `PASS` lines (26 pre-existing + 8 new across cases 9–12), trailing `PASS
test-quarantine.py`, `rc=0`.

## Cross-tree check

`git -C /Users/molchairuangutai/GitHub/harness status --porcelain` shows only unrelated
untracked entries (BUG-1030, BUG-1080, BUG-251, daily log, two grilling notes) — nothing
under `.claude/skills/harness/bin/` or `FEAT-51-claude-code-lifecycle-safety`. No cross-tree
leak from this work.

## Scope note

A scratch copy of the pre-fix binary was placed at `.claude/skills/harness/bin/
quarantine-prefix-scratch.py` (inside the worktree) purely so its `harness_boundary`/
`harness_merge`/`inflight_registry` sibling imports would resolve for the RED run; it was
`rm`'d before the fix landed and is not present in the final diff (`git diff --stat` shows
only `quarantine.py`, `test-quarantine.py`, plus the main session's concurrent `plan.yaml`
edit — not mine).

## Cycle 2 — root-anchoring, kill the second derivation

**BLUF: all three blocking defects fixed. `_quarantine_containment(root, realpath)` now
requires `realpath` resolve *under* `root` (realpath-vs-realpath, via `os.path.relpath`,
never abspath-vs-realpath) before it ever tests the quarantine shape; `cmd_list` derives its
`canonical=` field through that same helper and `_canonical_target_for` is deleted; cases 9
and 11 are retargeted at `feature.json` so their `exits 2` assertion can only be quarantine.py's
own refusal, case 12's two non-discriminating byte-unchanged assertions are deleted with
reasons recorded below, and a new case 13 proves the root-anchoring fix end to end. 35 PASS
lines (was 34), `rc=0`, no weakened assertion.**

### Defect A — root-anchoring

`_QUARANTINE_PATH_RE` lost its `(?:^|/)`/`$` anchors and its `.search`; it is now matched with
`.fullmatch` against `os.path.relpath(realpath, os.path.realpath(root))` inside
`_quarantine_containment(root, realpath)` (`quarantine.py:50`). A `rel` that is `..`, starts
with `../`, or is absolute means `realpath` fell outside `root` and the parse refuses
regardless of whether the tail looks quarantine-shaped — this is what closes the "file merely
LOOKS quarantine-shaped under a foreign root" hole. Both sides are realpath'd (never abspath)
specifically to dodge the macOS `/var`→`/private/var` trap the dispatch flagged:
`_resolve_root` returns abspath and `tempfile.mkdtemp()` fixtures live under `/var/folders/...`,
so an abspath(root)-vs-realpath(file) comparison would have false-refused every fixture.
`_adopt_target` and `cmd_discard` both now call `_quarantine_containment(root, ...)`, so both
subcommands share the anchoring, not just adopt.

**RED proof (case 13, standalone harness against a saved copy of the cycle-1 binary — the
delivered F-2 fix, unanchored regex — before this cycle's edit):**

```
=== cycle-1 (quarantine-c1-scratch.py) ===
rc= 0
stdout: ADOPTED /var/.../quarantine-A-y-.../.harness/harness/features/FEAT-51-.../feature.json FROM /var/.../quarantine-A-x-.../.harness/harness/features/FEAT-51-.../quarantine/w/feature.json
stderr:
victim unchanged: False

=== cycle-2 (quarantine.py) ===
rc= 2
stdout:
stderr: REFUSED: adopt only accepts one of plan.yaml, BRIEF.md, feature.json, STATE.md, ...
  resolved to: /private/var/.../quarantine-A-x-.../.harness/harness/features/FEAT-51-.../quarantine/w/feature.json
victim unchanged: True
```

A file physically rooted at an attacker-controlled `root_x`, shaped exactly like
`<root>/.harness/harness/features/FEAT-51-claude-code-lifecycle-safety/quarantine/w/feature.json`,
adopted with `--root` pointed at an unrelated `root_y` holding a real `feature.json`: cycle-1
binary adopts it onto `root_y`'s canonical file (exit 0, victim overwritten — the regression
the dispatch named); cycle-2 refuses it (exit 2, victim untouched). This is now permanent as
**case 13** in `test-quarantine.py` (two checks: `exits 2`, canonical byte-unchanged), verified
against `quarantine.py` in the full suite run below. The scratch binary used for this proof
(`quarantine-c1-scratch.py`, a byte-for-byte copy of the cycle-1 delivered file, made solely so
its sibling imports resolved) was `rm`'d before this receipt was written and is not in the
final diff.

### Defect B — one derivation, not two

`_canonical_target_for` (the `..`-walking arithmetic `cmd_list` alone still used) is deleted.
`cmd_list` now calls a new `_canonical_for_listing(root, path)` (`quarantine.py:98`), which
calls `_quarantine_containment(root, os.path.realpath(path))` — the identical parse
`_adopt_target` uses — and builds `canonical=` from the parsed `(repo, feature, basename)`,
never by walking `..`. **My own call on the unparseable case**, as invited by the dispatch: an
entry `_quarantine_containment` can't resolve (e.g. a symlink whose realpath escapes its
quarantine dir) prints `canonical=<unresolvable>` rather than a guessed path. Reasoning: `list`
is documented as read-only and must keep exiting 0 on everything the glob turns up — printing a
wrong-but-plausible path would be worse than a placeholder, since an operator reading `list`'s
output to decide what to `adopt` could otherwise be told a false landing site for exactly the
entry that most needs their attention. Case 7 (list changes no file) and case 8 (empty list)
pass unchanged — neither one exercises an unresolvable entry, so `<unresolvable>` is new,
unexercised-by-suite behavior; it is documented in `_canonical_for_listing`'s docstring.

### Defect C — cases 9 and 11 made discriminating; case 12 trimmed

Cases 9 and 11 are retargeted from `plan.yaml` to `feature.json`. `feature.json` takes
`_adopt_payload`'s `harness_merge.locked_update` arm, which has no downstream guard of its own
(unlike `plan.yaml`'s `plan-merge.py apply`, whose `require_destination` was masking these two
cases in cycle 1) — so on any binary lacking quarantine.py's own containment, `feature.json`
adoption cannot be refused by anything but quarantine.py itself.

**RED proof, retargeted cases 9 and 11 against three binaries** (baseline = `git show
HEAD:.claude/skills/harness/bin/quarantine.py`, the pre-any-containment code the cycle-1
receipt's own RED proofs used; cycle-1 = the delivered F-2 fix; cycle-2 = this file):

```
case 9 (outside quarantine dir)      baseline: rc=0 unchanged=True (WRONG canonical path — ADOPTED .../features/feature.json, one level too shallow, exit 0)
                                      cycle-1:  rc=2 unchanged=True (own REFUSED)
                                      cycle-2:  rc=2 unchanged=True (own REFUSED)

case 11 (nested one dir too deep)    baseline: rc=0 unchanged=True (WRONG canonical path — ADOPTED .../quarantine/feature.json, exit 0)
                                      cycle-1:  rc=2 unchanged=True (own REFUSED)
                                      cycle-2:  rc=2 unchanged=True (own REFUSED)
```

On baseline, `exits 2` is genuinely RED (baseline exits 0 both times) — and it is RED for
quarantine.py's own missing containment alone, since `feature.json` never touches
`plan-merge.py`. The `canonical unchanged` assertion happens to also hold on baseline, but only
because baseline's blind `..`-arithmetic computes the WRONG location for an out-of-shape input
(one level shallow / one level too deep) — it still adopts, just onto the wrong path, which is
itself evidence of the bug, not evidence of correctness. `exits 2` is the assertion that
discriminates; `canonical unchanged` is retained as a secondary, non-vacuous check (the intended
canonical genuinely never changes on any of the three binaries under test, for whichever
reason).

**Case 12 — two assertions deleted, not strengthened.** The cycle-1 receipt already recorded
that case 12's `escape target byte-unchanged` and `canonical byte-unchanged` assertions passed
on the pre-fix baseline too (plan-merge's own schema refusal on the escape file's non-plan
content left both targets untouched before quarantine.py's own containment was ever reached).
Retargeting to `feature.json` would not manufacture a genuine plan-merge-only failure mode to
discriminate against, and no other realistic operation makes an escaped-symlink adoption
corrupt a specific byte range without also getting caught by `exits 2` first — so per the
dispatch's explicit allowance, both are **deleted**, leaving `case12: a symlink whose realpath
escapes the quarantine dir exits 2` as the sole, real discriminator for this case (comment
left in place in `test-quarantine.py` explaining the deletion).

### F-3 — grade, before/after

Measured with `python3 .agents/skills/harness/bin/code-grade.py .claude/skills/harness/bin/
quarantine.py`.

| function | cyclomatic | cognitive | ABC | driver | grade |
|---|---|---|---|---|---|
| `_quarantine_containment` (cycle 1, 1-arg) | — | — | — | — | not separately measured (part of a smaller function pre-root-anchoring) |
| `_quarantine_containment` (cycle 2, root-anchored) | 4 | 4 | 8.4 | cognitive+abc | **4 (PASS)** |
| `cmd_list` (cycle 1) | — | — | — | — | grade 4/5 (unmeasured in cycle-1 receipt; not a target function then) |
| `cmd_list` (cycle 2) | 4 | 4 | 16.4 | cognitive+abc | **4 (PASS)** |
| `_canonical_for_listing` (new, cycle 2) | 3 | 3 | 7.1 | — | **5 (PASS)** |
| `_adopt_target` (cycle 2) | 3 | 4 | 11.4 | cognitive+abc | **4 (PASS)** |
| `cmd_adopt` (cycle 1 → cycle 2, unchanged) | 4 | 3 | 9.8 | abc | **4 (PASS)** — identical to cycle 1's row, root-anchoring added zero branches to `cmd_adopt` itself (it lives inside `_adopt_target`/`_quarantine_containment`) |
| `cmd_discard` (cycle 2) | 4 | 4 | 12.0 | cognitive+abc | **4 (PASS)** |

`PASSING: 13`, no `FAIL` line anywhere in the file. `_adopt_target`'s cognitive rose from 3
(cycle-1 baseline before extraction, per that receipt's own table) — it stayed at grade 4
without a further extraction; splitting it further would separate `given`/`resolved`
construction from the containment call for no readability gain, since the whole function is
four lines of sequential resolution.

### Verify

```
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-51-claude-code-lifecycle-safety
python3 .agents/skills/harness/bin/test-quarantine.py; rc=$?; echo "rc=$rc"
```
→ **35 PASS lines** (delta +1 from cycle 1's 34: −2 case 12 byte-unchanged deletions, +2 case
13, cases 9/11 unchanged at 2 assertions each just retargeted), trailing `PASS
test-quarantine.py`, `rc=0`.

**Named per the dispatch's acceptance clause:** case 1's fifteen-id union check —
`case1: canonical carries all fifteen task ids` — **PASS**. Case 2's byte-identical approval
carry-forward — `case2: the canonical approval block survives adoption byte-identical` —
**PASS**. All 26 of cycle 1's original checks pass unchanged; none was touched by this cycle's
edits (only cases 9, 11, 12 were touched, and none of those 26 is among them).

### Cross-tree check (re-run at the end of this cycle)

`git -C /Users/molchairuangutai/GitHub/harness status --porcelain` shows only unrelated
untracked entries (BUG-1030 review note, BUG-1080 qa digest note, BUG-251 directory, a daily
log, two grilling notes) — nothing under `.claude/skills/harness/bin/` or
`FEAT-51-claude-code-lifecycle-safety`. No cross-tree leak from this cycle's work either.

### Scope note, cycle 2

Two scratch files were used for RED proofs and both were `rm`'d before this receipt was
written: `quarantine-c1-scratch.py` (a byte-for-byte copy of the cycle-1 delivered file, for
defect A's RED proof) and `quarantine-baseline-scratch.py` (`git show
HEAD:.claude/skills/harness/bin/quarantine.py`, for defect C's RED proof against the true
pre-any-containment baseline). `git status --porcelain -- .claude/skills/harness/bin/` after
cleanup shows only `quarantine.py` and `test-quarantine.py` modified — no scratch file survives
in the final diff.
