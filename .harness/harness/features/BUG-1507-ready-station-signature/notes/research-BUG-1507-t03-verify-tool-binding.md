# T-03 verify — the tool name is now bound to the phrase

**Done.** T-03's `verify:` search term went from the bare phrase `set-feature-station --station
building` to the full `plan-merge.py set-feature-station --station building`, mirroring T-02's
repair verbatim in idiom. The placement half — two delimiter counts, whitespace collapse,
non-empty guard — is byte-unchanged. One field amended; nothing else in the file moved.

Written through `plan-merge.py amend --key tasks --id T-03 --field verify
--expect-sha256 763b2dce3d8e869b8595819562d4552d5fcbc46a9a4d32aacefae05e9bf1a138 --value-file`,
exit 0, `AMENDED tasks:T-03.verify`. Value stays a `|` literal block, no backticks, no markdown.

## The new verify (plan.yaml, T-03 `verify:`)

    python3 -c "import re,sys; t=open('.claude/skills/harness/SKILL.md',encoding='utf-8').read(); blk=t.split('## The build phase')[1].split('## Routing a lead')[0]; a='The eng segment.'; b='The qa segment'; ok=blk.count(a)==1 and blk.count(b)==1; seg=re.sub(r'\s+',' ',blk.split(a)[1].split(b)[0]) if ok else ''; print(ok, len(seg)); sys.exit(0 if ok and seg.strip() and 'plan-merge.py set-feature-station --station building' in seg else 1)"

Search term is a contiguous literal, which is safe only because the slice is already
whitespace-collapsed — SKILL.md wraps commands across lines routinely, and segment 4's existing
style (line 156) puts the whole invocation inside one backtick span, so a style-matching edit
keeps the literal intact.

## Observed exit statuses

Unfixed tree, verify read back off disk and run verbatim from the worktree root:
`exit 1`, stdout `True 424` (slice found and non-empty; term absent). Discrimination on throwaway
fixture copies of SKILL.md in temp trees (`/tmp/bug1507_t03_probe.py`, real file never written):

| case | new verify |
|---|---|
| segment 1, full `plan-merge.py set-feature-station --station building` sentence | exit 0 (`True 549`) |
| segment 1, same sentence wrapped between tool name and argument | exit 0 (`True 549`) |
| segment 1, BARE phrase without `plan-merge.py` | exit 1 (`True 535`) |
| segment 1, wrong tool `gh-sync.py set-feature-station --station building` | exit 1 (`True 546`) |
| segment 4, full sentence (placement half) | exit 1 (`True 424`) |

**Residual reproduced:** the OLD command on the bare-phrase fixture exits **0** (`True 535`) —
the fail-open PF-0274cfb40625bb45a968c559d773bcfd family, now closed. The line-wrapped case
exiting 0 is the collapse doing its job.

## Plan integrity after the amend

`yaml.safe_load` clean; `status: plan`; `approval.status: pending`; 5 tasks `T-01..T-05`,
6 decisions `D-01..D-06`, ids unchanged. `panel:` unchanged — canonical JSON sha256 of the whole
key is `f58711591695a3d477ec253b9fbe22f2c92ae5350fa438e722734519474d0b9f` before and after, and
all four recorded summaries re-hash to their recorded ids under `panel_findings.py id`
(PF-4d48a751…/T-05, PF-f0a35051…/T-02, PF-0274cfb4…/T-03, PF-41dcf8d7…/D-03, each still
`disposition: resolved` with its original `resolved_by`).

`check-plan-routes.py <plan.yaml>`: **0 violations across 1 plan**, exit 0, T-03 still
`OK main-session-direct (.claude/skills/harness/SKILL.md ungranted)`.

No commit, no PR, no production surface touched.

## Open

- None blocking. Advisory: T-03's `intent:` does not carry T-02's explicit "the backtick span must
  enclose the WHOLE invocation" warning. Segment 4's existing style already does that, so a
  style-matching edit passes; a doer who closes the span after `plan-merge.py` would redden a
  substantively correct edit. Out of scope for this amend (intent is not mine to touch here).
