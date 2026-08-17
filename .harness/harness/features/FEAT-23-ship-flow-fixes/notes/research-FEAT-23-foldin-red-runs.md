# Red runs for the pre-signature fold-in — 2026-08-17

**BLUF: exactly ONE `verify:` clause changed text in this fold-in — T-05's — and it was executed
fresh, in both directions, against the clause exactly as it now stands in `plan.yaml`. The other
five clauses are byte-unchanged and keep their existing receipts.**

## Which clauses changed, stated per clause so nothing is ambiguous

| Task | Clause text changed? | Receipt |
|---|---|---|
| T-01 | **No.** Only `intent:` changed (A-01, A-02, A-05) | existing, `research-FEAT-23-verify-red-runs.md` |
| T-02 | **No.** Only `intent:` changed (MF-1, MF-2) | existing, same file |
| T-03 | **No.** Only `intent:` changed (MF-1 ripple, A-06) | existing, same file |
| T-04 | **No.** Only `intent:` changed (MF-1 ripple, peer A re-anchoring) | existing, same file + `research-FEAT-23-453-station.md` |
| T-05 | **YES — three case labels added** | **this file** |
| T-06 | **No.** Only `intent:` changed (A-03, ui Q1) | existing, `research-FEAT-23-453-station.md` |

The three added labels, byte-exact as the clause greps them (`PASS` then TWO spaces then the label,
`test-gh-board.py`'s `check()` format, which T-05's intent pins):

```
board-station outside a harness root writes nothing and exits 0
board-station with github.sync false writes nothing and exits 0
board-station exits 0 when set_station raises a non-BoardError exception
```

They were added for A-04 (two specified exit-0 branches with no case) and for MF-3 (the widened
catch, which was otherwise asserted in prose and tested by nothing).

**A-04's third branch — `github.repo` absent or carrying no slash — was DECLINED a case, and the
reason is stated rather than left as silence.** It is the same code path as the sync-off branch: one
config read, one prefixed line, exit 0, no board call, all of it inside item 4's single
precondition block. The sync-off case executes that block and asserts its outcome, so a regression
that broke the exit-0 contract there would redden it. What the declined case would add is
discrimination between two arms of one `if`, which is a smaller defect than the cost: every pinned
label is a byte-exact string the clause reddens on if reworded, and each one needs its own red run
in both directions. Three added labels is where the value stops paying for the pinning. **If the
operator disagrees, the cheap remedy is a fourth label, not a rewrite** — the branch is already
specified in item 4, so only the case and the conjunct are missing.

## Half one — the clause CAN FAIL

**Failing state 1, the real tree.** The clause's head conjunct was run against the working tree at
`e26e628`, where `board-station.py` does not exist:

```
T-05: .claude/skills/harness/bin/board-station.py does not exist
exit=1
```

**Failing states 2–5, the label ladder.** Conjunct 1 exits before the ladder is reached, so the
ladder was run on its own with the suite output supplied as a shell variable — the same capture
shape the shipped clause uses (`out=$(...)`, then a `say()` that reprints it), so each `grep` gets
its own stream and no one-shot process substitution can invert the ladder (O-03). Five mutants of a
seven-case green output, each observed:

```
== no-root label deleted     :: T-05: the no-harness-root case did not pass or did not run     exit=1
== sync-off label deleted    :: T-05: the sync-off case did not pass or did not run            exit=1
== non-BoardError deleted    :: T-05: the non-BoardError case did not pass or did not run      exit=1
== non-BoardError case FAILs :: T-05: the non-BoardError case did not pass or did not run      exit=1
== no-root label REWORDED    :: T-05: the no-harness-root case did not pass or did not run     exit=1
== all seven PASS, suite rc=1:: T-05: the suite exited 1                                       exit=1
```

**The reworded mutant is the important one.** A label rewritten to "board-station when no ancestor
holds the manifest writes nothing and exits 0" — same behaviour, different words — reddens. So the
conjunct discriminates the exact pinned string, which is why T-05's intent pins all seven labels
byte-for-byte rather than describing them.

**Honest note on the `^FAIL` conjunct.** The "case FAILs" mutant above reddened on the *label*
conjunct, not on the `^FAIL` conjunct, because flipping `PASS` to `FAIL` also removes the label the
ladder greps for. To prove the `^FAIL` conjunct itself is reachable and live, a separate fixture was
run in which all seven labels PASS and an eighth, unpinned case FAILs:

```
FAIL  board-station some other case: got exit 3
T-05: a case failed
```

So a regression in a case the clause does not name by label still reddens.

