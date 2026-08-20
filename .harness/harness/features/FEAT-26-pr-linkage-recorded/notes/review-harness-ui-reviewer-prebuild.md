# UI review — FEAT-26 pr-linkage-recorded — pre-build (Mode A)

## Verdict: PASS, no DESIGN.md/prototype required — product lead's judgment holds

I read BRIEF.md, plan.yaml (all 8 tasks), and the product digest independently, and reached my own
conclusion before re-reading the product lead's stated reasoning in "The prototype gate" section.
They agree; this is not a relayed verdict.

## Census — the eight tasks, and which surfaces are text a human reads

| Task | Surface | Rendered/interactive? | In this review's remit? |
|---|---|---|---|
| T-01 | `feature-schema.json` `source_issues` property | No — schema, not rendered | No |
| T-02 | `gh-sync.py` internal mirroring (`load_recorded`/`save_recorded`) | No — file I/O, no output | No |
| T-03 | `_record_pr` diagnostic print-lines, `record-pr` subcommand | Yes — stdout lines a human reads at the terminal | Adjacent, lightly checked (not one of the two named surfaces) |
| T-04 | `cmd_closes` — `Closes #<n>` renderer | Yes — stdout text pasted verbatim into a PR body | **Yes, examined in full** |
| T-05 | INV-28 warn line in `check-state.sh` | Yes — stdout text read at session entry, prescribes an action | **Yes, examined in full** |
| T-06 | Backfill of 11 `feature.json` `pr` values | No — data write, no rendering | No |
| T-07 | `SKILL.md` table rows, `templates/plan.yaml` comment | Documentation for the next author, not runtime UI | No |
| T-08 | `DECISIONS.md` entry | Documentation | No |

No task in this plan produces HTML, CSS, a component, a layout, a colour, or anything with a
light/dark variant. Every text surface here is either internal (T-01, T-02, T-06) or plain CLI
stdout/stderr (T-03, T-04, T-05). That is the basis for the product lead's "no end-user interactive
surface" claim, and it holds under my own read, not just theirs.

## T-04 — `closes` renderer: tightly pinned, verifiable

`plan.yaml:365-377`. The intent pins: exact literal `Closes #<n>` with nothing else on the line, no
heading, no blank line, no trailing prose; one line per recorded ticket in **recorded** order (not
sorted — the in-order test case explicitly uses out-of-order numbers on disk, `plan.yaml:387-389`);
empty/absent list prints nothing and exits 0; zero `gh` calls, asserted against the fake gh's own
call log, not just against exit success (`plan.yaml:389-391`); diagnostics to stderr only.

This is functionally forced to be exact, not merely a style choice: `Closes #N` is a string GitHub's
own keyword parser matches literally when a human pastes it into a PR body. A near-miss (extra
whitespace, a heading, "closes" lowercase) would silently fail to close the ticket. The contract
recognizes this and pins accordingly. I found no gap here — a reviewer or test can tell conforming
from non-conforming output without asking the author. No finding.

## T-05 — INV-28 warn line: mostly pinned, two low-severity gaps

`plan.yaml:417-447`. Pinned: gated on `github.sync`; fires only on `status == "Done"` with `pr` not
an int; silent on `Abandoned` and every non-terminal status; one line **per** offending feature, not
an aggregate count (`plan.yaml:441-443`, correctly rejecting the failure mode this dispatch itself
warns about). The six required test-case names (`plan.yaml:454-459`) enforce all of that.

Two things are not pinned tightly enough to be verifiable as written:

1. **Remedy-command path substitution is ambiguous.** The intent says the warn line names "the
   remedy command: `gh-sync.py record-pr <feature-dir>`" (`plan.yaml:440`). Elsewhere in the same
   document `<feature-dir>` is consistently CLI-usage notation for a placeholder in a signature
   (`record-pr <feature-dir> [--pr N]`, `closes <feature-dir>` — `plan.yaml:313`, `363`), never
   literal text to print with angle brackets. Taken literally, an implementer could print the
   command with the bracket placeholder still in it — which the feature id named earlier in the
   same line does not resolve to a runnable command — or substitute the feature's actual directory
   (`.harness/harness/features/FEAT-01`) so the line is directly copy-pasteable, matching how T-06
   actually invokes `record-pr` (`plan.yaml:534`, `549-552`). None of the six named test cases
   ("names each offending feature on its own line") pins which reading is correct — a substring
   check for `gh-sync.py record-pr` and the feature id would pass under either. Given T-05's own
   framing — "a human reads at session entry and must then act on" — the unresolved-placeholder
   reading defeats the point of naming a remedy at all. **Low severity**: this affects operator
   convenience, not correctness, and INV-28 is warn-level bookkeeping (D-06) that gates nothing.
   Worth a one-line clarification in the task intent, not a blocking finding.

2. **The parse-failure branch is specified in prose but has no enforcing test.** The intent
   (`plan.yaml:430-433`) says a `feature.json` that does not parse appends "the same shape of
   message INV-21 uses, naming INV-28 as the check that could not run for that feature." None of
   the six required check names in `plan.yaml:454-459` exercises this branch — the task's `verify:`
   block would pass unchanged even if that branch were never written. I checked whether this is a
   new gap or an inherited one: `test-check-state.py` already carries a generic top-level "a
   `feature.json` that does not parse is a VIOLATION, never a silent skip" case (`test-check-state.py:184-199`)
   that is independent of any specific invariant, and INV-21's own suite (the block T-05 is modeled
   on) has no invariant-scoped parse-failure case either (`test-check-state.py:60-87`). So a
   malformed `feature.json` is already caught elsewhere regardless of what INV-28 does with it,
   which is why I rate this **low, not high** — but it is still a state this task's own prose
   describes and its own verify does not check, which is exactly the completeness gap Mode A exists
   to catch (my Expertise's P-08: a row with correct prose and no enforcing criterion is invisible
   to gates).

Neither gap changes SC-07/SC-09's checkability (those concern the Done+null / Done+int cases, both
of which are fully pinned and tested) and neither is a `must_fix`.

## Accessibility and light/dark theme parity — explicitly not applicable

Stated once, with the reason: every surface examined here is plain CLI stdout/stderr text — no
markup, no colour, no theme, no focus management, no hit targets, nothing an assistive technology or
a colour-vision check would apply to. State is conveyed by which line is printed or absent, never by
colour alone, because there is no colour. This section is not silently omitted; it is checked and
found inapplicable for a stated reason, per this review's own instruction.

## What I did not evaluate

T-03's diagnostic print-lines (branch-unset, zero-merged, two-merged, already-recorded messages)
were not one of the two named surfaces and I did not audit them to the same depth as T-04/T-05.
They are lower stakes than T-04 (not machine-parsed, not copy-pasted elsewhere) and lower stakes
than T-05 (not gated by any SC or invariant) — none of the plan's success criteria depend on their
exact wording, only on the write/no-write behavior they accompany. If a future reviewer wants
message-contract rigor there, that is a legitimate but separate ask.

## Recommendation to the product lead / pm

No `DESIGN.md` and no prototype are correctly not required for this feature — I concur, on the
strength of the census above, not on the strength of the digest's own framing. If pm wants to close
the two low-severity gaps before signature, the fix is two sentences in T-05's intent (state whether
`<feature-dir>` in the remedy line is substituted, and add a seventh named test case for the
non-parsing branch) — neither is a blocking rewrite.
