# Rulings after validate c2 (ESCALATE) — FEAT-2488 — 2026-11-24

Ruled by fable-advisor (AdvisorE4Esc) under the operator's delegated approval.

## OQ-1
**Rework raised to 3 rounds / 120 minutes** (set-rework, DEC-226). Round 3 is the last and is strictly scoped to the brief: MF-9, MF-10 (remedy (a), both sidecar names), and one ledgered T-01 amendment (files + intent). A new high in a changed surface returns to the advisor; a new high in an untouched pre-existing surface goes to backlog (D precedent).

## Summary of the other rulings
- OQ-2: MF-10 remedy (a). check-domain denies governed Write/Edit/NotebookEdit on plan.yaml.harness-merge.journal and feature.json.harness-merge.journal. (b) is refused as unsound (no authenticatable producer), and (c) is refused as the primary remedy. The Bash-route porosity predates the feature and goes to backlog.
- MF-9: inside C5 and in the round; dup2 devnull over the broken stream; no new amendment.
- OQ-3 and the c1 security advisories: backlog.

## Full ruling (verbatim)

# Ruling — FEAT-2488 validate c2 ESCALATE (AdvisorE4, pin 2eab047b)

All trace claims below re-verified at source in W; no suite or probe executed by me — execution evidence is the readers', bound by the digest's receipts. Where my verification is static I say so.

## The one place I disagree with the digest before ruling

**MF-10's "defeats plan.yaml has exactly ONE writer" overstates the delta.** The single-writer rule was never airtight against this actor: `bash-write-guard.py` contains **no plan-route rule at all** (zero matches for `plan` outside comments; its denial text at `:921-923` even assumes the Write tool is where "your domain is enforced"), and the orchestrator's domain glob `.harness/*/features/**` (team-config.yaml:42) **covers plan.yaml itself** — so a detected shell write to plan.yaml passes the guard's domain walk. check-domain's own comments concede this: the PostToolUse Bash route "is the ONE route this rule cannot deny before the fact" (`check-domain.py:1326-1328`), and the denial text admits a shell write is "the one channel the sweep above admits it cannot attribute to an author" (`:2565-2568`). The post-hoc sweep catches dead station words, not a well-shaped hostile plan.

So the journal is **not the first breach of the boundary; it is a second, quieter channel across a boundary already acknowledged porous on the Bash side** — with two aggravations the Bash route lacks: it launders the final plan.yaml bytes through the trusted writer's own process (the forged content lands attributed to plan-merge), and it leaves no shell command in the transcript, only an in-domain Write. It also adds a **wedge** the digest doesn't name: `_journal_names` treats an unreadable journal as naming every file (`harness_merge.py:404-412`), and a journal named for feature.json refuses UNREADABLE in `_recover_journal` (`:470-473`) — so a governed Write of *either* sidecar name can hold every plan.yaml **and feature.json** write at exit 5 until a human removes the file. This matters for the remedy's scope below.

The trace itself is real; I re-verified every link: the grant matches the sidecar (team-config.yaml:42, `upsert: true`); `_PLAN_YAML_PATTERN` is anchored `/plan\.yaml$` (`check-domain.py:958`, compiled `:1501`, gate `:2561`) so neither the as-typed, symlink-resolved, nor hardlink branch of `_plan_route` catches `plan.yaml.harness-merge.journal`; replay validates **hashes, not provenance** — `_replay_targets` accepts any member whose current bytes match the attacker-computed `before_sha256` and writes the arbitrary `after` image (`harness_merge.py:429-446`), and the orchestrator can trigger replay itself through any of its routine feature.json writes (`locked_update` → `recover_journals`, `:492-511`). Static trace; nobody executed it, me included.

---

## OQ-1 — grant one further round

**Authority.** The operator's delegation ("defer to Advisor"), against my own signature ruling (2 rounds / 90 min, DEC-226/C1) and my c0 fix ruling (round 1 of 2). The budget was mine to set; it is mine to raise, on the record.

**Gap.** Both remaining highs are fix-shaped and small, but the signed budget is spent, so building without a recorded raise would breach my own C1.

**Ruling: grant round 3.** Neither alternative survives inspection:

