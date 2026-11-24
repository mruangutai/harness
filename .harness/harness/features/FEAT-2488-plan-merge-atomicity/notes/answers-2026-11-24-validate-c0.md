# Rulings after validate c0 — FEAT-2488 — 2026-11-24

Ruled by fable-advisor (AdvisorE3Fix) under the operator's delegated approval. Fix round 1 of 2.

## Summary
- OQ-1: (a). Narrow the five handlers to the named classes; one ledgered amendment per task (T-01.intent, T-02.intent). No re-signature (DEC-23). (b) and the BaseException evasion (c) are refused.
- OQ-2: waived.
- MF-2 to MF-5 are inside C5; no new journal surface.
- MF-6, the SC-01 gaps G-a..G-d and the diagnostic bounding are all in this round.
- Full `unit` and `integration` kinds run before the re-pin.
- Backlog: the FEAT-63 census loophole (BaseException and tuple handlers uncounted).

## Full ruling (verbatim)

All evidence read and verified at the pin (worktree product tree is byte-identical to `95606ddb`; `git diff --name-only 95606ddb..HEAD` outside `.harness/` is empty). Paths below relative to `.claude/skills/harness/bin/` unless noted.

---

# Ruling — FEAT-2488 fix round (AdvisorE2, validate c0 FAIL at 95606ddb)

## Authority
The operator's delegation ("defer to Advisor"), exercised against my own signature ruling `notes/answers-2026-11-23-signoff.md` (C1–C6; rework 2 rounds / 90 min, 0 used) and DEC-23/DEC-229's amendment governance, which I re-read at source (`docs/DECISIONS.md:262-267`).

## Gap
The validator's OQ-1 blocks the round: the signed T-01 §6 / T-02 items 2–3 require five `except Exception` handlers the FEAT-63 census refuses at ceiling 0, and the ceiling table is in forbidden `check-plan-routes.py`. OQ-2 and the C5 classification of MF-2..MF-5 need rulings before Main builds.

---

## OQ-1 (blocking) — Ruling: **(a), narrow the five handlers; record one ledgered amendment per task. (b) is dead twice over; one (c) exists and is refused.**

**What the census treats as broad — verified.** `check-plan-routes.py:2507-2510`: `_is_broad_catch` flags only a bare `except:` or a handler typed exactly the name `Exception`. A tuple catch (`except (OSError, ValueError)`) is `ast.Tuple` → not counted. `except BaseException` is not counted either — QA confirmed the base's five sites were "`except BaseException` or absent, and the census does not count those" (`review-harness-qa-c1.md:53`).

**(b) is dead on both prongs — verified.** `harness_boundary.py`'s two sanctioned catches are `_as_repo_module_failure` (`:579-587`, wraps everything into `RepoModuleError` — the wrong type: a journal commit failure must become `JournalPending`, not a module-load failure) and `hook_guard` (`:601` — the hook own-failure idiom, returning hook exit codes; these call sites are not hooks). Neither is reusable, and adding a third catch there is pinned shut independently of the BRIEF: `test-checker-structure-locks.py:488-490` asserts `BROAD_CATCH_CEILINGS.get("harness_boundary.py") == 2` *exactly*, and `:509-511` asserts a third catch fails against ceiling 2. Routing through the boundary therefore also requires editing the forbidden file.

**(c) exists and is refused.** Rewriting each site as `except BaseException` with an `isinstance(exc, Exception)` filter would preserve the signed text verbatim and pass the census (verified above: BaseException is uncounted). I refuse it: it is semantically identical to the catch the census rejects, defeats the lock FEAT-63 exists to hold, and the census's own finding text names the intended remedy — "narrow the new one to the boundary's real error class" (`check-plan-routes.py:2554`). It would also be the fleet's first census-evasion precedent. (The loophole itself is real and goes to backlog, below.)

