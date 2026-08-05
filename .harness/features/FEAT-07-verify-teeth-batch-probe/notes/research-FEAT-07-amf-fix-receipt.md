# Verification receipt — harness-pm — FEAT-07 amf-fix (arch-review resolution)

> **PATH NOTE, raised as an open question, not worked around.** This dispatch asked for
> `notes/receipt-harness-pm-amf-fix.md`. `check-domain.sh` BLOCKED that write: `harness-pm`'s grant
> list has no `receipt-*` entry (permitted: `BRIEF.md`, `PLAN.md`, `notes/research-*.md`,
> `notes/uat-*.md`, `observations/harness-pm.md`, and two codebase lenses). The hook's own message
> says "if this path should be yours, it belongs in `.harness/team-config.yaml` — do not work around
> this hook", so the content lands here instead, at a granted path. **This is the same class of
> finding as F1**: a dispatch asked an agent for something its enforcement layer makes illegal, and
> the only legal answers were to disobey the hook or to disobey the dispatch.

**BLUF.** BRIEF and PLAN are revised for F1/F1b/F1c, F3, F2, F4 and F6. F1's remedy is written as a
recommendation the user can sign as-is (D-07: a fourth `task_verify` value, `no-task`), with the
alternative priced, and returned as a BLOCKING open question. The review's characterization of the
`DECISIONS-INDEX.md` drift is WRONG and I reproduced the measurement below: it is uniformly +6 across
57 rows — ONE edit, not two independent ones. Both `## Approval` blocks remain `status: pending`.

## The F3 measurement, reproduced verbatim — this settles the two prose accounts

Base for "committed": `git show 3bfedc9:docs/harness/DECISIONS-INDEX.md`.
Base for "generated": `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout`, run over
`DECISIONS.md`, which `git diff --stat 3bfedc9 -- docs/harness/DECISIONS.md` shows is byte-identical
to `3bfedc9` (empty output).

```
--- DEC-118 committed ---
- DEC-118 @2376 [orchestrator,dispatch,plan,state] refs: DEC-102 DEC-116 :: A team is single-squad by construction, so a multi-squad lifecycle such as `plan-feature` or `ship-feature` is an orchestrator playbook sequencing one lead-owned run per squad segment.
--- DEC-118 generated ---
- DEC-118 @2382 [orchestrator,dispatch,plan,state] refs: DEC-102 DEC-116 :: A team is single-squad by construction, so a multi-squad lifecycle such as `plan-feature` or `ship-feature` is an orchestrator playbook sequencing one lead-owned run per squad segment.
--- DEC-174 committed ---
- DEC-174 @4674 [plan,state,cost,digest] refs: DEC-142 DEC-173 :: The harness plans its own work but never EXECUTES changes to its own hooks, validators or gate scripts — green gates cannot vouch for the code being changed.
--- DEC-174 generated ---
- DEC-174 @4680 [plan,state,cost,digest] refs: DEC-142 DEC-173 :: The harness plans its own work but never EXECUTES changes to its own hooks, validators or gate scripts — green gates cannot vouch for the code being changed.
```

**My measurement AGREES with the orchestrator and CONTRADICTS the review.** DEC-174 committed is
`@4674`, generated `@4680` — generated is HIGHER, the same direction as DEC-118. The review printed
DEC-174 as "committed `@4680` vs generated `@4674`", i.e. transposed, and concluded from the apparent
reversal that there were "at least two independent pre-existing edits". There is one.

Delta over every row, generated minus committed, and the boundary:

```
$ paste <(grep -o '^- DEC-[0-9]* @[0-9]*' idx-committed.md) \
        <(grep -o '^- DEC-[0-9]* @[0-9]*' idx-generated.md) \
  | awk '{split($3,a,"@"); split($6,b,"@"); print b[2]-a[2]}' | sort | uniq -c
 117 0
  57 6

BOUNDARY at DEC-118 2376 2382 6      # first row with a non-zero delta
```

