# Security review — BUG-285-canonical-reader

**FAIL.** The canonical reader does not enforce one signed trust-boundary invariant: a present top-level `github` or `factory` value of the wrong type is accepted as though the block were absent. This is a medium-severity tampering/fail-open defect and a must-fix SC-03 violation.

- `base_sha`: `8e3bda037bf62e89966d898ccfdf8c9cabcdcdea`
- `review_sha`: `da8932a065137bcfbdb85fc2489b5bdd01936a6f`
- Reviewed range: `base_sha..review_sha` only. The base is the authoritative planning base named by BRIEF.md; mutable HEAD and the later `main` merge-base were not used.

## Ranked finding

1. **MED · substance · task scope · T-02 · harness-backend-dev / team** — `.claude/skills/harness/bin/artifact_accessors.py:151-159` (`_validate_recorded_block`). The function returns for every non-dict block, although BRIEF SC-03 requires any *present* `github` or `factory` nested field with the wrong type to be refused. Reproducible scenario: supply `load_feature_json(text='{"feature_id":"F","github":[]}')` or the corresponding `factory` value; strict JSON parsing succeeds and the accessor returns the document. A maintainer or process able to hand-edit `feature.json` can therefore turn a corrupted recorded-issue block into absence at the shared boundary; callers using `.get()`/`isinstance()` can omit recorded linkage rather than diagnose tampering, undermining the duplicate-creation guard that SC-03 assigns to this accessor. The T-02 shapes receipt covered wrong-typed `parent` and `issues` *inside a mapping*, not the wrong-typed parent block. Remedy: distinguish missing/null from present wrong type in `_validate_recorded_block`; retain the sanctioned absent/null behavior, but raise `FeatureJsonError` for every present non-mapping block, and prove both `github` and `factory` at the public accessor plus the issue-creation consumers. No payload value needs to appear in the diagnostic.

## Security surfaces inspected

- Canonical input boundary: strict JSON duplicate-key/non-finite rejection, UTF-8 file reads, mapping requirements, mutually exclusive path/text selection, feature recorded-field validation, strict YAML plan/fleet/manifest/frontmatter/OMP routes, and GitHub response parsing in `artifact_accessors.py`.
- Trust-boundary callers: hook payload readers and policy gates (`bash-write-guard.py`, `branch-create-gate.py`, `check-domain.py`, `dispatch-guard.py`, `gh-close-gate.py`, `merge-gate.py`, `plan-sign-gate.py`, `post-merge-sweep.py`, `validate-digest.py`); factory/GitHub/board consumers and validators migrated in T-03 through T-07.
- Diagnostics/data exposure: strict parse errors report context, structural key names, parser location/type, and filesystem errors; they do not interpolate raw JSON/YAML payload bodies or rejected values. No new log/export/spreadsheet surface or credential-shaped committed value was identified in the pinned production diff.
- Injection/filesystem: no new SQL, shell interpolation, redirect, SSRF, or export formula sink was introduced. File accessors accept caller-selected paths but do not themselves derive paths from untrusted payload fields; containment remains caller-owned. Atomic `harness.json` writing uses same-directory temporary replacement.
- Diff census: all 142 paths were classified—production reader/caller changes above are in scope; targeted tests/classification fixtures are evidence surfaces; plan/BRIEF/decision-index/docs and mechanical import/catch relocations have no independent executable security surface.

## STRIDE assessment

- **Tampering — unmitigated:** present wrong-typed feature linkage blocks cross the canonical reader as absence-equivalent (finding 1).
- **Information disclosure — mitigated:** normalized strict errors omit payload contents; only caller context/path, offending key name, type, and parser location are exposed.
- **Denial of service — mitigated for parsing semantics:** duplicate keys, non-finite constants, malformed/non-UTF-8 input, and wrong result mappings fail closed; no unbounded recursion or attacker-controlled allocation newly introduced beyond whole-artifact reads already inherent in these local artifacts.
- **Spoofing / elevation of privilege — mitigated except finding 1's integrity gap:** manifest-domain parsing stays strict and enforcement callers retain blocking behavior; no new credential or authorization selector is sourced from parsed payload content.
- **Repudiation — partially mitigated:** corruption is generally contextualized, but finding 1 suppresses the canonical corruption signal by accepting the document.

No unowned scope change or blocking open question was found. Per dispatch, no tests or commands beyond read-only diff inspection were run.