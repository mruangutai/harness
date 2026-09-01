# Handoff — FEAT-51-claude-code-lifecycle-safety, plan → operator signature — written at 0bc57c88, seq-10

## Next

Nothing is dispatchable and no fix is pending. The plan is panel-clean: 13 findings, every high
`resolved`, no critical or unrated. The remaining act is the operator's, and it is three things in
`notes/ship-review-plan-signature-c9.md`: sign (accepting the REQ-04 narrowing), repair
`cmd_sign_approval` so `plan.yaml` can hold a signature at all, and rule on the T-07 title residue.
When the signature lands, the build starts at segment 1 (T-01 and T-02, both `depends_on: []`, both
main-session-direct) — the seven segments are §6 of the briefing. Raise `max_total_cycles` in the
same act as the signature: 9 of 10 are spent and the budget is per feature, not per phase.

## Trust

- The plan is 9 tasks / 17 decisions / 12 SCs, `status: plan`, no `approval:` key — parsed with `yaml.safe_load` myself — verified-at 0bc57c88
- `check-plan-routes.py` exits 0, zero violations across 4 plans; the four DEVIATION lines on T-01, T-02, T-07 and T-10 are the DEC-174 carve-out — ran it myself in the worktree — verified-at 0bc57c88
- Every high panel finding is `resolved` and none is critical or unrated — asserted programmatically over the parsed `panel.findings` — verified-at 0bc57c88
- F-A is real: `agent_type: harness-pm`, no live claim, `cp /tmp/evil.md <feature>/BRIEF.md` exits 0 at `bash-write-guard.sh`, `plan-sign-gate.sh` AND `check-domain.sh` — I fired all three payloads myself — verified-at 0bc57c88
- `plan.yaml` cannot acquire an `approval:` mapping by any route, and the editor route is denied for the MAIN SESSION too — four probes including a no-`agent_type` `Write` payload I fired myself — verified-at 0bc57c88
- T-02's amended `verify:` exits 1 against the current tree, so it discriminates — I ran the whole block verbatim — verified-at 0bc57c88
- 19 of the plan's 21 target files are byte-identical between `ad93d43e` and `0bc57c88`; the two that moved are T-01's — `git diff --numstat` over the file list — verified-at 0bc57c88
- T-01's re-measured anchors are correct, 26 of 26 — the validator's reader checked each; I re-derived only the ten in `validate-digest.py` — partially UNVERIFIED
- T-06's `intent:` bullet list no longer contradicts D-15, and F-B/F-C/F-F are closed at source — the independence pass reports this; I checked none of the three myself — UNVERIFIED

## Dead ends

- Do not try to give `plan.yaml` an `approval:` block through `plan-merge.py`. All four routes are closed and the fifth (a `cp` of the template, which the Bash route does not deny before the fact) is the doctrine's own prohibition — four probes — verified-at 0bc57c88
- Do not amend `lanes` or `panel` with an incremental `apply`; it exits 7 and refuses the whole write. Remove-then-single-shot-apply with absolute paths, then byte-diff — `plan-merge.py:98` — verified-at 0bc57c88
- Do not spend cycle 10 on T-07's title. It is med, no `verify:` greps it, all five recording surfaces are qualified, and the build phase shares this budget — briefing §3 — verified-at 0bc57c88
- Do not re-litigate the discard cut, T-10/SC-13, the `DEC-210` renumber, or F-A's disposition. All four are ruled and the panel was told so explicitly — this phase's dispatch record — verified-at 0bc57c88
- Do not dispatch a squad for T-01, T-02, T-03, T-05, T-07 or T-10. DEC-174 holds them main-session-direct and `check-plan-routes.py` records four of them as declared deviations — verified-at 0bc57c88
- Do not use a relative path in any `rm`/`cp` under `bash-write-guard.sh`; it resolves against the MAIN checkout and refuses with a message that reads like a domain error — measured twice in earlier cycles — UNVERIFIED here

## Working set

- `.harness/harness/features/FEAT-51-claude-code-lifecycle-safety/notes/ship-review-plan-signature-c9.md`
- `.harness/harness/features/FEAT-51-claude-code-lifecycle-safety/plan.yaml`
- `.harness/harness/features/FEAT-51-claude-code-lifecycle-safety/BRIEF.md`
- `.harness/harness/features/FEAT-51-claude-code-lifecycle-safety/STATE.md`
- `.harness/harness/features/FEAT-51-claude-code-lifecycle-safety/runs/plan-panelverify-c9-validator/digest.md`