174 rows total; 117 unchanged, 57 uniformly `+6`, the `+6` run beginning at DEC-118 and continuing to
the last entry DEC-174. **Cause: ONE edit — six lines inserted into `DECISIONS.md` ahead of DEC-118's
entry after the index was last generated.** F3's substance is unaffected; only its two-edits framing
was wrong, and PLAN now carries the simpler true cause.

## The row `PLAN:645` got wrong, re-measured with all four elements

| Command | Base | Exit | Interpretation |
|---|---|---|---|
| `gen-decisions-index.py --stdout \| diff - docs/harness/DECISIONS-INDEX.md` | `3bfedc9` | **1** | pre-existing drift, 57 rows, anchors only |
| same command | working tree | **0** | the generator was already re-run here, undeclared — Q2 |
| `grep -c '^- DEC-17[5-7] ' <index>` | `3bfedc9` | 0 | discriminates |
| `grep -c '^- DEC-17[5-7] ' <index>` | working tree | 0 | discriminates |

The superseded row claimed exit 0 with "no pre-existing drift, clean on arrival". It is FALSE against
`3bfedc9` and true against the dirty working tree — which is why re-running it carelessly would have
reproduced the falsehood. Naming the base is the whole point, and T-09's precondition is now written
CONDITIONALLY (run the diff; exit 1 means report the drift, exit 0 means already reconciled) because
Q2 is unresolved.

**One correction to F3's own instruction, applied and flagged rather than shipped quietly.** F3 asks
that T-09 "report, do not absorb" the drift. Regenerating the index rewrites EVERY anchor row, so
there is no variant that both satisfies SC-12's first half and leaves the drift unabsorbed. T-09 now
says the achievable thing: you cannot avoid absorbing it, you must not absorb it SILENTLY — the
receipt names the exit code, the differing-row count and one row in full.

## Every other `verify:` re-run this pass

Base: current working tree. `git status --short` shows it differs from `3bfedc9` only in
`docs/harness/DECISIONS-INDEX.md` and `.harness/logs/2026-08-04.md`, so for every command below the
two bases are the same tree.

**T-01 (all digests piped to `validate-digest.py <persona>`, full field set, `printf`-built):**

```
T-01(i)   dev-ops suite:n/a  task_verify:n/a   PASS  -> digest ok, exit 0
T-01(ii)  dev     suite:fail task_verify:pass  PASS  -> digest ok, exit 0
T-01(iii) qa      matrix_ok:false              PASS  -> digest ok, exit 0
T-01(v)   dev     task_verify:no-task          PASS  -> digest ok, exit 0   [regression clause]
T-01(v)   dev-ops task_verify:no-task          PASS  -> digest ok, exit 0   [regression clause]
T-01(vi)  dev     task_verify:bogus            PASS  -> digest ok, exit 0   [CHANGE DETECTOR]
T-01(vii) dev     task_verify OMITTED          PASS  -> digest ok, exit 0   [CHANGE DETECTOR]
```

`(v)` is honestly labelled a regression clause, not a detector: `task_verify` is in no schema yet, so
an unknown key is ignored and `no-task` is already accepted. `(vi)` is its detector partner — an
acceptance clause with no rejection partner is the vacuous shape this feature exists to remove.

**T-01(iv) `run-unit-tests.sh` — NOT RE-RUN.** The dispatch withholds the gate scripts from this
pass. The receipts table records it as not-re-run and cites the architecture reviewer's observed
green (`notes/receipt-harness-backend-dev-arch-review.md:165-166`) rather than restating it as a
fresh run.

**T-02:**
```
grep -c task_verify           harness-digest-dev/SKILL.md      -> 0
grep -q 'PLAN.md'             harness-digest-dev/SKILL.md      -> exit 1
grep -Eq 'BLOCKED.*PLAN\.md|PLAN\.md.*BLOCKED'                 -> exit 1
grep -c 'VERDICT: PASS is rejected' harness-digest-dev/SKILL.md-> 1
grep -q 'no-task'             harness-digest-dev/SKILL.md      -> exit 1
grep -ci receipt              harness-tdd-enforcement/SKILL.md -> 0
grep -ci verbatim             harness-tdd-enforcement/SKILL.md -> 0
grep -Eqi 'receipt.*verbatim|verbatim.*receipt'                -> exit 1
grep -c '^VERDICT:'           harness-tdd-enforcement/SKILL.md -> 1     [F6 guard, regression]
```