## Half two — the clause CAN PASS

The full ladder was run against a seven-case green output in the format T-05's intent prescribes:

```
== green :: T-05 label ladder GREEN     exit=0
```

This is the half FEAT-22 got wrong in the other direction, so it is recorded explicitly: the clause
passes against the text the intent prescribes, and reddens against every state it exists to catch.
A clause that cannot pass is the same defect as one that cannot fail.

**Not re-run, and stated rather than implied:** the two conjuncts of T-05 that surround the ladder —
the `run-unit-tests.sh` registration grep and the `--kind unit` drift-detector run — are
byte-unchanged by this fold-in. Their receipts, including the drift detector proved by mutation
(`rc=0` unmutated, `rc=2 MISCONFIGURED` with one on-disk test file unlisted), stand at
`research-FEAT-23-453-station.md` and were not repeated here.

## The commands, verbatim

The fixture, the five mutants and the ladder harness, exactly as run. No file was written — the
suite output is carried in a shell variable, because `bash-write-guard.sh` denies `harness-pm` a
redirect outside its domain and a redirect-based probe was blocked on this session before being
rewritten to this shape.

```bash
GREEN=$(cat <<'EOF'
PASS  board-station moves the named issue to the named station
PASS  board-station with no board configured writes nothing and exits 0
PASS  board-station reports a BoardError on stderr naming issue and station and exits 0
PASS  board-station rejects a missing argument with exit 2
PASS  board-station outside a harness root writes nothing and exits 0
PASS  board-station with github.sync false writes nothing and exits 0
PASS  board-station exits 0 when set_station raises a non-BoardError exception
7 passed, 0 failed
EOF
)
M_NOROOT=$(printf '%s\n' "$GREEN" | grep -v "outside a harness root")
M_SYNCOFF=$(printf '%s\n' "$GREEN" | grep -v "github.sync false")
M_NONBOARD=$(printf '%s\n' "$GREEN" | grep -v "non-BoardError")
M_FAIL=$(printf '%s\n' "$GREEN" | sed 's/^PASS  board-station exits 0 when set_station raises a non-BoardError exception/FAIL  board-station exits 0 when set_station raises a non-BoardError exception: got exit 1/')
M_REWORD=$(printf '%s\n' "$GREEN" | sed 's/^PASS  board-station outside a harness root writes nothing and exits 0/PASS  board-station when no ancestor holds the manifest writes nothing and exits 0/')

ladder() {
  out="$1"; rc="${2:-0}"
  say() { printf '%s\n' "$out"; }
  say | grep -qF "PASS  board-station moves the named issue to the named station" || { echo "T-05: the station-write case did not pass or did not run"; return 1; }
  say | grep -qF "PASS  board-station with no board configured writes nothing and exits 0" || { echo "T-05: the unconfigured-board case did not pass or did not run"; return 1; }
  say | grep -qF "PASS  board-station reports a BoardError on stderr naming issue and station and exits 0" || { echo "T-05: the board-failure case did not pass or did not run"; return 1; }
  say | grep -qF "PASS  board-station rejects a missing argument with exit 2" || { echo "T-05: the usage case did not pass or did not run"; return 1; }
  say | grep -qF "PASS  board-station outside a harness root writes nothing and exits 0" || { echo "T-05: the no-harness-root case did not pass or did not run"; return 1; }
  say | grep -qF "PASS  board-station with github.sync false writes nothing and exits 0" || { echo "T-05: the sync-off case did not pass or did not run"; return 1; }
  say | grep -qF "PASS  board-station exits 0 when set_station raises a non-BoardError exception" || { echo "T-05: the non-BoardError case did not pass or did not run"; return 1; }
  say | grep -E "^FAIL" && { echo "T-05: a case failed"; return 1; }
  test "$rc" = 0 || { echo "T-05: the suite exited $rc"; return 1; }
  echo "T-05 label ladder GREEN"; return 0
}
ladder "$GREEN";     ladder "$M_NOROOT";  ladder "$M_SYNCOFF"
ladder "$M_NONBOARD"; ladder "$M_FAIL";   ladder "$M_REWORD"
ladder "$GREEN" 1
```

The ladder body is the shipped clause's label section verbatim, with `exit 1` replaced by `return 1`
so one shell can run seven states, and with `out=$(python3 "$T" 2>&1); rc=$?` replaced by the fixture
— `board-station.py` and its test file do not exist yet, so there is no suite to run. The head
conjunct that covers that absence was run against the real tree, unmodified:

```bash
B=.claude/skills/harness/bin/board-station.py
test -f "$B" || { echo "T-05: $B does not exist"; exit 1; }
```

