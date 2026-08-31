# Code review — PR #922 (OMP long-running Harness supervision) — code-reviewer, cycle 1 (RE-REVIEW)

reviewed: `7ccfae8dd7644bc3aaea612dabf4317c0d804f99..fee9d5fded415ad4a3db13a30958a4730f9ff61d`
Source read from the pinned worktree only. Fix commits: `cc9e5cf` (F1, F2), `fee9d5f` (F3, F5).

## BLUF — PASS. All four c0 findings hold closed; the fixer's three revisions are correct, independently re-derived, not merely trusted. Two new low/med findings on the new pid+start-time code, neither gating.

## Per-finding disposition

**F1 — CLOSED, fixed and tested.**
`harness-hooks.ts:546-548`: `parseClaimReceipt(result.stdout)` now only *adds* a receipt when one
exists; an absent receipt is logged via `debug()` and the dispatch proceeds. The old
`if (!receipt) { …rollback…; reason = "…no claim receipt…"; break; }` is gone. Re-measured every
pass-through branch at source in `dispatch-guard.sh`: unreadable payload (`:32`), non-`harness-`
agent_type (`:34-35`), non-harness dispatched persona (`:76-83`), no checkout root (`:138-141`),
registry unavailable (`:114-116`), no valid OMP supervisor pid (`:144-146`), and the internal
`except Exception` around the claim step (`:184-189`, `sys.exit(0)`) — all seven print no
`harness_claim` JSON and exit 0; `runPolicy` (`harness-hooks.ts:194-210`) maps exit 0 → `blocked:
false`, so the caller now genuinely lets these through. The one still-fail-closed branch (missing/
malformed `HARNESS-FEATURE:` line, `sys.exit(2)`) still maps to `result.blocked === true` and still
refuses. **Tested**: `omp-hooks.test.ts` "a guard pass-through with no claim receipt allows the
dispatch" and "a claimless dispatch in a batch does not roll back its siblings' claims" exercise
exactly this; ran the suite, 24/24 pass (was 20).