**T-03:**
```
grep -q 'task_verify: pass|fail|n/a|no-task' agents/harness-dev-ops.md -> exit 1
grep -A4 'task_verify' agents/harness-dev-ops.md | grep -q suite       -> exit 1
grep -qi 'never the honest answer' agents/harness-dev-ops.md           -> exit 1  [scope guard]
```

**T-04 (re-run because T-02 now appends to the same file, and F6 is new):**
```
awk '/^VERDICT: BLOCKED$/,/^artifact: none$/' harness-tdd-enforcement/SKILL.md \
  | validate-digest.py harness-backend-dev  -> digest ok, exit 0
grep -q 'task_verify: n/a' harness-tdd-enforcement/SKILL.md -> exit 1
```

## Source facts re-derived at this tier, not taken on report

- `validate-digest.py:485` is the `continue` closing the `field in NULLABLE and val in
  PLACEHOLDER_UNSET` branch opened at `:477`; `:486` is `if isinstance(allowed, set):`. F2's restated
  insertion point ("after the `continue` at `:485`, before `:486`") is written into T-01 step (5).
- **`no-task` parses as the plain string and clears the enum check — measured, because D-07's whole
  cheapness claim rests on it and `T-01(v)`'s `digest ok` proves nothing about the VALUE (the field
  is unknown today, so `val` is never compared to anything):**

  ```
  parse_scalar(no-task): 'no-task'
  parse_scalar(bogus):   'bogus'
  PLACEHOLDER_UNSET:     ('none', 'null', 'n/a')
  no-task in PLACEHOLDER_UNSET: False
  parse_scalar("no-task") in {"pass","fail","no-task"}: True
  ```

  `parse_scalar` is defined in `validate-digest.py:281`, not in `harness_yaml`; `PLACEHOLDER_UNSET`
  is `harness_yaml.py:302`. This is the same probe D-05 already records for
  `parse_scalar("false") -> False`.
- **T-01 step (6)'s hint carries a WORDING constraint, added after review.** The new branch fires on
  any missing gated field, which for `dev` includes `suite` — and `suite: n/a` with `VERDICT:
  BLOCKED` is legal (SC-06/REQ-03). So the hint must say a placeholder ALONGSIDE `VERDICT: PASS` is
  what gets rejected, never that placeholders are disallowed. The looser wording would have been
  true of a PASS return and false of a BLOCKED one — F1b's defect class inside the validator's own
  guidance.
- `:468` builds the missing-field hint as `` "`none` if genuinely not applicable" `` for a `NULLABLE`
  field. `:691-692` is `if d.get("stop_hook_active"): return 0`. `:481` is the `GATE_FIELDS`
  consultation, inside the placeholder branch. `GATE_FIELDS` at `:73` is
  `{"dev": {"suite"}, "qa": {"suite","matrix_ok"}}` today.
- F4 anchors in `test-validate-digest.py`, each line printed and read: `:187`, `:290`, `:582`,
  `:717`, `:951`, `:954` are `case(` heads; `:561-564` is the inline digest STRING; `:558` is the
  `_dec156_case(` call line; `DEV_NA` is defined at `:939`, not `:943`. The corrected set is what
  T-01 step (7) now carries.
- The arch reviewer's own `suite:` value is NOT persisted — `runs/arch-review-eng/state.yaml:72-80`
  records only persona, verdict and artifact. I therefore cite its receipt line 166
  ("`run-unit-tests.sh` (full suite): green") for the claim that a non-task dispatch has a truthful
  `suite` answer. That is the fact D-07 rests on for scoping the remedy to `task_verify` alone, and
  it is inference from that receipt rather than a read of the literal field.

## Where F1c cuts, stated because it is not fully independent of F1

T-01 step (6) fixes the hint by DERIVING the allowed values from the schema
(`sorted(a for a in allowed if isinstance(a, str))` when `allowed` is a set, existing wording
otherwise) rather than naming a literal. That is deliberate: under the recommended option the hint
enumerates `no-task` by itself, and under the alternative it enumerates `pass, fail` and is still
correct. **So F1c survives either F1 outcome and is NOT a fourth F1b surface.** Had the hint named
the new value literally, it would have been one.

