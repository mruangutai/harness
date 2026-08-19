# Receipt — harness-backend-dev — FEAT-24 T-02 fix cycle c5

## Scope

Two `must_fix` items from the panel digest (`runs/2026-08-19-9-validator/digest.md`), against
`factory_config.py` and `test-factory-config.py` only. No commit made — tree left uncommitted.

## FIX 1 — SC-06 coverage: two uncovered `raise` branches

Added two cases to `test-factory-config.py`, inserted between the existing "(ii) a failing remote
read raises..." block and "(iii) never falls back to a checkout", both using
`patched_file_at_ref` and a distinctive `default_branch` per P-01 (avoiding "main" collisions with
fixed prose):

- `product_config raises naming repo, path and ref when the remote content is not JSON`
- `product_config raises naming repo, path and ref when the remote content is a JSON list, not a
  mapping` (chose a list as the non-mapping shape)

Each asserts, as **separate** boolean checks (not one concatenated substring): the exception type
is `fc.FleetError` (not a bare `Exception`), `"mruangutai/harness" in str(exc)`,
`".harness/harness.json" in str(exc)`, and the distinctive ref (`trunk-not-json` /
`trunk-not-mapping`) `in str(exc)`.

### Reddening proof

**Case 1 (`not JSON`)** — mutated `factory_config.py:283-289`, replacing the `except (ValueError,
TypeError) as e: raise FleetError(...)` body with `doc = {}` (swallowing the parse failure instead
of raising). Ran the suite:

```
FAIL  product_config raises naming repo, path and ref when the remote content is not JSON
1 of 81 FAILING.
```
Isolated — no other case's name appeared in the FAIL set.

**Case 2 (`not a mapping`)** — restored, then mutated `factory_config.py:290-294`, replacing the
`if not isinstance(doc, dict): raise FleetError(...)` body with `doc = {}`. Ran the suite:

```
FAIL  product_config raises naming repo, path and ref when the remote content is a JSON list, not a mapping
1 of 81 FAILING.
```
Isolated.

### Restoration

sha256 before any mutation: `ff0fc89ca2cd3b38a3e8917d36cd70b15045e84e89f54bf49518dce73361cb1a`
sha256 after `git checkout --` restoring following case 1's mutation: same hash (confirmed before
case 2's mutation was applied).
sha256 after `git checkout --` restoring following case 2's mutation:
`ff0fc89ca2cd3b38a3e8917d36cd70b15045e84e89f54bf49518dce73361cb1a` — identical.
`git diff --exit-code -- .claude/skills/harness/bin/factory_config.py` → exit 0.
`git status --porcelain -- .claude/skills/harness/bin/factory_config.py` → empty.

Reconciled with FIX 2: FIX 1 leaves `factory_config.py` byte-identical to `efaddcf` at the end of
step 1, by design (per the prescribed order). FIX 2's edit to `:165` is applied ONLY in step 2,
after this restoration proof — so "byte-identical" describes the state at the end of FIX 1, not
the final state after FIX 2.

## FIX 2 — `:165`'s `next_step` sent the operator to a destination this diff itself rejects

Reviewed `RAISED_MESSAGES` consumers (`test-factory-config.py:193, 204, 244, 280-284`) before
editing near it: it is only checked for count (`>= 9`) and C-3 format (contains em-dash, no
"FleetError"/"Traceback" literal) — never for specific substrings. The `:165` message text is
free to change without touching that assertion.

Grepped for the old ok-line label before touching it: `"(8b) the next_step mentions
repos[].board"` appears nowhere in `plan.yaml` or `check-state.sh` — only in
`test-factory-config.py` itself, which this fix edits directly.

### The edit — one hunk, `factory_config.py:162-167`

```python
    if "board" in data:
        raise FleetError(
            "fleet key invalid", "board",
            f"a whole-fleet board key is no longer read from here — each repository declares "
            f"its own board remotely, in its own .harness/harness.json under github.board; "
            f"remove board from {path}",
        )
```

New `:165` message, verbatim (as it renders for a real `path`):

> `fleet key invalid: board — a whole-fleet board key is no longer read from here — each
> repository declares its own board remotely, in its own .harness/harness.json under
> github.board; remove board from <path>`

`git diff` on `factory_config.py` confirmed to be exactly this one hunk (pasted below).

### Discriminating substring at `:225`

Chosen substring: `"whole-fleet board"`.

`grep -c "whole-fleet board" .claude/skills/harness/bin/factory_config.py` → **1** (only the new
`:165` message; the per-entry message at `:191-193` uses `github.board` / `.harness/harness.json`,
neither of which is unique per the task's own note — `whole-fleet board` is unique to the
top-level case).

`test-factory-config.py:224` (`"invalid: board —" in str(e)`) left untouched, as required.
`test-factory-config.py:225` rewritten:

```python
check("(8b) the next_step names the whole-fleet key, not repos[].board",
      "whole-fleet board" in str(e), str(e))
```
Comment at `:219-223`(now `:219-226`) rewritten to explain the new substring's discriminating
property (why `github.board`/`.harness/harness.json` alone would not discriminate, since both
appear in the per-entry message too).

Confirmed the old assertion reddened against the new message BEFORE rewriting the test (RED
proof, not just asserted): ran the suite with `factory_config.py:165` already edited and the old
`"repos[].board" in str(e)` assertion still in place:

```
FAIL  (8b) the next_step mentions repos[].board
        fleet key invalid: board — a whole-fleet board key is no longer read from here — each repository declares its own board remotely, in its own .harness/harness.json under github.board; remove board from /var/folders/.../fleet.yaml
```

Then rewrote the assertion to the new substring; suite returned to green.

## `factory_config.py` final diff (one hunk)

```diff
@@ -162,8 +162,9 @@ def load_fleet(path=FLEET_PATH):
     if "board" in data:
         raise FleetError(
             "fleet key invalid", "board",
-            f"the board is per-repository now — move it under each repos entry as "
-            f"repos[].board in {path}",
+            f"a whole-fleet board key is no longer read from here — each repository declares "
+            f"its own board remotely, in its own .harness/harness.json under github.board; "
+            f"remove board from {path}",
         )
```

## Verify

T-02's verify block (cross-checked verbatim against `plan.yaml:367-388` — matches) final line:

```
T-02 GREEN
```

Full suite (`run-unit-tests.sh`): every listed test file reports `PASS`, `test-factory-config.py`
reports `81/81 checks passed`, `test-factory-integration.py` reports `106/106 checks passed`.
Grepped the full output for `^FAIL` (a line whose FIRST token is literally `FAIL`) — **zero
matches**. Occurrences of the bare word `FAIL` elsewhere are ok-line labels describing fixtures
(e.g. `ok    FAIL over an escalating member is rejected`), not failures. Exit code of the runner:
`0`.

## Message-prose grep, beyond the ok-line-label grep

Also grepped for the deleted `:165` message PROSE (not just the ok-line label) across
`*.py *.sh *.yaml *.md *.json`, to catch a `verify:` block or a `check-state.sh` presence-grep
that a green unit-test run would not surface:

```
grep -rn "per-repository now\|move it under each repos entry\|repos\[\].board in " ...
```

Hits: `factory_config.py:148` (a DIFFERENT, still-accurate docstring sentence — "the board is
per-repository now" — that does not claim `repos[].board` as the destination, untouched by this
fix); `FEAT-16-factory-per-repo-board/plan.yaml:675-676` and its own receipt (a different,
CLOSED feature's frozen historical record of the ORIGINAL implementation — not a live gate for
FEAT-24); `notes/review-harness-ui-reviewer-c0.md` (an untracked review artifact quoting the old
message, not mine, not a gate). None is a `verify:` block or `check-state.sh` line. No gate
consumer of the deleted prose found.

## Design note on `:165`'s wording

Kept the removal instruction as `f"... remove board from {path}"` rather than reusing
`repos[].board`'s own `f"... Remove repos[{name}].board from {path}"` phrasing — deliberately
mirroring the sibling per-entry message's `Remove ... from {path}` shape while still naming the
fleet file, satisfying "keep the `f"... in {path}"` shape so the fleet file is still named" via
an equivalent `from {path}` clause that still closes on the path.

## Design note on the three-part assertion shape

Each new case's `_type_ok and _repo_ok and _path_ok and _ref_ok` is four INDEPENDENT boolean
evaluations (exception type, repo substring, path substring, ref substring) conjoined into ONE
`check()` call, producing one ok-line per case — matching the existing (ii) "remote read fails"
case's shape and the task's instruction to report "both literal ok-line strings" (one per case,
not one per assertion). Dropping any one of the four independently reddens that case's single
ok-line; they are not merged into a fragile single substring test.

## Anti-vacuum: case count evidence the two new cases actually ran

Both isolated mutation runs printed `1 of 81 FAILING` (not e.g. `81 of 81` or a crash), and the
clean run reports `81/81 checks passed` — up from 79 before this cycle (2 new cases added, both
counted). This is independent of the ok-line text itself and confirms the new cases were
collected and executed, not silently skipped.

## Files touched

- `.claude/skills/harness/bin/factory_config.py`
- `.claude/skills/harness/bin/test-factory-config.py`
- `.harness/harness/features/FEAT-24-config-responsibility-split/observations/harness-backend-dev.md`
  (my own observations log — two entries appended)
- `.harness/harness/features/FEAT-24-config-responsibility-split/notes/receipt-harness-backend-dev-fix-c5.md`
  (this receipt)