**The approved classes, per site** (verified against each body's actual raisables):

| Site | Narrow to | Why complete |
|---|---|---|
| `harness_merge.py:364` `_replay` | `except OSError` | body is `replace_bytes` (mkstemp/fdopen/write/os.replace — all OSError) + `os.unlink` |
| `harness_merge.py:464` `_commit_published` | `except OSError` | os.open/fsync/close + `replace_bytes` + unlink — all OSError |
| `plan_merge/guards.py:48` `_recover_plan_journals` | `except (OSError, ValueError)` | `recover_journals` raisables beyond the two already-handled types: listdir/lock-open OSError; `ValueError` from `_default_timeout` on a malformed `HARNESS_LOCK_TIMEOUT_SECONDS` (`harness_merge.py:106-113`). json/base64/schema faults are already `MergeRefusal` inside `_read_journal` |
| `plan_merge/amendments.py:235` `write_plan_and_ledger` | `except (OSError, ValueError)` *after* the existing JournalPending/MergeRefusal dispatch | `ValueError` covers `json.JSONDecodeError`, `UnicodeDecodeError`, base64 faults, `_pair_directory`'s ValueError; OSError covers all I/O. `_pair_failure` keeps dispatching by type |
| `plan_merge/amendments.py:199` `_relay_after_commit` | `except (OSError, ValueError)` | `changed_state_feedback` already catches `(OSError, SubprocessError)` around its subprocess (`harness_boundary.py:500-505`); what remains is print-to-stderr (OSError on broken pipe, ValueError on a closed stream) |

The builder may **add** a further concrete, named class if a test surfaces one; never `Exception` or `BaseException`.

**Is the outcome space still total?** Not by construction any more — that is the real deviation, and it must be said plainly in the amendment. After narrowing, every failure lands in exactly one of: {MergeRefusal exit N; JournalPending → exit-2 "journaled/pending" message; **uncaught traceback with the journal left on disk**}. The third bucket is new and is confined to exception classes outside the enumerated sets — none plausible from the os-call bodies (the residue is MemoryError-grade interpreter anomalies). Two properties survive untouched: the **disk** is still safe-by-journal in that sliver (the journal is only unlinked last, so the next write rolls forward), and the traceback does not *lie* — whereas today's `guards.py:48` would stamp "nothing was written" on it. What is lost is the signed "No recovery failure prints a Traceback" and the guarantee that every post-publish failure is *reported* as journaled. Side benefit: narrowing partially retires the diagnostic misnomer my signature ruling logged as plan-defect 2 (a pre-member-write bug mislabelled "the ledger write failed") — bugs now traceback, environmental failures get the clean message.

**Amendment mechanics — no approval reset, no re-signature. Verified at source.** DEC-23 (`DECISIONS.md:262-267`): a departure from a signed task's HOW "is governed afterwards by the ledger — one amendment judgement per changed field … — **and never by a fresh signature**." `amend` on `tasks.*.intent` is a ledgered field (`amend.py:233` `LEDGERED_FIELDS`), requires `--reason`, appends one judgement via `write_plan_and_ledger`, and "leaves the signature standing (BUG-1716 D-04)" (`amend.py:158-161`); there is no APPROVAL_RESET path in `amend.py` (SC-06, re-verified at signature: `result["reset"] = False` at `:163` is the only assignment). `signed_task_hashes` is deliberately not revised — the hash mismatch plus the judgement is exactly INV-40's ledgered-amendment signal, audited at ship (DEC-230). **Record two amendments, one per task** (`amend --key tasks --id T-01 --field intent` and `--id T-02`, each via `--show` → `--expect-sha256` → `--value-file --reason`), each reason enumerating *all* of that task's deviations — the narrowed classes **and** the MF-2/3/4 validation tightening below, which also deviates from §6's signed algorithm (as signed, §6 accepts a one-member journal and locks arbitrary siblings). One amendment per task, not five, keeps the ledger legible. Note the pleasant recursion: the ledgered T-01 amendment runs `write_plan_and_ledger` — the code under repair — so record the amendments *after* the code lands and they double as a live probe.

## OQ-2 — Ruling: **waived**, extending Q2(c)'s rationale. Not a fix-round item.
The missing replay-path directory fsync buys only OS-crash durability, which the BRIEF excludes and Q2(c) already reasoned through: members are un-fsync'd by design, and a crash-resurrected journal meets members at after (no-op) or diverged (exit-5, images kept in `after_b64`). Two additional points specific to this case: (1) the kill-safety guarantee — the only one warranted — needs no barrier at replay, because a journal that is being replayed already survived; (2) in the triggering scenario the device just returned EIO on fsync, so a replay-time fsync would most plausibly fail again and convert a *succeeding* roll-forward into a `JournalPending(replay=True)` loop until the disk heals — the fix would make the failure mode worse. No new surface, no code. The builder may add one sentence to `_replay`'s docstring (`harness_merge.py:357-359`) noting replay performs no directory fsync, under C5 wording latitude.

## C5 check — MF-2..MF-5 are all **inside the pinned shapes**; no new surface, approval granted here where the line was arguable.
- **MF-2 (pair binding)** — in shape, with this pre-approval: all refusals land in the existing exit-5 UNREADABLE/DIVERGED class; requiring **exactly two members** in `_read_journal` is a stricter parse of the existing schema, not a schema field (the only producer, `locked_pair_update`, writes exactly two — `harness_merge.py:479-480`); and the authorized-membership check must run **before any secondary lock is acquired** (which is what kills the reversed `feature.json`-primary order at `_recover_journal`, `harness_merge.py:383-384`). Mechanism is the builder's pick — either pass the authorized sibling set through the existing `recover_journals` signature from its callers, or declare the one legal pair at module level in `harness_merge` (whose docstring already names plan.yaml/feature.json as *the* amendment pair). Extending the signature of the one entry point is **not** "a second recovery entry point"; adding a second function would be. Constraint: the fix must not break sign-approval's nested write (plan-primary journal found while the plan lock is already held).
- **MF-3 (dangling/non-regular)** — in shape: `lstat`/`S_ISREG` before open (no FIFO block), ENOENT-on-nothing stays the benign vanished case, a present-but-dangling or non-regular entry refuses exit-5 naming the journal. Existing refusal class; kills the measured infinite loop (`_journal_names` true at `:313` vs `os.path.exists` false at `:375`).
- **MF-4 (require `before_sha256` key)** — in shape: stricter parse at `harness_merge.py:248-252` (`"before_sha256" not in member` → UNREADABLE; explicit `null` keeps meaning recorded absence), matching `_read_journal`'s own stated contract.
- **MF-5 (`amend --show` read-only)** — in shape and already plumbed: `_amend_preflight` calls `_resolve_plan(args.file)` before the show branch (`amend.py:209-221`); pass `recover=not args.show` (or equivalent) using the exact lever `check` already uses (`guards.py` `recover=False`). Restores D-02's mutating-verbs-only scope and `plan-merge.py:252-253`'s promise. Fold a clause into the T-02 amendment only if T-02's signed amend item literally mandated unconditional recovery — [unverified at that word-level depth; builder checks while drafting the amendment].

## MF-6 and the advisories — Ruling: **all in the fix round.**
- **MF-6**: yes. Assert the named failure in the `case_1985` successor (`"PermissionError" in stderr` — goalcheck P4 confirmed production prints it, so this is assertion-only) and compare the three snapshots as **bytes** (`open('rb')`), removing the newline-normalizing text reads at `test-plan-merge.py:176-178`.
- **SC-01 assertion gaps G-a..G-d / pm F-2**: yes, same test file, same sitting — torn state (b) through record-amendments, exit-5 via amend, the (d) re-run exit code, and "exit-5 names the journal path". My probes carry these clauses today; probes are not regression guards.
- **Security-low diagnostic bounding**: yes — the MF-2/MF-4 rewrites touch exactly the message sites (`harness_merge.py:248-279,347-349`); a truncated-repr of malformed field values is wording latitude under C5, near-zero marginal cost. Do **not** grow it into a sanitization layer.

---

## Fix-round brief (round 1 of 2; order matters)

**Main builds, in this order — each production fix lands with a red-first test (the pin has no test constructing a malformed, misbound, dangling or non-regular journal, nor `amend --show` with a pending journal: the digest's own coverage_gaps):**

1. **OQ-1 narrowing** — the five handlers, to the classes in the table above. Red proof: `test-checker-structure-locks.py` red at pin, green after (QA already captured the red).
2. **MF-4** — require the `before_sha256` key in `_read_journal`; explicit `null` only for absence.
3. **MF-2** — exactly-two-member parse; authorized-pair binding refused exit-5 *before* any secondary lock; one-member, misbound-sibling, and `feature.json`-primary journals all refuse; sign-approval's nested path stays green.
4. **MF-3** — `lstat`-based refusal of dangling/non-regular journal entries, exit 5 naming the journal; no open on a FIFO; vanished stays benign.
5. **MF-5** — `--show` passes `recover=False` through the existing `_resolve_plan` lever.
6. **Diagnostic bounding** — truncated repr/escaped names in the refusal messages being rewritten in 2–4.
7. **MF-6 + G-a..G-d** — named-failure assertion, raw-byte snapshots, and the four SC-01 assertions.
8. **Record the two ledgered amendments** (T-01.intent, T-02.intent) via `amend --show`/`--expect-sha256`/`--reason`, reasons enumerating every deviation per task; verify the two judgements landed and approval is untouched (no reset exists to fire).
9. **Verification before re-pin**: full `unit` **and full `integration` kinds** via `run-unit-tests.py` — not hand-picked suites; the builders' skipping of the full integration kind is how MF-1 shipped (QA's G-02/G-04). C6 receipts to `notes/`, C4 forbidden-surface diff re-run at the new pin.

**Waived / not in the round:** OQ-2 (ruled above, docstring sentence optional).

**Backlog (not E):**
- FEAT-63 census loophole: `except BaseException` and tuple-typed handlers are uncounted (`check-plan-routes.py:2507-2510`), so the census permits a *broader* catch than the one it refuses. File against the census owner with this ruling attached.
- Q3 (apply/load_plan verify asymmetry) and Q4 (mission-less intake) remain backlogged per the signature ruling.

**Where I disagree with the validator, for the record:** only one substantive point — the digest calls narrowing "the only remedy." It is not: the BaseException evasion exists and passes the census today; I verified it and refused it above, because a time-pressed builder would otherwise find it on their own. Everything else in the digest I verified and endorse, including the severity reconciliations (MF-5 at med is right — the state `--show` reaches is the correct roll-forward; the breach is the promise, not the bytes). [unverified]: I did not re-run any suite or probe; all execution evidence cited is the readers', which the digest's receipts bind to the pin.

Budget stance: this is one round's work, within 2/90 with round 2 held in reserve for the re-validate's findings.