- **Ship-as-accepted-risk fails on MF-9 alone.** The Feature D precedent (R1, pre-existing high → ship+backlog) does not cover either finding: MF-10 is feature-introduced (T-01 adds `JOURNAL_SUFFIX`; the base has no journal — verified in the digest and at source), and MF-9 **falsifies a ledgered amendment**: T-02 amendment (7)'s "the verb still exits 0" is in the ledger and measured false (`guards.py:287-297` docstring carries the same false promise). Shipping a ledger whose recorded justification is known-false corrupts the honest record — that is not an acceptable-risk category, it is a truth defect. The fix is one site plus one test.
- **Stop is waste.** MF-8 and MF-7 are closed by measurement, CI is fully green at the pin, SC-01..07 met, three of five perspectives pass. The remaining work is a one-site stdio fix and a ~10-line gate extension.

**Recording (verified against `feature-record.py --help`):** the spent budget is the DEC-226 **rework** ruling, so the verb is **`set-rework`**, not `raise-cycles` (`raise-cycles` raises `max_total_cycles`, which is not exhausted — the digest records `cycles_used: 0`):

```
python3 .claude/skills/harness/bin/feature-record.py set-rework \
  --file <FD>/feature.json --rounds 3 --minutes 120 \
  --decision notes/answers-2026-11-24-validate-c2.md#oq-1
```

Run **before** any production edit, with this ruling's text carried verbatim in that answers note (C1's shape). Round 3 is strictly scoped to the brief below; nothing else enters it.

**Constraints.** Round 3 is the last. If the re-validate finds a new high in the *changed* surfaces, it returns here; a new high in untouched pre-existing surfaces goes to backlog under the D precedent.

## OQ-2 — MF-10 remedy: **(a)**, extended to both sidecar names; (b) refused on the merits; (c) refused as primary

**Authority.** C5 reserved "any new journal surface" to me; DEC-174/G-03 makes the check-domain edit main-session-direct; the operator's delegation covers the out-of-plan call.

**Gap.** The digest presents (a)/(b)/(c) as an open operator choice. It isn't, once (b) is examined technically.

**Ruling: (a).** Extend check-domain's plan-route denial (`check-domain.py:2540-2562` neighborhood, reusing `_plan_route`'s as-typed/resolved/hardlink machinery) to deny governed Write/Edit/NotebookEdit on **both** `plan.yaml.harness-merge.journal` **and** `feature.json.harness-merge.journal` within the feature-dir grammar. Both names, because the second is the wedge/DoS surface verified above, and the recovery side already declares only `JOURNAL_PAIR[0]` carries an intent journal — a governed agent has no legitimate reason to Write either. No false positive is possible: the legitimate producer is `locked_pair_update` running inside plan-merge's own process (`harness_merge.py:535-560`), which no PreToolUse hook sees. The denial text should name plan-merge as the only journal producer, same posture as the existing message. **Not** in `check-plan-routes.py` — that file is C4-forbidden; `check-domain.py` is not on the C4 list (verified against C4's text in my signature ruling).

**(b) is refused on soundness, not just budget.** There is no authenticatable producer on this filesystem: every agent runs as the same uid, so owner/mode checks distinguish nothing; lock provenance does not survive the producing process; and any HMAC/secret scheme fails because the orchestrator holds `{path: ".", read: true}` (team-config.yaml:50) — the key would be readable by the actor it defends against. Replay-side "authorization" would be mechanism that cannot deliver its own premise, plus exactly the new journal surface C5 exists to block. The only sound authority boundary is the write gate — which is (a).

