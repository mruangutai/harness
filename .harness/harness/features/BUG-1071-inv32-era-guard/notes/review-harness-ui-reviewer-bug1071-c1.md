# UI Review — cycle 1 — BUG-1071 inv32-era-guard (operator-string remit)

Reviewed at pinned `review_sha` **6b65ecc** (worktree HEAD `093574a`, which only adds a
re-pin commit after 6b65ecc — no file content differs at 6b65ecc vs HEAD for the paths in
remit). Base `75daa3bb`. Superseding cycle 0's PASS at `bf12a96b` per dispatch — this is a
fresh judgment of the F1/F2 remedies, not a rubber stamp of the earlier one.

## Remit

Dispatch explicitly hands this non-UI diff's four INV-32 operator-facing strings to this
role (repo-tier Expertise P-01 / project-tier P-06: adjacent CLI/gate-emitted text is this
role's reduced scope on a no-rendered-UI diff in this repo). Reviewed **only** those four
strings and the stream they print in. Did not re-judge era logic, boundary correctness, or
the four new test cases — other reviewers' ground, per cycle 0's own confinement.

## The four strings (verified against `check-state.sh` diff 75daa3bb→6b65ecc)

1. **Key-absent VIOLATION** (~L216): *"INV-32: .harness/harness.json has no
   `panel_era_start`, so no panel era can be resolved. Run /harness-init --upgrade
   (upgrade-config.py) to merge the key in, then set it to the date the adversarial panel
   became available here, or null if this project never predated it."* — names the
   defect, the file, and a two-step remedy (command + what value to set). Fully
   actionable. No finding.

2. **Malformed-`panel_era_start` VIOLATION** (~L228): *"INV-32: .harness/harness.json
   `panel_era_start` is {value!r}, which is neither null nor a YYYY-MM-DD date. Nothing is
   exempted while it is unreadable."* — names the field, the file, the current (bad) value,
   and the two valid shapes. No explicit imperative verb ("set it to…") the way its sibling
   above has, but the constraint stated is sufficient for an operator to act. **Info,
   non-gating**: a symmetry nit against its sibling message, not a defect — nothing is
   missing that blocks action.

3. **Missing/malformed `approval.date` VIOLATION** (~L266) — this is F1's remedy, and the
   one cycle 0 rated LOW for naming the defect but not the remedy. New text: *"INV-32:
   {feat} is approved but approval.date is missing or malformed ({signed!r}), so its panel
   era cannot be placed. Add the signature date; recover it with git log -S'status:
   approved' -- <this plan.yaml>."* **Finding below — MED, non-gating.**

4. **Pre-era note** (~L272): unchanged in shape from cycle 0's no-finding, now also names
   the config source (`harness.json panel_era_start`) in the parenthetical. Still requires
   no operator action and states its own exemption reasoning. No finding.

## Finding — MED, non-gating: the approval.date recovery command is not the path it names

**Scenario, concrete and reproduced:** the message is formatted as a runnable shell
command, so the natural operator action is to copy the line after "recover it with" and
paste it into a terminal. Done literally, the command is:

    git log -S'status: approved' -- <this plan.yaml>

`<this plan.yaml>` is a literal, unsubstituted placeholder, not the discovered path. I
confirmed this two ways:

- **Copy-pasted literally**, this tool's own write-guard classified the string as a file
  redirect/write attempt and refused to run it — direct evidence that a real shell parses
  `<this` as stdin redirection from a file named `this` and hits `>` after `plan.yaml` as
  an (here, dangling) output-redirect token, not as prose. It does not do what the message
  promises; at best it is a confusing syntax error, not the git history the operator asked
  for.
- **Substituted with the real path** (`.harness/harness/features/FEAT-40-harness-writes-done/plan.yaml`,
  the one plan this exact message class was written for), the command works exactly as
  claimed:

      $ git log -S'status: approved' --oneline -- .harness/harness/features/FEAT-40-harness-writes-done/plan.yaml
      f11b41a [harness:BUG-1071] Close panel finding F1: an undated approval now fails (#1071)
      2938a5c FEAT-40 the operator signs, and bounds execution at T-03 (#842)

  `2938a5c`, `2026-08-25` is exactly the recovered signature the backfill commit
  (`f11b41a`) cites. The command's *idea* is sound and does surface the signing commit —
  it is only unusable as literally printed. (Note in passing: it returns two commits here
  because BUG-1071's own backfill comment happens to quote the phrase "status: approved" —
  an artifact of this specific case, not a defect in the command's general shape; a future
  undated approval elsewhere would very likely return exactly one hit.)

**Why this rates above cycle 0's F1 (LOW → this, MED):** the file has a documented,
consistently-followed convention for exactly this situation. Its own comment at
`check-state.sh:78-81` (D-08, FEAT-21 T-05) states the rule directly: *"a finding that
names a PATH carries the DISCOVERED segment-qualified path, so a reader can open exactly
what the label names."* Every other path-naming message in this file honours that via
`fpath(feat, '<file>')` (10+ call sites grepped, e.g. `fpath(feat, 'plan.yaml')` at L107,
L161). This is the only operator-facing message in the file using an angle-bracket
placeholder instead of the resolved path — `fpath(feat, 'plan.yaml')` was sitting right
there, already imported, already used for this exact filename elsewhere in this same
function. The remedy F1 asked for (name the fix, not just the fact) is now present in
spirit but not in a form that survives contact with a terminal.

**Why non-gating:** it does not misdirect the operator to a false remedy, does not cost
data (the guard's own reaction shows the likely failure mode is a syntax error, not a
write), and the feature name is stated one clause earlier in the same message so a reader
familiar with this repo's layout can reconstruct the real path without much friction. It
also only fires on a currently-empty condition — the one undated approval in this tree was
already fixed pre-emptively as part of this same change, per the plan's stated ordering
("fix the data first, then close the hole"). This is a clarity gap on a now-dormant path,
not a live functional defect, matching the shape (not the target) of cycle 0's F1.

## Scannability (cycle 0's volume note — reconfirmed live)

Ran `check-state.sh` at HEAD: **32 `INV-32:` lines, 0 `VIOLATION` among them, 0 `bad`
lines anywhere in output, exit 0.** All 32 are the pre-era note (FEAT-40 included, now
correctly graded pre-era at its recovered 2026-08-25 signature rather than triggering the
undated-approval branch) — independently confirms the author's claimed "32 INV-32 notes,
0 violations." Order is still per-feature iteration order, not grouped or sorted; this
diff did not introduce that and fixing it here would be scope creep onto a file-wide
presentation pattern shared by INV-22/INV-23, consistent with cycle 0's ruling. No new
finding.

## Verdict rationale

No `must_fix`. The one new finding (MED) is a real, reproduced actionability gap — but it
sits below cycle 0's own bar for gating (F1 at LOW did not gate; this finding closes F1's
substantive ask while opening a narrower, lower-stakes one). `severity_max: med` → PASS.

## Open question

None blocking. Whether to swap `<this plan.yaml>` for `{fpath(feat, 'plan.yaml')}` is a
one-line, reversible fix that brings the message into line with the file's own stated
convention — noted as a take-it-or-leave-it improvement for whoever next touches this
block, same disposition as cycle 0's F1 wording note.