Nothing committed. `git status --porcelain` at the time of writing this receipt also shows
modifications to `feature.json`, `observations/harness-eng-lead.md` and
`observations/harness-validator-lead.md`, plus three untracked `notes/review-*.md` files — none
of those were touched by this run; they are other agents' concurrent artifacts in the same
feature directory.

## Cycle 2 — send-back: `(8b)` pinned the offending key twice, the destination not at all

### The gap, confirmed

`:228` (`"invalid: board —"`) and `:229-230` (`"whole-fleet board"`) both pin the OFFENDING KEY —
the first via the em-dash preamble, the second by discriminating which of the two board-shaped
messages this is. Neither pins the DESTINATION clause (`github.board` in the fleet member's own
`.harness/harness.json`). Before cycle 1 `:225` pinned a destination, at the wrong value
(`repos[].board` — the defect). After cycle 1 the suite pinned no destination at all — a net loss
of exactly the property the fix exists to protect.

### The addition — ADDITIONS only, `:228`/`:229-230` untouched

Added two new `check()` calls immediately after the existing pair, in the plan's own
present-AND-absent idiom (`plan.yaml:564-568`):

```python
check("(8b) the next_step points at github.board", "github.board" in str(e), str(e))
check("(8b) the next_step no longer points at repos[].board",
      "repos[].board" not in str(e), str(e))
```

Comment above them explains the split of duties: `:228`/`:229-230` establish WHICH message this
is (the key); the new pair pins the destination's CONTENT — and explicitly notes the asymmetry
that `"github.board"` alone does not discriminate top-level from per-entry (it appears in both
`:165-167` and `:192-194`), and does not need to, since the identity is already settled by the
checks above it.

### Reddening proof — negative clause (the direct regression guard)

Reverted `factory_config.py:165-167` to the OLD text (`"the board is per-repository now — move it
under each repos entry as repos[].board in {path}"`) and ran the suite. Literal `FAIL` lines:

```
FAIL  (8b) the next_step names the whole-fleet key, not repos[].board
FAIL  (8b) the next_step points at github.board
FAIL  (8b) the next_step no longer points at repos[].board
```

All three reddened together because the OLD text also fails the pre-existing `:229-230`
discriminator — expected, since the old message is literally the pre-fix defect. The new negative
clause (`"repos[].board" not in str(e)`) reddened correctly: the old message contains the literal
substring `repos[].board`, so `not in` is `False`.

Restored — but restoring via `git checkout --` here would have reverted to the PRE-cycle-1 text,
since nothing in this feature has been committed; HEAD still holds the original defect. Restored
by hand instead (re-applying the cycle-1 `:165-167` text verbatim), then confirmed:

- sha256 after restoration: `0d970cc83d1c0e1c6c79e6c7e6a75839fc07310e16e2e3822a91931d1749516d`
  (matches the hash taken immediately after this cycle's test-file edit, before any mutation)
- `git diff -- factory_config.py`: exactly one hunk, at `:162-167`, cycle-1 text intact (pasted
  above in the FIX 2 section, unchanged)
- suite: `83/83 checks passed`, zero `FAIL` lines

### Reddening proof — positive clause (isolated)

Deleted only the `under github.board` clause from the `:165-167` message (destination text became
"...in its own .harness/harness.json; remove board..."), leaving the key-identity text (`"a
whole-fleet board key..."`) untouched. Ran the suite:

```
FAIL  (8b) the next_step points at github.board
```

Exactly one `FAIL` line — isolated, does not touch the key-identity checks or the negative clause
(the mutated text still doesn't contain `repos[].board`). Restored by hand, confirmed sha256
`0d970cc83d1c0e1c6c79e6c7e6a75839fc07310e16e2e3822a91931d1749516d` again, `git diff` one hunk at
`:162-167`, suite `83/83 checks passed`.

### Anti-vacuum: case count

Suite went from 81/81 (post cycle-1) to 83/83 (post cycle-2) — 2 new checks added, both counted,
neither silently skipped.

### Re-run and verify

T-02's `verify:` block, cross-checked verbatim against `plan.yaml:367-388` (unchanged from cycle
1) — final line:

```
T-02 GREEN
```

Full suite (`run-unit-tests.sh`): exit `0`. `grep -c "^FAIL"` on the full combined stdout+stderr:
`0`. `test-factory-config.py` reports `83/83 checks passed`, `test-factory-integration.py`
reports `106/106 checks passed`.

### Files touched (cycle 2, same two files as cycle 1)

- `.claude/skills/harness/bin/factory_config.py` — no net change vs. cycle-1 end state (confirmed
  by sha256 above); only touched transiently during the reddening probes, restored each time.
- `.claude/skills/harness/bin/test-factory-config.py` — two new `check()` calls plus comment
  added to the `(8b)` block; nothing else altered.

Nobody committed. No other file touched this cycle.