## Open questions carried up

- **Q1 (BLOCKING) — D-07's shape.** Recommended: a fourth `task_verify` value `no-task`. Alternative
  priced in D-07 and in BRIEF `## Verification gaps`: a declared `task: T-NN|none` field with
  `task_verify` conditional on it.
- **Q2 (non-blocking) — `docs/harness/DECISIONS-INDEX.md`'s undeclared working-tree modification.**
  Not reverted (reverting restores the drift). T-09's precondition is conditional on either outcome.
- **Q3 (non-blocking) — the receipt-path grant above.** `harness-pm` cannot write
  `notes/receipt-*.md`; the dispatch asked for one.

## Not applied, deliberately

Nothing on the LEAVE list was re-adjudicated. The `dev-ops suite: fail` residue stays discharged and
all four of its surfaces are untouched. No task was executed; `validate-digest.py`, the agent files
and the skills are unchanged.

---

# Cycle 2 — S-01 send-back: three stale enumerations

**BLUF.** All three corrected. No task executed, no LEAVE-list item re-adjudicated, both
`## Approval` blocks still `status: pending` with `approved-by` and `date` empty. Q1, Q2 and Q3 stand
unchanged in substance. **Item (1) does NOT change Q1's substance** — Q1 as written above carries no
step list, only D-07's two shapes; the corrected price tag lives at `PLAN.md:144-159`.

## (1) `PLAN.md` — the D-07 redirect-surface list

Re-derived against the ⚠️ markers actually in the file, not from memory:

```
$ grep -n "⚠️" PLAN.md          # before the edit
114   D-07's own recommendation flag — not a redirect surface
199   T-01 intent step (2), the schema clause
305   T-01 intent step (9), cases (g2)/(h2)      <- the "short by one"
362   T-01 verify: clauses (v) and (vi)          <- covered by NOTHING in the old list
455   T-02 verify:, the `no-task` clause — DROPPED, not respelled
482   T-03 intent
572   T-06 intent

$ grep -n "⚠️" PLAN.md          # AFTER the edit, final state — 11 lines, 6 of them redirect sites
114 145 146 213 319 376 469 496 586 878 918
        ^^^ ^^^                     the six sites: 213 319 376 469 496 586
```

The sentence cites the **post-edit** numbers, re-grepped at final state. Citing the pre-edit ones
would have been G-01's failure — a pointer captured mid-edit, right about the site and wrong about
the line. The sentence also states the grep's own arithmetic (11 hits, 6 sites, and what the other
five are: D-07's recommendation flag `:114`, the sentence's own two lines, and two mentions in
`## Verify receipts`), so a reader who runs the grep does not find a count that contradicts the
claim — the non-discriminating-grep shape this feature exists to remove.

Two defects, not one: `(8)` should have read `(8)` and `(9)`, and the marked site at `:362` —
T-01's `verify:` clauses, a surface distinct from its intent steps — was absent entirely.

The closing absolute "does not touch anything else" was removed rather than re-enumerated. It
self-contradicted D-07's own pricing eleven lines above it (`:139-141`: the alternative's new
REQUIRED field "propagates to ... plus all nine fixtures, roughly doubling T-01's diff"). It is
replaced by a scoped, checkable negative:

```
$ grep -n '^  traces:.*D-07' PLAN.md      # at final state
378 (T-01)   471 (T-02)   510 (T-03)   597 (T-06)      # exactly four tasks, measured
```

so the sentence now asserts only that no task OUTSIDE T-01/T-02/T-03/T-06 moves, and names T-04,
T-05, T-07, T-08, T-09 and T-10 as untouched. BRIEF's `## Verification gaps` bypass bullet was added
to the list as a redirect surface — it is written to the recommendation and prices the alternative in
its own closing lines.

## (2) `BRIEF.md:233` — the unit-proven enumeration

Partition re-derived by extracting every SC's own `verify:` line rather than recalling it:

