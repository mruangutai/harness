# Handoff — FEAT-36-merge-gitignore-coverage, build → validate — written at ac8533876d5539bfa5db50802b3a3c321add89a8, seq-4

## Next

Begin validate by confirming the committed build tip contains T-01 plus the QA/simplify trace artifacts, pin `feature.json.review_sha` to that exact tip, then run `gh-sync.py status <feature-dir> Review` and dispatch the validation review panel against the pin. This is the review-pin and panel-kickoff step after completed `plan.yaml#tasks/T-01`; no build task remains.

## Trust

- T-01 is `done` and its implementation commit carries the required marker — .harness/harness/features/FEAT-36-merge-gitignore-coverage/plan.yaml and git commit ac8533876d5539bfa5db50802b3a3c321add89a8 — verified-at ac8533876d5539bfa5db50802b3a3c321add89a8
- The blocking QA gate satisfied required unit and integration kinds with red-capability and unchanged-production evidence — .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/qa-validator/digest.md and notes/qa-T-01.md — verified-at ac8533876d5539bfa5db50802b3a3c321add89a8
- Four separate simplify readers were dispatched concurrently and all returned explicit empty findings; no apply occurred — .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/simplify-eng/state.yaml and digest.md — verified-at ac8533876d5539bfa5db50802b3a3c321add89a8
- Post-simplify unit and integration commands both exited 0 with named evidence and no MISCONFIGURED or KIND-DRIFT output — .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-simplify-final-suites.md — verified-at ac8533876d5539bfa5db50802b3a3c321add89a8
- GitHub sync recorded feature status Building exactly once after authoritative disk state; D-23 leaves T-01 open at Building until panel kickoff moves every card to Review — .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/github-sync-build.md — verified-at ac8533876d5539bfa5db50802b3a3c321add89a8
- No review pin exists yet — .harness/harness/features/FEAT-36-merge-gitignore-coverage/feature.json#review_sha — UNVERIFIED

## Dead ends

- Do not redispatch T-01; its completed engineering run was assessed rather than repeated — .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/t01-eng/digest.md — verified-at ac8533876d5539bfa5db50802b3a3c321add89a8
- Do not run `close-task`; D-23 requires the open task to move through Review and close with the parent at merge — .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/github-sync-build.md — verified-at ac8533876d5539bfa5db50802b3a3c321add89a8
- Do not apply an invented simplify change or weaken an assertion; every angle finding list was empty — .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/simplify-eng/digest.md — verified-at ac8533876d5539bfa5db50802b3a3c321add89a8
- Do not merge, create a PR, or enter ship during validate — .harness/harness/features/FEAT-36-merge-gitignore-coverage/BRIEF.md#constraints — verified-at ac8533876d5539bfa5db50802b3a3c321add89a8

## Working set

- .harness/harness/features/FEAT-36-merge-gitignore-coverage/plan.yaml
- .harness/harness/features/FEAT-36-merge-gitignore-coverage/STATE.md
- .harness/harness/features/FEAT-36-merge-gitignore-coverage/feature.json
- .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/qa-validator/digest.md
- .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/simplify-eng/digest.md
