# Security review — T-01 — c0

**PASS — in scope; no exploitable security regression found.** Reviewed only `4a05030d..3e6add2af05f5b801afec1ef69440fe54e1529a4`, using pinned `git show` sources. Findings and must-fix: none. Maximum severity: none.

## Scope and census

Pinned diff: 4,975 changed paths, comprising 4,890 deletions and 85 retained/add/rename paths. The latter comprise three skills, 18 bin paths (17 Python and one schema), one project config, three product documents, 20 intake/evidence paths and 40 test/manual paths. Deletions are historical corpus/records and the two authorized manual probes; the accessor extension is an exact R100 relocation. No dependency, network endpoint, credential transport or export-format addition appears in this census. All retained patch additions, including evidence/config/docs, were searched for credential-shaped strings and credential assignments; no credential value was identified. This is a delta review, not a claim of historical whole-repository clearance.

Scope is **IN**, because canonical-reader plan ownership becomes optional and merge/sweep receipt enforcement changes. These are Tampering/privilege boundaries even without a new public input.

## Boundary assessment

- **Feature record → merge/destructive sweep (T/E):** `feature_schema.py:579-589` removes the age-based success fallback and retains repository/provenance checks. `merge-gate.py:263` and `post-merge-sweep.py:252` consume the same predicate; an absent/incomplete receipt no longer gains permission by feature identity. `gh-sync.py:1683` refuses missing Build receipts. Removal tightens rather than bypasses authorization.
- **Classification inventory → enforcement audit (T):** `check-plan-routes.py:1180-1197,1606-1664` deliberately removes implicit historical plan ownership. A row without `plan` no longer proves task ownership; it does **not** skip DEC-174 routing, AST coverage, canonical-remedy or disposition checks (`:1200-1246,1376-1445`). Explicit unreadable/malformed ownership plans still produce findings and exit 2; unresolved migrations still exit 1 (`:1594-1603`). The 28 removed pointers, including BUG-20261006, do not authorize runtime writes. Editing this committed enforcement inventory already requires enforcement-source authority; no lower-privilege actor gains a capability here. Synthetic ownership/route assertions are retained in `tests/integration/test-check-plan-routes.py:1861-1940` (inspected, not executed).
- **Persisted run/handoff/branch records → integrity checks (T/R):** `feature_schema.py:187-209`, `check_state/seams.py:53-84` and `feature_corpus.py:460-469` remove identity/baseline skips. Rules now apply uniformly, including Kaya; no Kaya data modification or new exception is introduced.
- **Probe/record retirement:** SC-04 security inspection finds DEC-204's removed sentence is only the retired live merge probe; lifecycle/lineage authority remains (`DECISIONS.md:6430-6574`). DEC-159/213/215/220 describe the uniform rules/relocation; DEC-250 acknowledges probe retirement without changing its exact-lineage authorization. Approved retirement/pruning is not treated as an attacker-controlled deletion mechanism.

## Evidence limits and questions

Read BRIEF and plan before diff, binding grilling and pinned operator survivor answer; consulted pinned SPEC §§2/8/9/11/15 and relevant decisions. No source edits, test/build/lint/formatter runs, or credentialled live probes. QA owns final matrix and exact-pin standalone verification; builder receipts are not represented as my execution evidence. Open questions: none.
