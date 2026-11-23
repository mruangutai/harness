# Rulings after validate c2 (ESCALATE) — FEAT-2452 — 2026-11-23

Ruled by fable-advisor (AdvisorD6Esc), which holds the operator's delegated approval. Full text: agent://AdvisorD6Esc.

## OQ-VC3-1 (blocking): R1, wayfind drops a relation's repository
- **Authority:** operator delegation. `gates.review = advisory_unless_high`, so only an operator-level ruling disposes of a reader's high.
- **Gap:** confirmed at source and at base b788e9da. The defect predates the feature, which narrowed the class: it added the number equality and the typed shapes. It is outside SC-03's signed text, and both signed rework rounds are spent.
- **Ruling (a):** ship, and backlog R1 together with security S2 as one issue.
  - Every wrong write lands in the local repo and is reversible; the frontier misdirection is read-only.
  - Option (b) would spend an unbudgeted round on wayfind semantics under a transport-consolidation mission.
- **Constraints:**
  - The backlog issue carries both ratings unreconciled, the measured scenarios, the blast radius and the remedy direction. **Filed as #2470** (readback `notes/repo-identity-backlog.json`, OPEN, body byte-exact to `notes/repo-identity-issue-body.md`).
  - The ship record cites #2470.

## OQ-VC3-2 (non-gating)
- **Ruling:** fix V1/V2 wording now and backlog A-1/A-2/S1. S1 rides in #2470.
  - V1 and V2 are this feature's own deliverables stating falsehoods.
  - A zero-behaviour delta needs no new validate.
- **Constraints:**
  - Touch only github-mirror.md:106, the test-factory-gh.py:2204 comment and the fix note's disclosed-limit line.
  - Evidence: the T-01 and T-05 verifies, plus `git diff --stat <review_sha>..HEAD` teed to `notes/post-review-delta.txt`.
  - The ship record names this post-review delta.
  - A-2's backlog row notes that the null-payload exit-1 change is unpinned.

## OQ-QA-c3-2: backlog to the harness owner
Repro pair: `> /tmp/x/mut-$m.txt` is refused while the literal `/tmp/x/mut-3.txt` passes. Workaround: use literal paths.
