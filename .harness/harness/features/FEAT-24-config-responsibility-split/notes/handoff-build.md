# Handoff — FEAT-24, build → validate — written at 6baa39b, seq-1

## Next

All ten tasks are `done` and committed; the build seam is crossed. Dispatch the **qa `test_matrix`
segment** to `harness-validator-lead` (the project's only blocking gate) against the diff
`ada8e99..b0604c3`, handing it the two coverage gaps named in Trust. Then the **four-angle simplify
pass** to `harness-eng-lead` over the code surface, **re-pin `review_sha` after any apply commit**,
then the review panel, then pm's goal-check on all 13 SCs through `harness-product-lead`.

## Trust

- All ten tasks `done` in `plan.yaml`, ten commits on the branch, every sub-issue closed and the
  parent derived to `Review` — `plan.yaml`, `gh-sync.py close-task` output — verified-at 6baa39b
- Full suite green: `run-unit-tests.sh --kind all` returns zero `FAIL` lines — verified-at 6baa39b
- I re-ran T-01, T-02, T-08, T-09 and T-10's `verify:` blocks myself on disk rather than taking
  them on report; all GREEN — verified-at 6baa39b
- **SC-06 is met and was checked LIVE, not from the suite:** `board_for` returns kaya's board with
  all five stations from `master`, with a checkout present on disk — which also proves the
  no-fallback rule — verified-at 6baa39b
- `gen-decisions-index.py --stdout | diff` against `DECISIONS-INDEX.md` is byte-identical; the index
  was regenerated, not hand-edited — verified-at 6baa39b
- **GAP for qa, real and unclosed:** nothing in the suite would redden if `factory_gh.py:456` flipped
  `validate=True` to `validate=False`. Discriminating fixture is `aGV!sbG8=` — validate=True raises,
  validate=False silently decodes to `b"hello"`. I confirmed both modes myself — verified-at 6baa39b
- **GAP for qa, systemic:** the fake `gh` recorder models argv but not the HTTP method or the real
  response shape, and shipped TWO defects past 208 passing checks — `-f` forcing a POST, and
  line-wrapped base64. `test-factory-gh.py:904` and `:910` still feed unwrapped synthetic base64.
  Whether a live smoke check is warranted is qa's call — verified-at 6baa39b
- `review_sha` is pinned at `b0604c3`, which CONTAINS the work under review. Re-pin after any
  further commit — `feature.json` — verified-at 6baa39b

## Dead ends

- Do not re-run T-01 through T-10; all are committed and independently verified — source: this session
- Do not trust a green suite as evidence an integration works — it was green through both live
  defects. Call the real thing — source: this session, two fix cycles
- Do not edit `check-state.sh`, `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py` —
  source: DEC-174 carve-out
- Do not stage with `git add -A`, `git add .` or `git add .harness`; explicit pathspecs only, and
  confirm `git status --short` before every commit — source: #433, and a live foreign reconciliation
- Do not touch or report on `FEAT-25-*`, `FEAT-26-*`, `FEAT-27-*`; their violation count is changing
  under a foreign pen and that is not a regression — source: this session's dispatch
- Do not re-raise D-10's `because` or D-06's reversibility cost — both applied pre-signature — source: plan.yaml:246, :290
- **Simplify hazard:** before applying any finding to a file a verify clause reads, check whether the
  clause greps words the edit changes — source: a pass did exactly that today, gates stayed green

## Working set

- `.harness/harness/features/FEAT-24-config-responsibility-split/STATE.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/plan.yaml`
- `.harness/harness/features/FEAT-24-config-responsibility-split/BRIEF.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/runs/2026-08-19-1-eng/digest.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/notes/ship-review-2026-08-18-ship-01.md`
