# Security review c1 — BUG-285-canonical-reader

**PASS.** The exact repository-policy range `8c3143bd5668ce11186a2a1f8dbe784ff9639d88..5be21a432b87ed648c0bed50fbf9a2642c84e0a9` is security-relevant because it centralizes reads of locally authored and externally returned artifacts across enforcement callers. The concrete worktree `HEAD` was measured as `5be21a432b87ed648c0bed50fbf9a2642c84e0a9`. No new exploitable auth, secrets, injection, deserialization, data-exposure, SSRF, or authorization surface was found.

## Original finding dispositions

- **F-01 — resolved.** `.claude/skills/harness/bin/check-plan-routes.py:1290-1311` no longer treats every raw parse in `artifact_accessors.py` as accounted by file identity. Accounting now requires a signed row identity, exact canonical remedy, or exact relocated implementation. The c1 self-test injects an unclassified raw JSON call in that module and the receipt records pre-fix exit 1/current exit 0. This strengthens the tampering boundary; it does not consume attacker-controlled strings or add an execution sink.
- **F-02 — resolved.** `tests/unit/test-feature-json-reader.py:123-155` now uses issue 285's exact comment-bearing YAML/invalid-JSON inverse: the legacy YAML reader returns the complete expected mapping while `load_feature_json` refuses the same bytes. This is test-only input and introduces no parser or deserialization path in production.
- **F-03 — resolved.** The backend receipt records the current cutover assertion failing against compatible pre-cutover commit `5369a9ba8326fb95a74ee32b3468cb1268b960f4` and passing at the corrected tree. No c1 production change expands input reachability.
- **F-04 — resolved.** The main-session receipt records exact 29-case enforcement-output equality at strict-accounting commit `0ad0d0b8490bcfa84f5bf3a6c9aec0f213460800` and a deliberate divergent baseline exiting 1. The historical comparator and temporary baseline remained outside the shipping tree, so this evidence added no runtime input or output interpreter.

## SEC-01 disposition

**SEC-01 remains med/substance, assessed and dismissed.** `.claude/skills/harness/bin/artifact_accessors.py:151-159` still treats a present top-level `github` or `factory` non-mapping as absence-equivalent. The signed T-02/SC-03 contract specifically requires rejection of wrong-typed present `parent` and `issues` fields inside a GitHub-style mapping while preserving missing blocks as legitimate absence; it does not establish a top-level block-shape invariant. No c1 change alters that scope or mechanism. The unmitigated theoretical integrity case is therefore scope-closed, not an active must-fix finding.

## Security census and threat model

- The c1 production delta is confined to the AST classification guard in `.claude/skills/harness/bin/check-plan-routes.py`; it removes a file-wide exemption and narrows acceptance. The accompanying integration/unit changes supply adversarial classification and strict-parser evidence only. The two c1 receipt commits contain hashes, local paths, commands, and expected output but no credential-shaped value.
- **Tampering:** mitigated for the c1 guard and comment-bearing feature input; unknown raw readers require explicit accounting, and permissive-YAML bytes are rejected by the strict feature reader. SEC-01 is separately unmitigated but scope-closed as stated above.
- **Information disclosure:** mitigated. C1 adds no production diagnostics containing payload bodies, credentials, or cross-user data; receipts contain only test material and local evidence paths.
- **Spoofing / elevation of privilege / repudiation:** no new auth decision or principal selector exists in either c1 code change. Narrower accounting improves auditability.
- **Injection / SSRF / unsafe deserialization / denial of service:** no shell, SQL, template, spreadsheet, URL, redirect, network, or unsafe object-deserialization sink is added. Inputs are fixed test strings or AST candidate dictionaries; the production check remains bounded by the scanned repository source set.

No active security finding or blocking question remains. The intentionally stale feature.json review pin was not treated as a defect, per fix-team scope.
