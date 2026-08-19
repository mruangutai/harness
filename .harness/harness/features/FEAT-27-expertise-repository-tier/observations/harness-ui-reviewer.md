# Observations — harness-ui-reviewer — FEAT-27-expertise-repository-tier

- 2026-08-19: diff b4659cd..9b929de is a 57-file, no-rendered-UI, no-DESIGN.md diff (measured:
  extension census 48 md / 3 py / 3 sh / 2 yaml / 1 json, zero html/css/scss/tsx/jsx/vue/svelte/less).
  Dispatch named an adjacent non-rendered surface (inject-expertise.sh's header/precedence text,
  check-expertise.sh's advisory line) as in-remit per P-06 — worth the look: found a real, low-severity
  completeness gap. The precedence line ("repository over project over global, by specificity") is
  only emitted when a repository-tier block is present; the pre-diff project header's unconditional
  "authoritative on conflict" phrase was dropped and not replaced for the global+project-only
  combination, so that combination now states no precedence at all. Confirmed via test-census: none
  of test-inject-expertise.py's 13 cases populate $HOME/.harness/expertise/<agent>.md (the global-tier
  fixture), so this exact combination is untested. SPEC.md's own wording ("whenever a repository block
  is present") honestly documents the conditionality rather than hiding it — this is a coverage gap
  in a deliberately-designed contract, not a hidden regression.
