# Code-review distillation

**Accepted C-CR1 as craft Outcome O-08; declined C-CR2 and C-CR3.** No diff reviewed, suite run, or commit made. No open questions.

- **C-CR1 — accepted.** Map each closure counterexample to a governing clause before grading. The c1 ruling found one required gap (text mode normalized line endings), not three: c0 prescribed the absence marker, the refusal marker could not collide with a plausible return, and silence was not in the criterion’s list. The final QA receipt shows the CRLF mutant distinguishes the fixed test. This check precedes the consequence-based severity rule in O-06. It displaces O-08’s less reliable shortcut that stricter code should drive a spec amendment.
- **C-CR2 — declined.** The row-carrying example overturned the signoff’s generalization, but P-08 already calls for probing beyond the example’s boundary and O-04 calls for comparing identical input at base when testing class membership. P-03 already requires checking record claims against code. A separate entry would restate the combined method.
- **C-CR3 — declined.** The c1 ruling excludes this feature’s compliance records from its source/behavior allowlist. That is a scope interpretation, not a blanket path exemption. Keep auditing the full range under P-16; report records separately when the governing scope warrants it. No new entry displaces a broader rule.

**Applied:** craft `replace Outcomes/O-08`, batch `658ff3df4e29e7386883f8253c55483f6d96eca88c487c17e9eb9fa896be6272`. Receipt (beside this note): `expertise-receipt-e944f97ef044b422124160f69b4106edce2386bc41db0ccf58c5962a7f421924.json`. Tool counts before→after: Patterns 15→15; Gotchas 15→15; Outcomes 10→10; Open 0→0. Repository tier untouched.
