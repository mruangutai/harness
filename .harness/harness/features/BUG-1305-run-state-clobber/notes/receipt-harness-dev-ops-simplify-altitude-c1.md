# ALTITUDE reader — BUG-1305, cycle 1 — harness-dev-ops

**BLUF:** Two altitude findings, both real. The one I'd apply if only one could be:
`check-state.sh:1502-1508` reimplements `run_identity.uid_conflict`'s own null/empty/equality
guard instead of just calling it on the real objects — a duplicate statement of the rule that
already disagrees with the canonical one on a whitespace-only `run_uid` value. Small, safe,
mechanical → **fold-in**. The second finding (POST-time effective-uid selection embedded in
`check-domain.sh`'s heredoc instead of `run_identity.py`) is real but a larger refactor near an
exhausted cycle budget → **briefing-row**. Everything else I looked at is at its right home;
the residuals D-08/D-12/D-13 are signed and I did not re-litigate them.

## Rule-to-home table

| Rule | Stated in | # statements | Verdict |
|---|---|---|---|
| Which paths are run-identity artifacts | `harness_boundary.RE_RUN_IDENTITY` (built from `run_identity.MARKER_NAME`), consumed by `check-domain.sh` SHAPE_PATTERNS + `bash-write-guard.sh._run_artifact_guard` | 1 | leave — correct, follows the pre-existing `RE_RUN_DIGEST`/`RE_STATE_YAML` pattern (`harness_boundary.py:1-46`) |
| Witness↔checkpoint seed-field conflict | `run_identity.conflict()`, called directly by both `check-domain.sh:1645` and `check-state.sh:1493` | 1 | leave — both callers pass the real objects through |
| Run_uid conflict | canonical: `run_identity.uid_conflict()`. Shadow copy: `check-state.sh:1504-1506`'s hand-rolled guard before calling it | 2 | **fold-in** (Finding 1) |
| POST-time effective-uid selection (landed › witness › freshly minted) | inline in `check-domain.sh:1582-1588`, no function in `run_identity.py`, no unit test | 1, wrong altitude | **briefing-row** (Finding 2) |
| Allowed top-level checkpoint keys | `ALLOWED` (`check-domain.sh:1522`) and `CHECKPOINT_KEYS` (`check-state.sh:1391`), each hand-listing `run_uid` | 2 | leave — pre-existing duplication (predates this diff), explicitly documented as an intentional vocabulary-only sync (D-02 comment at `check-domain.sh:1515-1521`), and D-12 signed adding `run_uid` to both. Consolidating the two sets reaches outside this diff's scope |
| Mode B closure (`check_artifact_file` root resolution) | `validate-digest.py`'s SubagentStop hook | 1 | leave — D-08 signed, single home |
| Witness-absent blind spot | `check-state.sh` INV-36 gate | 1 | leave — D-13 signed residual; no additive fix found that doesn't reopen it |

## Finding 1 — fold-in

**File/line:** `.claude/skills/harness/bin/check-state.sh:1502-1508`
**Summary:** Before calling `run_identity.uid_conflict`, the code re-derives and re-checks the
"is there a real uid disagreement" predicate itself (`_wuid is not None and str(_wuid).strip()
and _suid is not None and str(_suid).strip() and str(_wuid) != str(_suid)`), then calls
`uid_conflict({"run_uid": _wuid}, {"run_uid": _suid})` with reconstructed minimal dicts, when
`run_identity.uid_conflict(_marker, sdoc)` already implements exactly this guard internally
(`run_identity.py:123-132`: `if prior is None or prior == "": return None`) and would take the
real objects directly.
**Cost:** two independent statements of the same predicate that can drift — and already have:
the manual guard treats a whitespace-only `run_uid` (`" "`) as absent (`str(x).strip()` is
falsy), while `uid_conflict` treats it as present (`prior is None or prior == ""` is false for
`" "`), so a witness or checkpoint carrying a whitespace-only `run_uid` is silently un-reported
by `check-state.sh` today but would be reported if `uid_conflict` were called directly.
**Alternative:** replace lines 1502-1508 with `_uid_reason = run_identity.uid_conflict(_marker,
sdoc)` (guarded only by `isinstance(_marker, dict)`, already established above at
`check-state.sh:1483` `if os.path.lexists(_marker_path)`), then `if _uid_reason: bad.append(...)`.
**Breakage risk:** `uid_conflict` reads only the `run_uid` key off whatever mapping it's given,
so passing the full `_marker`/`sdoc` dicts instead of the reconstructed ones is safe; the one
behavior change is the whitespace-only edge case above, which becomes *more* strict (catches a
case it silently missed), not weaker — no assertion is deleted or softened.
**Recommendation: fold-in.**

## Finding 2 — briefing-row

**File/line:** `.claude/skills/harness/bin/check-domain.sh:1571-1592` (POST-mint block)
**Summary:** D-12's minting rule — "prefer the landed `run_uid`, else the witness's, else mint a
fresh one" (`effective_uid = landed_uid or witness_uid or run_identity.mint_uid()`), plus the
conditional `inject_uid`/`record_seed` calls that act on it — is business logic about how a run's
identity is established, not a shell-hook concern (payload shape, exit codes, deny wording). It
lives only inline in this heredoc; `run_identity.py`'s `__all__` (`run_identity.py:13-16`) has no
function that owns this selection rule, and `tests/unit/test-run-identity.py` tests every other
primitive (`record_seed`, `conflict`, `uid_conflict`, `inject_uid`) in isolation but not this one.
It is exercised only through `tests/integration/test-check-domain.py`'s
`run_bug1305_marker_cases` (`"POST mints uid and matching witness"`,
`"POST inject_uid is idempotent"`), which must boot the whole hook subprocess to prove a five-line
fallback rule.
**Cost:** the fallback-priority rule can only be unit-tested by way of the full hook, and any
future consumer that needs the same "pick the effective uid" rule (e.g., a repair tool, or a
second gate) has no importable function to call and would re-derive it inline, same as this one
did.
**Alternative:** extract a `mint_and_record(run_dir, absolute_path, doc)` function into
`run_identity.py` that does exactly what lines 1575-1592 do today (read the marker, compute
`effective_uid`, conditionally `inject_uid`, then `record_seed`), returning `effective_uid` or
raising nothing (preserve the current best-effort `except Exception: pass` contract at the call
site, or move it inside the function); `check-domain.sh` calls it in one line and keeps the
outer `try/except`.
**Breakage risk:** this is enforcement-layer code under the DEC-174 lane and the current block is
wrapped in one `try/except Exception: pass` specifically so POST recording is never blocking —
a refactor that moves the exception boundary incorrectly (e.g. letting `mint_and_record` raise
past the point `inject_uid` already succeeded but `record_seed` hasn't run) could turn a landed
write into an unhandled POST exception, or double-inject a `run_uid` line under a race. This is
exactly the kind of change the simplify pass's one-fix ceiling is unsuited to absorb safely with
the cycle budget at 9/9 — hence briefing-row, not fold-in now.
**Recommendation: briefing-row.**

## What I did not flag

- The dual `ALLOWED`/`CHECKPOINT_KEYS` vocabularies (see table) — pre-existing architecture,
  D-12 signed the shared-field addition, and consolidating the sets reaches outside this diff.
- `harness_boundary.py:22`'s `from run_identity import MARKER_NAME` — EFFICIENCY already flagged
  its eagerness; on placement, this is the *correct* altitude (boundary already the shared home
  for path classification per its own module docstring, importing the marker name is the right
  direction of dependency). Not re-flagged.
- The unlocked atomic write in `run_identity.py` vs `harness_merge.locked_update` — REUSE's
  finding, not restated.
- D-08/D-12/D-13 residuals — read, judged right to accept as signed; no additive deeper fix found
  that doesn't reopen them.

## Git status (verbatim, end of run)

```
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/receipt-harness-backend-dev-simplify-reuse-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/receipt-harness-dev-ops-simplify-altitude-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/receipt-harness-dev-ops-simplify-efficiency-c1.md
```

No file under `.claude/skills/harness/bin/` or `tests/` was touched. This receipt is the only write.
