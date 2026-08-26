# FEAT-37 — T-05/T-06 rewritten to subsume in place

**Conclusion.** T-05 and T-06 no longer instruct any amendment form. Both now widen/correct the
entry body itself, and each names, per item, what survives and what is cut so the documentor does
not re-judge it. D-09 records the ruling. `plan.yaml` parses: `6 pending` (exit 0).

## Check (a) — gen-decisions-index.py: verify blocks need NO change

Confirmed the operator's reading by running it. `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout` → exit 0;
`diff` against the committed index → exit 0 (index is clean at HEAD of the worktree).
`compute_amendments` emits an `am.N` span only when `AMEND_HEADING_RE`/`AMEND_BOLD_RE` match; absence
emits nothing and is not an error (`gen-decisions-index.py` lines 148ff and the `if amend_span:`
branch in `build_index`). Generated DEC-199 (row 217) and DEC-201 (row 219) carry no `am.` token.
The verify half is a generated-vs-committed diff, not a token assertion, so subsume-in-place leaves
it correct. **Both `verify:` blocks untouched.**

## Check (b) — T-06's bare-quote paragraph: SHRANK, did not die

Heading is now "THE VERIFY GRADES EVERY OCCURRENCE, INCLUDING ANY YOU INTRODUCE". The obsolete
rationale (an amendment quoting what it replaced) is gone; the safeguard is restated on its own
terms — whole-file scan, graded per containing sentence, leave no unqualified occurrence and
introduce none, and if a sentence must name the old claim the qualifier sits in that same sentence.

## Survives / cut calls I made (each written into the intent)

DEC-201: scope SURVIVES; two-moves mechanism SURVIVES compressed; specimen id + 40 cycles + 3.5
minutes + sidecar lines 35-186 CUT; "hook was ruled out" CUT (investigation narration, changes no
behaviour, held by D-07 and issue 831); platform dispatch text SURVIVES (it constrains how the rule
must be written); inoculation SURVIVES; fix-surface pointer SURVIVES, its grep-returned-0 CUT;
no-message-tool SURVIVES in full; "wake not re-measured" CUT (in one voice there is nothing to
disclaim).

DEC-199: "entry was corrected / DEC-188 does not apply" CUT (statement about editing); different
child sets SURVIVES as the reason, transcript id `agent-a89be3fd837d1b779` as a bare pointer only;
line numbers 178/392 and microsecond `started_at` CUT; no-already-refused-state mechanism SURVIVES;
platform eight-block cap CUT (answers a different question); consequence SURVIVES in full;
cross-site pointer SURVIVES rewritten to present tense.

## Open question

`D-02` and `D-11` still read "DEC-201 is AMENDED" / "DEC-199 is AMENDED rather than STRUCK"
(plan.yaml lines 54 and 82). Their substance is unchanged by the ruling; only the word is now the
wrong form. I did not edit them — the dispatch scoped me to T-05/T-06 plus D-09, and D-09 already
records the supersession. Non-blocking; the operator holds the pen.

## Commands (all completed)

- `gen-decisions-index.py --stdout` → 0; `diff` vs committed index → 0
- `plan-merge.py apply` (D-09) → 0, printed `ADDED D-09`
- `python3 -c "... safe_load ..."` → `6 pending`, exit 0
- `check-plan-routes.py` → `0 violation(s) across 1 plan(s)`, exit 0
