# Plan revision c2 — the operator's consolidated REVISE — BUG-1308-expertise-replace-drop

BLUF: the cycle-1 high finding is closed in the spec, not deferred. `T-01`'s application is now
specified against **stable target identity** — every op resolves to a `(section, id)` key, never an
index — and the composition that would have exposed the index-shift bug is covered by `u11`/`u12`
(unit) and `case19` (integration). Requiring `section` on every op deleted one resolution mode, one
ambiguity condition, `u4` and `case14(a)`. The concurrency case now forces contention by taking the
production lock in the test process. Plan reloads, `approval.status` is still `pending`, `panel:` is
untouched, `check-plan-routes.py` exits 0.

**The invariant, as written into `T-01`'s intent, quoted:**

> no index resolved against the base snapshot is ever used to address the mutated list.

## Per finding

**PF-f4d258f365f54f04d9cc976baf0ad981 (high) — closed in spec.** `T-01` Step B now yields a
`(section, id)` KEY and states no op carries, stores or computes a position. Step D is a single pass
that REBUILDS each affected section from the base snapshot — walk base entries in original order,
drop / substitute / keep by key, then append adds in proposal order — so a replaced entry keeps its
ordinal among survivors and the merged section is independent of op order for replace and drop. The
invariant above is stated as one checkable sentence. `D-06` was amended in the same pass: it said a
replaced entry keeps its *exact index* and section length is unchanged, which is false when the same
proposal also drops an entry above it; it now speaks of relative order. New cases: `u11` (drop `P-01`
at original index 0 with replace `P-05` at original index 4, asserting surviving sequence
`[P-02,P-03,P-04,P-05]`, `P-05`'s marker text, and the identical result with the ops reversed), `u12`
(two drops at original indices 0 and 3), `case19` (the same composition through the CLI, asserting
file-order id sequence and byte-identical output under reversed op order).

**PF-3f8a11143ba40f67b0f326d532381d5e (med) — accepted, followed through.** `D-02`: `target` and
`section` are BOTH required on every op; no optional-section affordance, no whole-file resolution.
Its `because:` no longer justifies the affordance by the ambiguity case it made reachable — the
reason is now the operator's: a uniform required key removes an agent-facing footgun and removes an
entire resolution mode. `D-03` drops to exactly two conditions, (a) duplicate id inside one section
and (b) two ops resolving to one `(section, id)`, both still exit 11 with `AMBIGUOUS TARGET` naming
section, id and reason; the `because:` records that an unreachable refusal branch is dead code and an
enumerated set is auditable only if every member is reachable. `D-05` adds a missing `section` on an
op of any verb to the exit-12 MALFORMED OPS set. `D-12` needed no change: it already says *"a drop
and an add of the same section and id in one proposal exit 11"*, which is exactly `D-03(b)`.
**Cases removed: `u4` (unit) and `case14(a)` (integration).** Neither number is reassigned; `T-01`
and `T-02` say so in place, so a future reader does not read the gap as an omission.

**PF-21e98fb21fbbe9fefe7c47cc9784c99b (med) — closed.** `case18` no longer relies on Popen-before-
wait. The test process takes the production lock itself via `harness_merge.acquire(<file>.lock)` —
the same primitive `locked_update` uses, on the same derived path — spawns both children inside the
block, and polls them every 0.05s for a **2.0-second hold window** asserting neither exits. **RED: a
child that completes while the test holds the production lock**, because it is not taking the shared
lock (`D-09`). No environment variable, no injected sleep, no test-only flag, no edit to
`expertise-merge.py` or `harness_merge.py`. 2.0s is far below `harness_merge.LOCK_TIMEOUT_SECONDS`
(10.0, read at `harness_merge.py:36`), so a correctly-locking child is still waiting rather than
refused at exit 6 — that exit is itself a FAIL. Budget: 2.0s hold + two 20s waits, **under 45s on
every path including FAIL**. `SC-11` restated to match, bound included.

**PF-0fd81890be0279f72e1fd44bc27f9828 (med) — closed.** `T-03.verify` now loops over ten tokens
against a normalised copy of the skill text (whitespace collapsed; backtick, asterisk, underscore
stripped): `expertise-merge.py ops --file`, `replace on the surviving id`, `drop of the absorbed id`,
`7 CONFLICT`, `8 CAP EXCEEDED`, `9 not an Expertise file`, `10 MISSING TARGET`,
`11 AMBIGUOUS TARGET`, `12 MALFORMED OPS`, `apply --entries`; it names the missing token and exits 1.
`T-04.verify` greps the DEC-216 region for `Chose:`, `Over:`, `Because:`, `Tradeoff accepted:`,
`DEC-66`, `DEC-95`, `DEC-145`; SPEC.md for `expertise-merge.py ops`, `10 MISSING TARGET`,
`11 AMBIGUOUS TARGET`, `12 MALFORMED OPS`; the index row ruling; then runs the generator test. Both
intents were amended so the doc author is told the exact token pairs their verify greps. Both blocks
were run against the unbuilt tree: `T-03` exits 1 reporting `expertise-merge.py ops --file`, `T-04`
exits 1 reporting `Chose:` — so each discriminates rather than passing vacuously.

**PF-5674cd3640c7f69731e86e655135ca8c (low) — softened, not dropped.** `case17` keeps its whole
value — the two set relations (`CONTRACT − ACCEPTED == REWRITTEN`, `ACCEPTED − CONTRACT == ∅`), the
probe-derived `ACCEPTED`, and both mutation copies. What changed is `REWRITTEN`'s detector: instead
of one verbatim prose sentence, it is `{"merge"}` iff the **normalised** text carries BOTH phrases
`replace on the surviving id` and `drop of the absorbed id`. Connecting words, punctuation, reflow
and emphasis are now the author's; the two load-bearing phrases are not. Drift detection is not lost:
mutation copy (a) removes `drop of the absorbed id` and must still redden. A3 is intact — `D-10`
stands, the contract keeps `merge`, and the tool still refuses `op: merge` at exit 12 naming the
rewrite; the rewrite stays pinned **character for character where the feature owns the characters**,
in `expertise-merge.py`'s own refusal line, asserted by `u7`. `D-10.because` and `SC-09` were amended
to say this, so no artifact still claims a literal-sentence pin.

**PF-12c69147fda194c41e76361acb23eef1 (low) — no action, as the validator lead recommended.** `u10`
stands; `SC-07` names it and it is the cheapest anti-revert evidence the feature has.
**PF-f9161ebeb204bb05a72667ebc1f7df84 (info) — no action.**

**New `D-15`** records that the operator ruled REVISE rather than overrule at the cycle-1 signature
review, names the four rulings, and points at this note. `approval:` untouched; `panel:` untouched —
findings keep `disposition: open` and the reader's own severity, because the panel is re-run and
re-recorded after this revision.

## Coverage after the revision

| REQ | SC | Tasks |
|---|---|---|
| REQ-01 replace | SC-01, SC-12 | T-01, T-02 |
| REQ-02 drop | SC-02, SC-12 | T-01, T-02 |
| REQ-03 caps | SC-01, SC-06 | T-01, T-02 |
| REQ-04 missing target | SC-03 | T-01, T-02 |
| REQ-05 ambiguous target | SC-04 | T-01, T-02 |
| REQ-06 byte-identity on refusal | SC-05 | T-01, T-02 |
| REQ-07 apply unchanged | SC-06, SC-11 | T-01, T-02 |
| REQ-08 contract agrees | SC-09, SC-10 | T-03, T-04, T-02 (case17) |
| REQ-09 regression shapes | SC-07, SC-08, SC-12 | T-01, T-02 |

SC changes: **SC-04 amended** (three ambiguity conditions → two), **SC-09 amended** (phrase-pair
detector, normalised text), **SC-11 amended** (deterministic contention, RED named, 45s bound),
**SC-12 added** (multi-op composition in one section, both orders). **No SC removed.** REQ-09 amended
to name the composition shape. Every SC still declares one deterministic `verify:` method.

## Open questions

- None blocking. One hazard the required-`section` change created was found and closed in this pass
  rather than raised: `case17`'s `ACCEPTED` probe emits one op per candidate verb, and every op now
  requires `section`, so an unknown-verb probe could be refused at exit 12 for the missing key
  instead of for the verb — same code, different reason, silently mis-populating `ACCEPTED`.
  `T-02`'s intent now requires every probe op to carry a `target` and a `section` that exist in the
  throwaway fixture, and to FAIL the case loudly when a refusal line names a key rather than a verb.
