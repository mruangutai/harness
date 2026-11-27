# Rulings after validate c3 (ESCALATE) — FEAT-2488 — 2026-11-24

Ruled by fable-advisor (AdvisorE5Esc) under the operator's delegated approval.

## OQ-1
**Rework raised to 4 rounds / 150 minutes.** Round 4 is FINAL, with no return clause. Another gating instance of either class means descope, not round 5. For stdio, descope means reverting to base print-only semantics and recording the MF-9 residue as accepted risk.

## Summary of the other rulings
- OQ-2: MF-12 remedy (b). Discovery is narrowed to JOURNAL_PAIR[0] + JOURNAL_SUFFIX, so foreign-named journals are inert. (a) is refused as primary. The two-name check-domain denial stays.
- MF-11: one total post-commit emission path in guards.py; catch tuple (OSError, ValueError, AttributeError); exhaustive stdio state matrix. No amendment (it delivers claim (7)).
- One T-01 amendment (intent + verify) before the harness_merge edit.
- Backlog: linked-worktree hardlink detection, RE_PAIR_JOURNAL `$` vs `\Z`, and the T-09 13 Edit/NotebookEdit gap.

## Full ruling (verbatim)

All sources read and verified at the pin's worktree. Ruling follows.

---

# Ruling — FEAT-2488 validate c4 ESCALATE (pin 6528b4db)

Issued under the operator's delegated approval (DEC-174, main-session-direct). I re-verified every cited site in W; execution evidence is the readers', bound by the digest's receipts.

## The one thing I'd change in the digest's framing before ruling

**MF-11 is still an instance, not the class — and the class has more members than anyone has named.** I verified two further members by reading the sources:

- `_note_on_stderr` (`guards.py:284-290`) with `sys.stderr is None`: `print(line, file=sys.stderr)` becomes `print(line, file=None)`, which CPython routes **to sys.stdout** — the "landed" note misroutes into the receipts stream — and the subsequent `sys.stderr.flush()` raises AttributeError outside the `(OSError, ValueError)` catch. If that handler was entered from `_print_receipts`' except block, the verb exits 1 after committing: MF-11's twin on fd 2. `[unverified at runtime — documented CPython `file=None` semantics plus the source; nobody executed the stderr-None state]`
- `relay_changed_state_feedback` (`harness_boundary.py:508-514`) prints via `file=sys.stderr`; with stderr None its feedback lines misroute to stdout (polluting the SC-04 receipt stream) rather than no-op. `[unverified, same basis]`
- `_silence(sys.stderr)` with stderr None raises AttributeError on `None.fileno()` *inside* `suppress(OSError, ValueError)`, which does not cover it (`guards.py:271-281`).

So a round briefed as "fix MF-11" is round-5 bait. Four rounds of one-class-member-each (OSError → ValueError → exit-flush → None; content → type → two names → any name) is exactly Feature D's lesson. Round 4 is granted **only** as a one-pass closure of both classes, with the matrix below as the test obligation.

## OQ-1 — grant round 4, the final one

**Authority.** The c2 ruling's own return clause ("a new high in a CHANGED surface returns here") plus the operator's delegation; the budget was mine to set at c2 and is mine to raise on the record.

**Gap.** Round 3 (the declared last) closed its brief exactly, but two gating findings remain in changed surfaces, one of which again falsifies a ledgered claim.

**Ruling: grant round 4.** The alternatives fail as they did at c2, and for the same reasons:

- **Ship-with-accepted-risk fails on MF-11 alone.** T-02 amendment (7) — "the verb still exits 0" — is in the ledger and measured false (code-reviewer, fd 1 closed → rc 1 after both files land; `guards.py:315` confirmed unguarded, catch tuple at `:317` confirmed `(OSError, ValueError)`). My own c2 ruling held that a ledgered claim known false is a truth defect, not an acceptable-risk category. Consistency binds me; MF-11's consequence (rc 1 after commit → caller retry → double amend) is also real harm, not cosmetics.
- **MF-12 alone could ship+backlog** (med is the right reconciliation: availability-only, one-file recovery, Bash-route parity). But the round is granted anyway, the class fix is ~1 line plus tests, and shipping it open would leave a ruled remedy knowingly incomplete.
- **Stop is waste**: MF-9/MF-10 closed by three-lens measurement, CI green with PYTHONUNBUFFERED stripped, SC-01..07 met.

