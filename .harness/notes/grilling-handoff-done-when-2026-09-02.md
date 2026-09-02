# Grilling — Handoff Done When contract — 2026-09-02

## Destination

Every newly written or edited orchestrator handoff states the immediate next action's completion boundary in a required fifth `## Done when` section. The contract is mechanically enforced without invalidating untouched historical handoffs.

## Settled

- Separate section or nested field? → A fifth standalone `## Done when` section, matching the benchmarked design.
- What does it describe? → The immediate action in `## Next`, not the entire next phase or feature.
- What is its shape? → Exactly one `Scope:` line containing a concise action label, followed by one to four `Authority:` lines and no other prose.
- How do multiple authorities combine? → Logical AND: every listed authority must be satisfied.
- What may an authority cite? → One of four bounded types: plan task `verify`, BRIEF success criterion, validation finding, or explicit user approval gate. Source-code locations alone are not authorities.
- What pointer syntax is used? → Typed, machine-readable pointers such as `plan-task:T-03.verify`, `brief-sc:SC-04`, `finding:<path>#F-02`, and `approval:<path>#<heading>`.
- How strongly are pointers checked? → Every pointer must resolve to an existing target when the handoff is written; syntax-only validation is insufficient.
- What happens to historical notes? → Untouched four-section handoffs remain valid. Every newly written or edited handoff must use the five-section contract.
- How is length bounded? → Keep the existing 60-line whole-file cap. Do not impose section caps on the four variable narrative sections; bound only `Done when` by its fixed shape and one-to-four authorities.
- How is the model benchmark used? → Permanently gate deterministic structure and pointer resolution; rerun the comprehension benchmark during review, but do not add the nondeterministic model benchmark to every normal test run.

## Not yet specified

- None.

## Out of scope

- Rewriting the historical handoff corpus.
- Raising the 60-line handoff cap.
- Section-specific caps for `Next`, `Trust`, `Dead ends`, or `Working set`.
- Claiming token or latency savings from this change.
- Making the exploratory model benchmark a permanent automated release gate.

## Facts I verified (so pm does not re-derive them)

- The existing contract requires four headings and a hard 60-line total; `check-domain.sh` rejects malformed writes and `check-state.sh` INV-17 scans persisted `handoff-*.md` files for missing or empty sections and excess length — read at `b7956fc4`.
- Across 137 parseable current handoffs, median/raw section spans were Next 8, Trust 17, Dead ends 12, Working set 6; their independent 95th percentiles sum to 67 before structural overhead, so per-section caps would weaken or conflict with the 60-line shared budget — measured 2026-09-02 at `b7956fc4`.
- The three highest-numbered available plans are 1,205–1,637 lines and all support task-level pointers through stable `T-NN` ids and `verify` fields; phase-level completion is not a plan section, and some real next actions instead derive from findings or approval gates — reviewed FEAT-48, FEAT-50 and FEAT-51 at `b7956fc4`.
- A controlled 30-run comparison over the FEAT-48/50/51 build handoffs increased required-fact coverage from 65.9% to 96.5% and perfect responses from 3/15 to 13/15 with the fifth section. Total character volume increased 2.8%; latency was noisy and inconclusive. This is directional evidence, not an overall Harness accuracy claim — measured in this grilling session.