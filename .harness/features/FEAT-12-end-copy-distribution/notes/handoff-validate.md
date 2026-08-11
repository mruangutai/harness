# Handoff — FEAT-12, validate → ship — written at fb80543, seq-3

<!-- Written at the seam by the orchestrator that ran validate and close-out. The feature is at
     its terminus: everything the factory can do is done, and what remains is the operator's. -->

## Next

Nothing to dispatch. Present `notes/ship-review-2026-08-10-ship.md` and get two rulings: the SC-06
UAT run, and the SC-05 disposition. On acceptance run `gh-sync.py ship <feature-dir>` and open the
unstruck backlog rows — but see the parent-issue trap under Dead ends first.

## Trust

- qa gate PASS, `matrix_ok: true`, unit 11 PASS and integration 12 PASS, 0 send-backs —
  `runs/qagate-validator/digest.md` — verified-at d543809
- Panel FAIL on ONE high, everything else advisory; its `must_fix` is SC-05's evidence gap —
  `runs/panel-validator/digest.md` — verified-at d543809
- Nine of eleven SCs met by their declared methods; SC-05 partial, SC-06 not_met —
  `runs/goalcheck-product/digest.md` `sc_status` — verified-at d543809
- kaya's `.harness/` IS tracked (117 files), the deletion commit touched nothing under it, and its
  one modified file has mtime 2026-08-07, three days before this feature — probed BY ME because the
  panel's blocking question was a measurement — verified-at fb80543
- The kaya manifests carry 377 identical paths and ZERO sha256 fields, so byte-identity was never
  captured and can never now be captured — read by me — verified-at fb80543
- 17 Expertise ops applied by their owners; `check-expertise.sh` OK on all 13 files; the three
  reviewer files took insertions only, checked per file — verified-at fb80543

## Dead ends

- Do not re-run the kaya manifest capture as SC-05's remedy — the before-state is gone, so it yields
  two after-captures; `runs/panel-validator/digest.md` — verified-at fb80543
- Do not rewrite commit `f3452bf`'s body to remove its unsupported "IDENTICAL, byte for byte"
  phrase — it is corrected in the ship review instead; rule 15 — verified-at fb80543
- Do not expect `gh-sync.py ship` to close #203 — `parent_origin: created`, so it closes #223 and
  leaves #203 open; `feature.yaml github:` — verified-at fb80543
- Do not run ship-refresh — there is no `.harness/codebase/` map in this repository, so nothing
  intersects; `ls .harness/codebase/` — verified-at fb80543
- Do not ask the orchestrator to apply another agent's Expertise ops — exit 2; the owner applies —
  verified-at fb80543

## Working set

- `.harness/features/FEAT-12-end-copy-distribution/notes/ship-review-2026-08-10-ship.md`
- `.harness/features/FEAT-12-end-copy-distribution/notes/uat-FEAT-12-sc06.md`
- `.harness/features/FEAT-12-end-copy-distribution/feature.yaml`
- `.harness/features/FEAT-12-end-copy-distribution/runs/goalcheck-product/digest.md`
- `.harness/features/FEAT-12-end-copy-distribution/runs/panel-validator/digest.md`
