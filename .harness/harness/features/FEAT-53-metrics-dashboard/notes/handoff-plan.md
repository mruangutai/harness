# Handoff — FEAT-53, plan → plan (pass 4) — written at ba5b4a50+, seq-3

## Next

Wait for the operator's pass-3 ruling on `notes/ship-review-2026-09-02-plan-c3.md`, which arrives as
`notes/answers-<runid>.md`. If they rule FIX on `V-1` (and on any of `B-15`..`B-18` they do not
strike), dispatch ONE consolidated `harness-product-lead` → `harness-pm` pass, then re-run the
`plan-panel` team at cycle 4, then have pm transcribe the panel into `plan.yaml`'s `panel` key. Every
one of the five is a sentence or a clause in an already-drafted task or decision — `V-1` in `D-22`'s
`choice` or `T-19`, `B-15` in `T-06`+`T-11`, `B-16` in `T-06`, `B-17` in `T-11`, `B-18` in `D-21`. If
they overrule `V-1`, the plan goes straight back for signature; only the main session signs.

## Trust

- All three pass-2 rulings are applied and the plan is otherwise sound — `runs/2026-09-02-1-product/digest.md`, and I re-read T-16's `depends_on`, D-14, D-19, D-21 and D-22 on disk — verified-at ba5b4a50
- `V-1` is real: `cmd_ship`'s only commit is `_commit_terminal_station`, which commits `plan.yaml` alone ("ONLY THIS ONE FILE … implies `--only`") — `.agents/skills/harness/bin/gh-sync.py:659-661` — verified-at ba5b4a50 by me, not adopted from the reader
- `plan.yaml`'s `panel` key holds 18 findings, cycle 3, both readers `ran` — `load_plan` over the file, every diff hunk inside `panel:` — verified-at ba5b4a50
- BRIEF `## Approval` `date:` is populated in 43 of 47 BRIEFs in the main checkout; the main session has confirmed it will fill it at signature — measured 2026-09-02, and the IRC confirmation is in this session's transcript — verified-at ba5b4a50
- `cycles_used` is 7 of a hard 10; a fix pass plus its panel re-read makes 8 — `feature.json` — verified-at ba5b4a50

## Dead ends

- DEC-5 / the visual prototype: CLOSED by the operator after two browser reviews including post-fix — `notes/answers-2026-09-01-plan-signature-c2.md` — do not reopen
- `B-6` (cycle-time origin): struck as redundant, Q2 resolved it — same answers file
- `B-12`/`B-13`/`B-14` and the ~250 stale spliced `#` comments: accepted backlog, not fixable by any sanctioned verb today — same answers file
- Widening `D-22` beyond the two files the operator named: that narrowing was MY dispatch instruction and it is what produced `V-1` — `notes/ship-review-2026-09-02-plan-c3.md` §1 — do not repeat it
- `plan-merge.py apply` for anything but a genuinely new block, and never with comment lines in the proposal: it splices them permanently — `notes/ship-review-2026-09-01-plan-c2.md` defect 1

## Working set

- `.harness/harness/features/FEAT-53-metrics-dashboard/notes/ship-review-2026-09-02-plan-c3.md`
- `.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml`
- `.harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-02-02-validator/digest.md`
- `.harness/harness/features/FEAT-53-metrics-dashboard/notes/answers-2026-09-01-plan-signature-c2.md`
- `.harness/harness/features/FEAT-53-metrics-dashboard/feature.json`
