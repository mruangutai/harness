# STATE

## Current

- feature: BUG-285-yaml-loader-pin
- run: .harness/harness/features/BUG-285-yaml-loader-pin/runs/2026-09-11-03-panelrecordc2-product/state.yaml
- squad: none
- status: awaiting-user

Rescoped on the operator's 2026-09-11 decision and re-panelled. The plan now carries three tasks:
T-01 (unchanged, the gh-sync.py regression pin), T-02 (the actual fix — factory_decompose.py:121's
YAML loader replaced by a JSON read) and T-03 (a unit fixture over the new reader). The panel ran
twice more: cycle 1 FAILED on a high finding both readers found independently, that finding is
fixed and verified closed at source, and cycle 2 PASSES with severity_max low. Nothing builds until
the approval state below is resolved.

## Open Questions

- BLOCKING — the approval state is inconsistent and no tool can fix it. plan.yaml reads
  `approval.status: approved` (mruangutai, 2026-09-09, commit bb488145) over a task set amended
  five times since that signature; BRIEF.md reads `pending`. `sign-approval` hardcodes `approved`,
  `amend` rejects `--key approval`, `apply` carries the base's approval bytes verbatim, and
  Edit/Write/redirect are denied. There is no approved -> pending route for anyone. The operator
  must either re-sign the amended plan knowingly or supply a reset route.
- BLOCKING — the operator has not signed the AMENDED scope. The 2026-09-09 signature covers a
  one-task plan that no longer exists.
- Non-blocking, four panel findings open: PF-2242299b369215b13ad577fe4279d52e (info),
  PF-cceab610738066... (info), PF-142f3a51c0d0152899db48cf7cbdfe31 (low),
  PF-a5b9a3c81ee99295515d75f5a776ebae (low). Recording acceptance of any of them needs
  `sign-approval --overrule PF-<id>:<reason>`.
- Non-blocking, out of scope: gh-sync.py:516-517 reads with encoding=utf-8 but catches only OSError,
  so a non-UTF-8 feature.json escapes load_recorded uncaught, and the
  `except (ValueError, UnicodeDecodeError)` at :524 guards a value that is already a str. Same
  defect class the panel gated on, in the reader T-01 exists to pin. Separate bug, or folded in?