**F2 — CLOSED, fixed and tested; the fixer's diagnosis is correct, and independently corroborated.**
`harness-hooks.ts:442-446` now gates capture on `!featureCaptured` and `role === "user"` before
`setFeature`; `message_update`/`message_end` (`:480-496`) call `captureFeatureFromMessage` instead of
the old unconditional `setFeature(detectHarnessFeature([messageText(candidate)]), ctx)`.
`setFeature` (`:418-422`) sets `featureCaptured = true` on any real capture, so the systemPrompt path
(`before_agent_start`, `:449-452`, still an unguarded throw-on-conflict — correct, per the commit
message, since a *real* identity clash from a host-controlled source should be loud) and the message
path share one latch. This closes both the `toolResult` exposure and the later-arbitrary-user-message
re-key. Note for the record: **the framing "C0 said capture was wrong because it read assistant
messages" does not match any c0 note** — grepped all four (`review-harness-{code-reviewer,security-
reviewer,qa,ui-reviewer}-c0.md`); the only "assistant" mention is security's, contrasting
`messageText` (no role filter) against `lastAssistantText` (role filter) as the pattern that *should*
have been applied — not a claim that capture ran on assistant-role messages. The fixer's own commit
message states the real complaint correctly ("no role filter and no one-shot"), matching c0
verbatim. So there is no diagnosis to correct; the fix matches the actual finding. Independent of the
fixer's own test fixture (which is self-authored evidence), **DEC-204's prose — added in the base
commit `66e9a9d`, before this fix existed** — already states "OMP places the task assignment in the
first user message," and the decision's own measured-evidence section describes a real run where
feature capture worked correctly under the OLD (unbounded) code, i.e. it corroborates a `user`-role
delivery channel from a source that predates and does not depend on the fixer's post-hoc test.
Residual, non-blocking: I cannot independently probe a live OMP host, so full certainty that the
production message role string is exactly the lowercase literal `"user"` rests on this project's own
prior measurement, not a channel outside this codebase — flagged as Q1 below, non-blocking. **Tested**:
"a tool result echoing another feature's marker cannot re-key the session" and "a later user message
cannot re-key the captured feature," both fail on the pre-fix adapter per the commit message. Ran the
suite: 24/24 pass.

**F3 — CLOSED, fixed, tested, and the re-rating to high is correct — independently re-derived, not
accepted on say-so.**
`_omp_claim_live` (`inflight_registry.py:145-176`) requires `(pid, start_time)` match, not bare pid;
`_expire` (`:194`) and `reconcile` (`:449-472`, via the same `_expire`) both route through it now —
confirmed by grep that `_pid_alive` has exactly one remaining call site, inside `_omp_claim_live`
itself (`:170`). This makes the fixer's "reconcile could not clear it either, because it asks the
same question" claim checkable and true *for the pre-fix code* (bare `_pid_alive` in both `_expire`
and `reconcile`'s only path to it) and false post-fix (start-time mismatch now expires a recycled pid
in both). I independently traced the blast-radius claim rather than accept it: `validate-digest.py`'s
held-child gate (~:977-1008) calls `_reg.live_children(_root, agent, session=…, feature=_feature)`
whenever `norm(agent) in ("lead", "orchestrator")` — no restriction to `SINGLE_FLIGHT_AGENTS`.
`live_children` (`inflight_registry.py:277-299`) filters only by `claim.get("dispatcher") ==
dispatcher` and runs every claim through `_expire_where`/`_expire`, i.e. the same `_omp_claim_live`
question, for **any** persona's children. So a stranded OMP claim for *any* dispatched persona, not
just `harness-pm`, blocks that lead's yield and then the orchestrator's — confirmed at source, not
inherited. Re-rating high is correct. **Tested**: ran `test-inflight-registry.py`, 97/97 pass (was
88); cases 22-25 cover recycled-pid expiry, verified-claim-never-ages-out (guards the backstop from
becoming a silent global TTL), unverifiable-claim-hits-backstop, and the exact `live_children`
consumer c0 never examined.

**F5 — CLOSED, correctly downgraded, and the "unreachable" claim holds under independent check.**
`release_cmd(root, agent, feature)` (`:476`) is now a required positional. Grepped every call site:
`dispatch-guard.sh:156` and `validate-digest.py:1001` both already pass `feature=` explicitly. Beyond
the fixer's own claim, I additionally verified the *value* can never be `None` even for a legacy
claim: `_parse`'s migration path (`:74`) does `migrated.setdefault("feature", LEGACY_FEATURE)`, and
`claim_with_receipt` always writes a `"feature"` key (`:329`, default `LEGACY_FEATURE`) — so
`_c.get("feature")` at `validate-digest.py:1001` can never yield `None` and hit the new
`shlex.quote(None)` `TypeError` that would otherwise abort composing every remaining release
command in the same loop (the surrounding `try/except` at `:1003-1008` catches it as one lump
failure, not per-claim — noted, not filed as a finding, because it is unreachable given the
schema invariant). Test `case14` confirms a featureless call now raises `TypeError`. Ran the suite:
97/97 pass.

## New findings — on the new `_process_start_time`/`_read_process_start_time` code itself

**N1 [med] — a non-English `LC_TIME` on the macOS branch silently defeats identity verification for
every OMP claim on that host, re-introducing exactly the class of bug F3 fixed, bounded to 24h.**
`_read_process_start_time`'s macOS path (`inflight_registry.py:~148-156`) runs `ps -o lstart= -p
<pid>` (inherits the parent's environment, including `LC_TIME`) and parses the result with
`time.strptime(line, "%a %b %d %H:%M:%S %Y")`. Python's `time.strptime` does not call
`locale.setlocale` on its own — it stays in whatever locale the process last set (default "C",
English month/day abbreviations) — while `ps`, a C binary, *does* honor `LC_TIME` from the
environment. Concretely: a macOS host with `LC_TIME=de_DE.UTF-8` (or any locale whose weekday/month
abbreviations differ from English) set in the environment the OMP extension inherits — plausible for
a non-US developer or CI box, and macOS is one of the two platforms this feature explicitly targets
and probed (DEC-204's measured-evidence section) — makes `ps` print localized abbreviations (e.g.
"Mo" not "Mon"); `strptime` then raises `ValueError`, caught by the outer `except Exception: return
None`, so `_process_start_time` returns `None` for every call on that host. Every OMP claim then
falls into `_omp_claim_live`'s "identity unproven" branch and is capped at
`OMP_UNVERIFIED_TTL_SECONDS` (24h) regardless of whether its supervisor is genuinely still running —
silently regressing DEC-204's "an OMP claim remains live for any age" guarantee for every claim on
that host, not just a recycled one. Bounded by the 24h backstop (self-limiting, not permanent, unlike
the bug F3 fixed) and conditional on a non-default locale plus a task genuinely exceeding 24h
(measured longest run is 7,200s), which is why this is `med` and not `high`.

**N2 [low] — a TOCTOU window between the `_pid_alive` and `_process_start_time` reads inside
`_omp_claim_live` can push a still-alive, correctly-identified process into the unverified backstop
for one evaluation.**
`_omp_claim_live` (`:167-176`) calls `_pid_alive(pid)` then, if true, `_process_start_time(pid)` a
moment later. If the process exits in the gap, the Linux `/proc/<pid>/stat` read (or the macOS `ps`)
can fail (`FileNotFoundError`/empty `ps` output) and `current` becomes `None` even though the pid
*was* alive at the `_pid_alive` check. This routes to the backstop rather than a proven match, which
is the conservative direction (a process that just exited moves toward being reclaimed anyway) so
this is `info`-adjacent, not a defect on its own — flagged because it is the one place the two reads
are not atomic with respect to each other, and worth a comment if anyone revisits this file.

**Cleared, not filed:** the `/proc/<pid>/stat` field index — traced `rpartition(b")")[2].split()`
against proc(5)'s 1-based numbering by hand: `tail[0]` is field 3 (`state`), so `tail[19]` is field
22 (`starttime`); correct, and the last-`)` split correctly survives a `comm` containing embedded
parens, since it takes the LAST `)` in the whole line — after the true end of `comm`, wherever it
falls. The module-level `_START_TIME_CACHE` lifetime: confirmed genuinely per-invocation — every
consumer (`dispatch-guard.sh`, `validate-digest.py`, the extension's `spawnSync` calls in
`harness-hooks.ts:184-193`) launches `inflight_registry.py`/its importer as a fresh `python3`
subprocess per gate call; no production path imports it into a long-lived process, so a stale
pid→start-time entry surviving a PID recycle across calls is not reachable. `ps` missing/slow: a
5-second `timeout` bounds a hang, `FileNotFoundError` and a non-zero exit are both caught or produce
an empty string, never propagate. `os.sysconf("SC_CLK_TCK")` failing: caught by the same broad
`except Exception` around the Linux branch, falls through to the macOS/`ps` branch. `btime` absent
from `/proc/stat`: `next(…)` raises `StopIteration`, caught the same way. `OMP_UNVERIFIED_TTL_SECONDS`
shape and leakage: traced every path into `_omp_claim_live` — the backstop is reached only when
`recorded` or `current` is not a number, never when both are present and could be compared; no path
lets it override a provable identity match.

## Verification re-run (not trusted from the commit message)

- `python3 test-inflight-registry.py` → **97/97 pass** (matches claimed 88→97)
- `bun test ./.claude/skills/harness/bin/omp-hooks.test.ts` → **24/24 pass, 0 fail** (matches claimed 20→24)
- `python3 test-dispatch-guard.py` → **42/42 pass**
- `python3 test-validate-digest.py` → **ALL PASSED** (24/24 T-09 cases + 2/2 template cases)
- `bash run-unit-tests.sh` → **exit 0**, no `FAIL` lines in two independent full runs
- `python3 check-omp-port.py` → `OMP port surface: ok`, exit 0
- `bash check-state.sh` → exit 0, only advisory `note` lines (pre-existing, unrelated to this PR)
- `python3 sync-agent-adapters.py --check` → exit 0

## Open questions

- { id: Q1, question: "Full certainty that the OMP host delivers the harness-assignment message
  with the literal role string \"user\" (not some other value the fixture's author assumed) requires
  live OMP telemetry this review cannot reach; DEC-204's prose and its measured-evidence section are
  the strongest available corroboration but both trace to the same team. Worth a one-line note in
  DEC-204 or a probe artifact citing the exact wire event if one hasn't already been captured
  in the FEAT-31 probe notes referenced elsewhere in this codebase.", blocking: false }
- { id: Q2, question: "Should _read_process_start_time's macOS branch pin ps's locale explicitly
  (e.g. LC_ALL=C in the subprocess environment) so a non-English host locale can't silently widen
  every OMP claim on that host to a 24h cap? Cheap, and removes N1 outright.", blocking: false }

```yaml
VERDICT: PASS
DIGEST:
  headline: All four cycle-0 findings (F1 fail-open inversion, F2 unbounded feature capture, F3 PID-reuse liveness, F5 unbound release selector) are genuinely closed at source and covered by tests that fail on the unfixed code, re-run and confirmed green (97/24/42/etc. exactly matching the fixer's claimed counts); the fixer's three contested revisions (F2's role diagnosis, F3's re-rating to high via the shared live_children/held-child-gate consumer, F5's unreachability) are each independently re-derived from source, not accepted on assertion, and each holds. Two new non-gating findings on the new pid+start-time code: a locale-dependent macOS path that can silently cap every OMP claim at 24h (med), and a narrow TOCTOU window in the liveness check (low).
  severity_max: med
  findings: 6
  must_fix: []
  spec_violations: []
  reviewed: "7ccfae8dd7644bc3aaea612dabf4317c0d804f99..fee9d5fded415ad4a3db13a30958a4730f9ff61d"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Full certainty that the OMP host delivers the assignment message with role literally \"user\" requires live OMP telemetry outside this review's reach; DEC-204's prose and measured-evidence section are the strongest available corroboration, both from this same team.", blocking: false }
    - { id: Q2, question: "Should the macOS ps-based start-time read pin LC_ALL=C to remove the locale-dependent 24h-cap risk (N1) outright?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/PR-922-omp-supervision/notes/review-harness-code-reviewer-c1.md
```