**(c) refused as the primary remedy** — not because the risk is apocalyptic (the Bash parity above says the boundary was already imperfect for this actor), but because (a) costs ~10 gate lines plus one test **inside a round that is being granted anyway for MF-9**, and it restores exact parity between the journal sidecar and plan.yaml on the one surface (Write/Edit) the fleet actually enforces. What **does** go to backlog is the pre-existing Bash-route porosity itself (shell write of a well-shaped plan.yaml passes bash-write-guard's domain walk) — that is FEAT-41 T-09's deliberate posture, predates E, and is not this feature's to fix.

**Mechanics.** check-domain.py and its test are outside every task's `files:`, so this needs **one ledgered amendment to T-01** — `files` is a ledgered amend field (`plan_merge/amend.py:233`, `LEDGERED_FIELDS = ("intent", "files", "verify")`), so: amend T-01 `files` adding `check-domain.py` and the chosen gate-test file, plus a one-clause `intent` amendment naming the sidecar denial, `--reason` citing MF-10 and this ruling. No APPROVAL-RESET exists to fire (re-verified at signature: `amend.py:163` is the only `reset` assignment); the signature stands per DEC-23.

## MF-9 — in the round; within C5; **no new amendment needed**

**Authority/Gap.** C5 forbids new *journal* surfaces: a schema field, a third outcome class, an added fsync, a second recovery entry point. The dup2 fix touches none of these — it is receipt plumbing in `guards.py:271-297`, inside T-02's files.

**Ruling: fix it in round 3.** On a caught OSError/ValueError in `_print_receipts`/`_relay_after_commit`, dup2 an `os.open(os.devnull, O_WRONLY)` over the broken stream's fileno (the documented SIGPIPE idiom), wrapped in `suppress(OSError, ValueError)` — the closed-stream case raises ValueError from `fileno()` and must not regress 2488/a. That makes the finalization flush succeed into devnull, so the docstring's and amendment (7)'s "the verb still exits 0" becomes **true**, which is why no further ledger entry is required: the fix delivers the already-ledgered claim rather than deviating from it. The test must run the CLI as a **child with `PYTHONUNBUFFERED` explicitly stripped** (`env -u`, not inherited absence) and a broken stdout, asserting rc 0 and both files landed; red at pin with rc 120 (code-reviewer already measured the red — capture it as the receipt). Cover the stderr variant (the measured pair-write case). This is the only way around the review shell's `PYTHONUNBUFFERED=1` blind spot the digest correctly diagnosed.

## OQ-3 — backlog

`write_feature_json`'s unguarded relay (`feature_json_write.py:231`, verified unguarded at source) and the non-amendment verbs' bare receipt prints are **pre-existing at base**, low severity, and outside both signed tasks. Folding them in would widen a last round whose entire justification is that both remaining items are small and scoped. Backlog, with one note for the backlog ticket: MF-9's helper should land where `feature_json_write` can later import it without a second convention — but the import happens in the backlog item, not now.

## c1 security advisories (case-insensitive alias, unescaped filenames) — backlog, confirmed

Ruled backlog at c0, not re-raised by any c3 reader (the digest's own "previously ruled" list), and the diagnostic-bounding work in round 1 already trimmed the worst of the filename echo. Nothing at this pin changes their standing. The security reviewer's c3 note confirms the new refusal text is fixed and introduces no journal-content echo.

---

## Fix brief — round 3, in this order

0. **Record the budget**: `set-rework --rounds 3 --minutes 120 --decision notes/answers-2026-11-24-validate-c2.md#oq-1`, ruling text verbatim in that note (C1).
1. **MF-9**: red receipt — child CLI run, `env -u PYTHONUNBUFFERED`, broken stdout → rc 120 at pin (`notes/` per C6). Fix in `guards.py` per above; stderr variant covered; green child test asserts rc 0 + both files landed + no journal; 2488/a stays green.
2. **MF-10**: red receipt — gate test planting a governed Write of each sidecar name (orchestrator identity) → allowed at pin. Fix in `check-domain.py` beside the plan-route gate, both pair sidecar names, symlink/hardlink routes included; test lands in the `test-check-domain*.py` family (the file that exercises `_plan_route`; `tests/unit/` holds eight — builder picks, likely `test-check-domain-grant.py` or `test-check-domain.py`). **Do not touch** `check-plan-routes.py`, `test-check-plan-routes.py`, `check_state/`, `union.py` (C4).
3. **Ledgered amendment**: one amend of T-01 (`files` + `intent`), reason citing MF-10 and this ruling; verify the judgement landed and approval untouched.
4. **Verification before re-pin**: full `unit` and `integration` kinds via `run-unit-tests.py`; C4 forbidden-surface diff at the new pin; C6 receipts to `notes/`.

**Explicitly out of the round:** OQ-3, QA A2 (the `lstat` is not dead — `_recover_journal:461` calls `_require_regular` standalone before any lock; leave it), QA A3, the c1 advisories, any Bash-route work, any sanitization growth.

**[unverified]:** the MF-9 rc-120 and MF-10 Write-allowed behaviors — my verification of both is reading the sources and the readers' measurements; I executed nothing. Everything else cited above I confirmed at the named file:line in W.
