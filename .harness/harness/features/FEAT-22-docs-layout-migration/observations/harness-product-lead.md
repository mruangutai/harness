# Observations — harness-product-lead — FEAT-22-docs-layout-migration

- 2026-08-15: I sent pm a list of five fold-in items as "could not find on disk", greppping for MY
  OWN wording of each. All five were already there under pm's wording (`BOTH of the list's
  consumers`, `WHY THIS TASK RUNS AFTER T-02`, `MUST STAY UNTOUCHED`, `IT IS A PATH SUBSTITUTION,
  NOT A REFLOW`, `NOTE what this state is NOT`). Cost: pm spent a chunk of a resume re-deriving
  claims it had already landed. The check that would have worked is grepping for the FACT (the
  cited line number `339-343`, `412-414`, `:736`) rather than for my phrasing of the instruction —
  a member writes its own prose but carries the anchor verbatim.

- 2026-08-15: my dispatch to eng-lead asserted "`depends_on` is a strict chain T-01→…→T-11". It was
  false — T-05 and T-06 are both children of T-04 and nothing depended on T-05, which was exactly
  the hole eng-lead's MF-2 turned on. I had READ both lines earlier in the run and still wrote the
  summary from the shape I expected. A dispatch premise I state as fact is one the reviewer may
  spend its spawn disproving instead of reviewing.

- 2026-08-15: the two blocking defects in this plan were BOTH in gating, not design — T-05's verify
  unsatisfiable across [T-02, T-09), and the atomic commit landing with no suite gate. I had read
  T-05's verify block and `test-gen-decisions-index.py:361-363` (which FAILs, not SKIPs, on a missing
  index) in the SAME session and did not compose them. Reading two halves of a contradiction is not
  the same as checking them against each other; the composition is the work.

- 2026-08-15: pm overturned a remedy shape proposed by eng-lead and endorsed by me (drop T-05's
  suite check) with a stronger one (pin the expected failure: 0 unit FAILs, exactly 1 integration
  FAIL, and it must be `test-gen-decisions-index.py`). Both times a member overturned advice in this
  feature it was right and it had primary-source evidence. Worth dispatching with "say why with
  evidence rather than adopting deferentially" as standing text — it was in the send-back and it
  worked.

- 2026-08-15: HARNESS DEFECT, raised as an open_question rather than absorbed. A lead hosting
  background agents has no way to idle-wait: ending a turn while a subagent is in flight trips
  `validate-digest.py --hook` (no VERDICT/DIGEST/artifact), and the only way to hold is to keep
  making tool calls. It bit twice. The second time it pressured me into issuing send-back 2 while
  eng-lead was mid-review — a sequencing decision I had explicitly reasoned AGAINST one turn
  earlier, reversed under hook pressure rather than on evidence. It cost nothing here because the
  delta was three prose blocks I could enumerate, but the mechanism is one that trades review
  freshness for contract compliance.

- 2026-08-15: pm's `sc_status` in two consecutive digests contradicted its own signed BRIEF — six of
  eleven rows carried a `method:` inverting the BRIEF's (`inspection` where the BRIEF said
  `automated` and vice versa), and SC-12 was omitted entirely. The ARTIFACT was right in both cases.
  No goal-check ran, so the contract value is `[]`; rebuilt it rather than re-spawning over a
  report-only defect (O-02).

- 2026-08-16: I passed `model: sonnet` in the re-grade dispatch to pm and `dispatch-guard.sh`
  blocked the call outright (DEC-152/155). No agent launched, so it cost one turn and not a spawn —
  but the reflex is worth naming: I reached for the model knob because the task looked mechanical
  (re-grade seven ids), i.e. I was optimising cost on a dimension that is org design and not mine.
  The guard's message is the correct handling; the re-dispatch without the parameter was identical
  in every other respect.

- 2026-08-16: two "survivors" numbers in this feature's own record disagree because they are
  different measurements under the same label. pm measured **173** at `e26e628` with 3 under
  `bin/`; the boundary note's depth sweep recorded **174** with 5 under `bin/`, and its appended
  CORRECTION re-derives **173** post-fix with 5 under `bin/`. The note's method line names a
  two-spelling command (`docs/harness` OR `"docs", ?"harness"`) with the feature dir excluded; pm's
  earlier bin/ enumeration is consistent with a single-spelling grep. The spelling gap explains the
  bin/ 3-vs-5 but does NOT close the totals (174 − 2 = 172, not pm's 173), so at least one further
  knob differs — exclusion scope, or tracked-vs-working-tree. Practical rule: when grading a count
  clause, match the INVOCATION before comparing the number; two totals that happen to agree under
  different commands verify nothing (G-01).