**Closed-form test.** I grant the round because a closed-form remedy exists for **both** classes (below). Had either class lacked one, the ruling would be stop/descope, not round 5.

**Budget record, before any production edit:**

```
python3 .claude/skills/harness/bin/feature-record.py set-rework \
  --file <FD>/feature.json --rounds 4 --minutes 150 \
  --decision notes/answers-2026-11-25-validate-c4.md#oq-1
```

(`feature.json` currently records `rework: {rounds: 3, wall_clock_minutes: 120}` — verified. `set-rework`, not `raise-cycles`, per the c2 precedent; this ruling's text carried verbatim in that answers note.)

**Terminal condition.** Round 4 is final with no return clause. If re-validate finds another gating instance of either class, the next step is descope, not round 5: for stdio, revert the explicit post-commit flush to base `print`-only semantics (base was accidentally total: `print` to a None stdout is a no-op) and record the MF-9 buffered-exit residue as accepted risk; for journals, remedy (b) below leaves no residue to descope.

## OQ-2 — remedy (b): narrow discovery to the one producer name. (a) is refused as primary.

**Gap.** The digest presents (a)/(b) as a choice. Examined at source, only one closes the class.

**Ruling: (b).** Change `_journals_naming`'s filter (`harness_merge.py:419`) from `entry.endswith(JOURNAL_SUFFIX)` to `entry == JOURNAL_PAIR[0] + JOURNAL_SUFFIX`. The invariant this restores: **the discovery set equals the producer set.** `locked_pair_update` is the only legitimate producer and writes exactly one name, `plan.yaml.harness-merge.journal` (`harness_merge.py:578`, primary constrained to `JOURNAL_PAIR` at `:521-522` — verified). Every foreign-named `*.harness-merge.journal` becomes inert litter by construction: never read, never wedging, never replayed — regardless of how it arrived, **including the backlogged Bash route**, which (a) cannot touch.

- (a) — whole-suffix denial in check-domain — is the instance-shaped fix one size up: it widens a denylist at the perimeter while `_journal_names`'s "an unreadable journal names every file" (`:402-410`, verified) keeps trusting a namespace no producer uses. It also costs more than claimed: `_plan_route`'s hardlink machinery is keyed to exact basenames, so a suffix-wide gate is not the one-token change it looks like.
- Fail-closed is preserved where it is wanted: an unreadable **real** journal (the one name) still wedges every write in the directory until reconciled — that is the designed crash-recovery posture, and the only agent-route into that name is already denied (MF-10, closed at this pin).
- The existing two-name check-domain denial **stays as is**: it blocks forging/clobbering the real journal and remains correct. No widening needed, no second convention.
- C5: narrowing discovery adds no schema field, outcome class, fsync, or recovery entry point — it shrinks the journal surface. In scope.

**Ledger mechanics.** Unlike MF-9/MF-11, (b) *deviates from signed text*: T-01 intent item 5 specifies suffix-wide discovery with unreadable-names-all semantics (verified in plan.yaml). One ledgered amendment to T-01 — `intent` (one clause: discovery is `JOURNAL_PAIR[0] + JOURNAL_SUFFIX` only; a foreign-named suffix entry is ignored; citing MF-12 and this ruling) **and, in the same amend, `verify`**: add `tests/integration/test-check-domain-approval.py` to T-01's run_pool list, closing G-04 (the ledgered verify not running the file the previous amendment added). `files` unchanged — `harness_merge.py` and both test files are already T-01's. No APPROVAL-RESET; signature stands per DEC-23.

## Fix brief — round 4, EXHAUSTIVE class enumeration

**1. Stdio class (MF-11 + the code-reviewer's non-gating `_silence` notes — same helper, same invariant, in scope).** Contract: *after commit, no state of stdout/stderr may change the exit code, double-apply the write, or misroute output.* One total emission path in `guards.py`; no second convention. Design constraints:

- Catch tuple `(OSError, ValueError, AttributeError)`, not `except Exception` — FEAT-63's broad-catch census is why harness_merge chose a tuple at c1, and this tuple **is** total for the CLI contract: CPython process stdio is a real stream (OSError family on failure, `io.UnsupportedOperation` subclasses both OSError and ValueError), a closed stream (ValueError), or None (AttributeError). Arbitrary in-process replacement objects raising outside the tuple are the caller's contract breach.
- `None`-check before any attribute access in `_print_receipts`, `_note_on_stderr`, `_silence`. **Never `print(..., file=<maybe-None>)`**: `file=None` routes to sys.stdout (the misroute above).
- `_silence(stream, expected_fd)`: `getattr`-guarded fileno; suppress the full tuple; **dup2 only when `fileno() == expected_fd`** (1/2) — closing the caller-owned-fd-4 clobber and the no-fileno AttributeError in one rule.
- `_relay_after_commit` / relay emission routed so a None/broken stderr can neither raise outside the tuple nor misroute feedback into stdout.

**Test matrix the builder must run (child CLI, `env -u PYTHONUNBUFFERED`, asserting rc 0 + both files landed once + no journal + no misrouted bytes on the surviving stream), per verb (`amend`, `record-amendments`):** each of stdout and stderr in {working, broken pipe (buffered, exit-flush), closed stream object, **fd closed at exec (stream is None)**}, plus the joint states {both broken, both None, stdout None + stderr broken, stdout broken + stderr None}; in-process: capture with no `fileno`, capture whose `fileno()` raises `io.UnsupportedOperation`, real stream on caller-owned fd (fd preserved after). 2488/a/g/k/l/m stay green; SC-04 byte-identity on a normal stdout stays green.

**2. Journal class (MF-12, remedy (b)).** Tests in `test-harness-merge-journal.py` + the gate family: with each of {garbage `evil.harness-merge.journal`, well-formed `BRIEF.md.harness-merge.journal`, well-formed `feature.json.harness-merge.journal`} planted on disk, `locked_update(plan.yaml)`, `locked_update(feature.json)` and `locked_pair_update` all **succeed, write, and leave the foreign file untouched**; the real journal still recovers on all three entry routes; an unreadable **real** journal still refuses exit 5 (fail-closed preserved); `recover_journals` returns False with only foreign files present. Drift-pin stays green.

**3. Order and record.** `set-rework` first; the one T-01 amendment (intent + verify) before the harness_merge edit; MF-11 needs **no** amendment (it delivers ledgered claim (7), c2's MF-9 logic). C4 surfaces untouched; C6 red/green receipts to `notes/`; full unit+integration kinds at the new pin.

## Backlog (ruled, not deferred by silence)

- **Linked-worktree hardlink detection** (security med): backlog. Pre-existing anchoring newly applied, static only, needs a pre-existing alias — D precedent. Not folded into MF-12; remedy (b) makes a journal-name hardlink inert anyway.
- **RE_PAIR_JOURNAL `$` vs `\Z`**: backlog. Over-denial of a basename no producer or legitimate agent emits; zero practical consequence.
- Previously backlogged items (OQ-3, Bash porosity, c1 advisories) stand; nothing at this pin changes them.
- T-09 13's Edit/NotebookEdit gap: acceptable as static evidence (shared gate expression, verified by two readers); note for the backlog ticket, not the round.

**[unverified]:** the stderr-None misroute/AttributeError behaviors and relay misroute (source + documented CPython semantics, not executed); MF-11's rc-1 and MF-12's wedge (the readers' measurements, which I corroborated at `guards.py:307-320`, `harness_merge.py:395-512`, `check-domain.py:2604-2629`). Everything else cited I confirmed at the named file:line in W.