```
automated / evidence: unit -> SC-01..SC-06, SC-13, SC-14, SC-15, SC-17, SC-18   (11)
inspection                 -> SC-07..SC-12, SC-16                                ( 7)
                                                             total = 18, each in exactly one list
```

`:233` now names SC-01..SC-06, SC-13..SC-15, **SC-17 and SC-18**, states that their fixtures are T-01
step (9) cases (g2)/(h2)/(i2), and closes with the property that makes the pair checkable: every one
of SC-01..SC-18 appears in exactly one of the two lists. The `inspection` list was already correct
and is unchanged. The enumeration was NOT made vague.

## (3) T-06's receipt row — RE-RUN, not carried over

All three clauses executed this cycle, base = current working tree:

```
$ awk '/^- \*\*eng devs\*\*/,/^- \*\*qa:/' docs/harness/SPEC.md | grep -c task_verify   -> 0
$ awk '/^- \*\*dev-ops:/,/^- \*\*leads:/'  docs/harness/SPEC.md | grep -c task_verify   -> 0
$ grep -c 'task_verify' docs/harness/SPEC.md                                            -> 0
```

The old row showed only two of the three clauses ("0 / 0"); it now shows all three. It is marked
**RE-RUN this cycle** with the reason, and BOTH facts are stated: the body changed (the `no-task`
spelling in both SPEC.md bullets plus a ⚠️ marker), AND that change could not have moved these
counts, because none of the three clauses reads the enum spelling. T-06 is added to the
changed-task-bodies list in the closing prose.

**One adjacent staleness corrected in the same paragraph**, because leaving it would be this
send-back's own defect shape: the paragraph asserted the working tree differs from `3bfedc9` "only
in `docs/harness/DECISIONS-INDEX.md` and `.harness/logs/2026-08-04.md`". Re-measured this cycle:

```
$ git status --short
 M .harness/logs/2026-08-04.md
 M docs/harness/DECISIONS-INDEX.md
?? .harness/features/FEAT-07-verify-teeth-batch-probe/
?? .harness/notes/grilling-perf-batch-1-2026-08-04.md
```

Two untracked paths the word "only" excluded. The load-bearing inference is unaffected —
`docs/harness/SPEC.md`, `.claude/**` and `.claude/skills/harness/bin/**` show no modification, so
every base claim in the table holds — and the paragraph now names all four paths and states that no
`verify:` command in the table reads any of them.

## Scope held

Nothing outside the three items changed. The LEAVE list, D-07's shape, the seven collation criteria
and both `## Approval` blocks are untouched. No gate script was run — `check-docs.sh`,
`check-state.sh`, `check-domain.sh` and `run-unit-tests.sh` are all withheld by dispatch; every
command above is `grep`, `awk` or `git status`. Nothing was written under `runs/`.

**My own return block was piped through the validator, as the dispatch mandates** — the one piece of
receipt execution cycle 1 did not carry:

```
$ printf '<this cycle's VERDICT+DIGEST block>' \
    | python3 .claude/skills/harness/bin/validate-digest.py harness-pm
digest ok
EXIT=0
```

Returning a PM digest unvalidated on the feature whose charter is removing checks that look real and
never run would have been that exact shape.

**One internal contradiction resolved, not just a name added (item 3).** `PLAN.md:23-24` — the Lanes
section — already read "T-01, T-02, T-03, **T-06** and T-09 changed their BODIES" on the previous
cycle, while the receipts prose named only T-01/T-02/T-03/T-09. Two sections of the same file
disagreed about the same fact; they now agree. Checkable in one grep — and this one was RUN, because
the first form I wrote for it (`grep -n 'changed their BODIES\|changed their task bodies'`) returned
only ONE line: `:23`'s phrase wraps mid-sentence, so the substring does not exist on any single line.
The form that discriminates:

```
$ grep -nE 'T-06(\*\*)? and T-09' PLAN.md
23:  ... T-01, T-02, T-03, T-06 and T-09 changed their      <- Lanes, correct all along
915: T-03, **T-06** and T-09 all changed their task bodies  <- receipts prose, corrected this cycle
```
