# Receipt — harness-backend-dev — T-03 cycle 1 (BUG-1309-mirror-build-entry)

Supplements the c0 receipt (`receipt-harness-backend-dev-T-03-c0.md`) — not restated here.
Send-back: `runs/2026-09-06-03-eng/send-back-T-03-c1.md`. Two assertion strengthenings only,
both inside existing cases, in `tests/integration/test-gh-sync.py`. No production file touched.

## F-1 — "T-03 parent contract error refuses" (now :3562-3565)

Added `n_before_R5 = len(calls(tmpR3))` captured immediately before the R5 `run(...)` (same
shape R4 already uses with `n_before_R4`), sliced to `logR5 = calls(tmpR3)[n_before_R5:]`, and
extended the check with `not non_preflight_calls(logR5)` — no calls beyond `load_config`'s
`auth status` preflight for this refusal, per the intent's "the fake gh log records zero
calls". Failure detail now includes `calls={logR5!r}`.

**Non-vacuity evidence:** a temporary `print(f"DEBUG logR5={logR5!r}")` (reverted before
finishing) showed the actual sliced log for this run:
`logR5=['auth status\x01']` — exactly one entry, the unavoidable preflight, and
`non_preflight_calls` strips exactly that string (`"auth status" not in l`), so the new
conjunct is `not []` = `True` here and would flip `False` the moment the refusal path made
any real gh call. The assertion's subject is observably non-empty machinery, not an
unreachable branch.

## F-2 — "T-03 gh failure records nothing" (now :3573-3576)

Added `and "gh-sync: SKIP" in rR6.stdout` — `skip()` in `gh-sync.py` (`bin/gh-sync.py:190`)
prints via `print()`, i.e. stdout, so the case now asserts the funnel the intent names
literally ("the process exits 0 through skip"), not merely the absence of a recorded
`build_entry`, which a total no-op would also satisfy.

**Non-vacuity evidence:** a temporary `print(f"DEBUG R6 stdout=...")` (reverted before
finishing) showed the real R6 stdout:
`'gh-sync: no github.board configured — station writes are not attempted\ngh-sync: SKIP — gh
api repos/implentio/fake/milestones -q… failed: simulated failure\n'` — the literal
`gh-sync: SKIP` is present, confirming the subject is genuinely observable on this stream.

**Mutant-catch proof (outside the tracked file, no scratch left behind):** ran a standalone
python snippet evaluating the identical boolean expression against a synthetic no-op result
(`rc=0`, `stdout=""`, `github={}` — a `recover-terminal` that returned 0 and recorded nothing
but never reached `skip()`):
```
cond = rc==0 and "build_entry" not in gh and "gh-sync: SKIP" in stdout
```
→ `False` for the no-op (would have FAILed the case), `True` for the real observed R6 stdout
above. This confirms the new conjunct is the discriminator the send-back asked for — it
reddens on exactly the no-op it exists to exclude, and stays green on the real skip-funnel
run. No file was left with this scratch check; it never touched the tracked test file.

## Verify — T-03's verify block, verbatim, from the worktree root

```
out=$(python3 tests/integration/test-gh-sync.py) || exit 1
if printf '%s\n' "$out" | grep -q '^FAIL'; then exit 1; fi
for n in "T-03 report and ask writes nothing" "T-03 recover-terminal creates milestone and parent only" "T-03 FEAT-55 shape adopts and creates nothing" "T-03 second run is idempotent" "T-03 parent contract error refuses" "T-03 gh failure records nothing" "T-03 ship names recover-terminal"; do
  printf '%s\n' "$out" | grep -qF "ok    $n" || exit 1
done
echo VERIFY-PASS
```

Cross-checked against `plan.yaml`'s T-03 `verify:` block — matches verbatim.

Output: `VERIFY-PASS`. Suite totals: **316 `ok`, 0 `FAIL`** — identical count to cycle 0
(no case added or removed, only two existing checks strengthened).

## Case-name / scope confirmation

- All seven `check()` case names unchanged, character for character (confirmed against the
  cycle-0 receipt's list and the verify loop above, which greps every one of them).
- `git status --porcelain` for the two T-03 source paths:
  ```
   M .claude/skills/harness/bin/gh-sync.py
   M tests/integration/test-gh-sync.py
  ```
  `gh-sync.py`'s `M` is entirely cycle-0's landed, still-uncommitted diff (127 lines vs HEAD,
  per `git diff --stat HEAD`) — this cycle made zero edits to it; no `write`/`edit` tool call
  in this cycle ever targeted that path, only two read calls (module docstring, `skip()` body)
  to confirm which stream `skip()` prints to. `gh-sync.py` is unmodified relative to cycle 0.
- `tests/integration/test-check-state.py` (T-06, main session) was not read or touched.

## Files touched

- `tests/integration/test-gh-sync.py` (two assertion strengthenings only; temporary debug
  prints added and removed before finishing, per the non-vacuity-evidence instruction).