The `^FAIL` reachability fixture is `$GREEN` with an eighth line appended:
`FAIL  board-station some other case: got exit 3`.

## What was verified at source during the fold-in, and is therefore not narration

- `cmd_abandon`'s early exit is a **conjunction** — `rec["milestone"] is None and not rec["issues"]`
  at `gh-sync.py:607`, observed at `e26e628`, and `gh-sync.py` is byte-identical across
  `b7ae135..HEAD`. `cmd_ship`'s is `rec["milestone"] is None` at `:670`. A-01's premise holds and
  T-01 item 4 now states the write structurally instead of gating on a milestone.
- The symbols peer finding A's re-anchoring depends on exist: `_apply_parent_rule` (`:162`), and the
  `parent_origin == "created"` gate inside `cmd_abandon` (`:631`) and `cmd_ship` (`:681`). D-05's
  `because:` and T-04's DEC-196 body now cite those symbols; no line number survives in either.
- `feature-schema.json` types `github.attached` as **array of string**, and `test-gh-sync.py`'s own
  abandon fixture already writes `["T-01"]`. T-01's intent still prescribes `attached true`, which
  is schema-invalid — **left standing deliberately**, because it is peer finding K and the operator
  holds it. Recorded here so it is not read as an oversight.
- **MF-1's task count, recomputed from each task's own `files:` block via `yaml.safe_load` of
  `plan.yaml`.** Granted `.claude/skills/harness/bin/**`: T-01, T-05 — **2 tasks**. Ungranted under
  `.claude/` (`skills/**/SKILL.md`, `commands/**`, which `team-config.yaml` grants to no lane —
  its only `.claude/` write grants are the two `skills/harness/bin/**` entries at `:161` and `:203`):
  T-02, T-03, T-06 — **3 tasks**. Outside `.claude/` entirely: T-04 (`.harness/harness/docs/**`,
  documentor). The BRIEF's earlier phrasing attached "three ... write there" to the *granted* path,
  which inverted MF-1's argument; corrected at `BRIEF.md` MF-1 to name the three NOBODY-resolved
  tasks explicitly. `plan.yaml` never carried the count and was not touched.
- `test-check-plan-routes.py` case 20 does scan every non-test `.py`/`.sh` in `bin/` for a logical
  line naming `.harness` beside a filesystem predicate, and it does sit in `INTEGRATION_SCRIPTS`.
  Peer finding F's premise holds. **No edit was made for it** — it is the operator's to route.

---

# Peer fold-in — the six remaining architecture findings — 2026-08-17

**BLUF: exactly ONE `verify:` clause changed text in this pass — T-02's — and it was executed fresh
in THREE states, including the case-sensitivity near-miss the previous lead flagged as a trap. The
other five findings (F, K, H, I, J) are plan-text only: no clause text moved for any of them, so
none required a receipt. The five other clauses are byte-unchanged and keep their existing receipts.**

The two bullets immediately above this section were true when written — F and K were then unrouted
and deliberately left standing. Both are now folded (T-05 item 4a, T-01's fixture paragraph). The
bullets are kept rather than rewritten, per rule 15; this sentence is the correction.

| Task | Clause text changed? | Receipt |
|---|---|---|
| T-01 | **No.** `intent:` only (peer K fixture) | this file, no new run required |
| **T-02** | **YES — one conjunct added** | **this section, three states** |
| T-03 | **No.** `intent:` only (peer H, peer I) | this file, no new run required |
| T-04 | **No.** `intent:` only (peer H, peer J) | this file, no new run required |
| T-05 | **No.** `intent:` only (peer F item 4a) | its own section above |
| T-06 | **No.** untouched this pass | `research-FEAT-23-453-station.md` |

## The literal, pinned once and checked mechanically

The conjunct greps, and T-02's intent prescribes, the same string:

```
four separate, parallel, read-only dispatches
```

**The trap and how it was closed.** The peer digest suggested `grep -qF "separate read-only
dispatch"`, but the intent's existing sentence spells it `SEPARATE` in capitals, and `grep -qF` is
case-sensitive — applied verbatim, that clause could never pass. A NEW lowercase literal was pinned
instead, stated in the intent in the file's own capital-pinning convention ("must contain this
literal string, byte-exact, because the verify greps for it"), leaving the existing `SEPARATE`
sentence untouched and unmatched by any grep. Byte-identity of the two halves was checked in code,
not by eye: the grep argument was extracted from the loaded `verify:` string by regex and compared
with `==` against the line extracted from the loaded `intent:` string. Result `BYTE-IDENTICAL: True`.

## The clause was run as it loads from disk, not as retyped

`yaml.safe_load(plan.yaml)` → T-02's `verify:` written verbatim to `clause.sh` → `bash clause.sh`
with cwd set to a scratch root holding `.claude/skills/harness-simplify/SKILL.md`. This doubles as
the parse check: the clause that ran is the clause a lead would carry.

**Isolation matters here and is the reason for the fixture.** T-02's first conjunct is
`test -f "$S" || exit 1` and the skill does not exist in the tree, so a red run on the real tree
would exit on line 2 and prove nothing about the new conjunct. Every fixture below satisfies EVERY
pre-existing conjunct — frontmatter, four `## REUSE|SIMPLIFICATION|EFFICIENCY|ALTITUDE` headings,
the source-note filename, "plan surface", "code surface", and neither forbidden string — and differs
only in the discipline sentence.

## Three states, observed

```
STATE 1-absent   exit 1 :: T-02: the skill does not pin the dispatch discipline; the literal
                           <four separate, parallel, read-only dispatches> is absent, so a
                           one-reviewer checklist would pass
STATE 2-nearmiss exit 1 :: (same echo)
STATE 3-exact    exit 0 :: T-02 GREEN
```

- **State 1** carries "Each angle is a separate read-only dispatch, run in parallel" — semantically
  the discipline, lexically not the pinned string. Red. This is the shape peer D exists to catch: a
  skill that reads plausibly while the four-reader rule is unpinned.
- **State 2** carries `four SEPARATE, PARALLEL, READ-ONLY dispatches` — the exact case-flip trap.
  Red, which is the proof that the clause discriminates the byte-exact string and therefore that the
  intent's pinned spelling is load-bearing rather than decorative.
- **State 3** carries the byte-exact literal. `T-02 GREEN`, exit 0 — the CAN-PASS half, which also
  proves the fixture satisfies all eight other conjuncts, so states 1 and 2 failed on the NEW
  conjunct alone and on nothing else. Their echo text confirms it independently.

Each run's combined stdout+stderr was written to its own file (`out-1-absent.txt`,
`out-2-nearmiss.txt`, `out-3-exact.txt`) and read back, rather than piped to `head`/`tail` (G-03).

## The commands, verbatim

```python
import yaml, re, subprocess
cur = yaml.safe_load(open('.harness/harness/features/FEAT-23-ship-flow-fixes/plan.yaml'))
t   = [x for x in cur['tasks'] if x['id'] == 'T-02'][0]
open(R + 'clause.sh', 'w').write(t['verify'])          # R = the scratch root
g      = re.search(r'grep -qF "([^"]*dispatches)"', t['verify']).group(1)
pinned = [l.strip() for l in t['intent'].splitlines()
          if l.strip() == 'four separate, parallel, read-only dispatches']
assert pinned == [g]                                    # printed BYTE-IDENTICAL: True
for name, disc in states.items():                       # the three sentences above
    open(R + '.claude/skills/harness-simplify/SKILL.md', 'w').write(base % disc)
    r = subprocess.run(['bash', R + 'clause.sh'], cwd=R, capture_output=True, text=True)
```

## Plan-text-only findings — stated explicitly, because "no receipt" must not be inferred

**F, K, H, I and J changed `intent:` prose and decision-body prose only. No `verify:` clause text
moved for any of them, so the operator's red-run bar does not attach and no new receipt exists or is
owed.** Where each landed is in the returning DIGEST, by file and line.

## Structure re-checked after the edits, not assumed

- `check-plan-routes.py` on `plan.yaml`: `0 violation(s)`, exit 0.
- `yaml.safe_load` parses the file; `approval:` reads `status: pending`, `approved_by: none`,
  `date: none`, and `BRIEF.md`'s `## Approval` reads `status: pending`.
- All six task `status:` values are `pending`; `depends_on` is `T-01 []`, `T-02 []`, `T-03 [T-02]`,
  `T-04 [T-03, T-06]`, `T-05 []`, `T-06 [T-03, T-05]` — unchanged, and no `T-04 → T-01` edge was
  added (leave-listed).
- Clause line counts after the pass: T-01 9, T-02 **12** (was 11), T-03 15, T-04 8, T-05 18, T-06 13
  — the single added line is T-02's new conjunct. `plan.yaml` is untracked at `HEAD`, so no
  `git show` baseline exists; the five unchanged clauses were compared against the pre-edit reads of
  this session and every edit made was an exact-string replacement inside an `intent:` block.
