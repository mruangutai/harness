# UI/design-contract review — FEAT-38 amendment (Mode A, pre-build)

## Verdict

**FAIL.** One in-scope design contract (repairing `DECISIONS.md`'s DEC-205 entry so it stops
lying about how many mechanical checks exist) is unsound: the task that implements it (T-28) does
not repair the companion reader-facing summary in `DECISIONS-INDEX.md`, and — per the generator's
own documented behavior — regenerating the index cannot fix that summary either. Followed exactly
as written, T-28 lands leaving `DECISIONS-INDEX.md` asserting the exact falsehood this feature
exists to eliminate.

## Surfaces examined (file:line)

- `BRIEF.md:1-14` — amendment banner
- `BRIEF.md:16-27` — Problem
- `BRIEF.md:29-42` — Goal, including the "One mechanical check ... There is deliberately no second
  check" paragraph
- `BRIEF.md:88-116` — "The executable-claims mechanism is DELETED, not redesigned" subsection
  (including the DEC-205 callout and the removal-cost subsection)
- `BRIEF.md:150-158` — REQ-08 tombstone
- `BRIEF.md:159-163` — REQ-09, REQ-10
- `BRIEF.md:230-245` — SC-09 tombstone
- `BRIEF.md:283-311` — SC-14 .. SC-18
- `BRIEF.md:355-358` — `## Approval` (read-only, not evaluated as a contract, not touched)
- `plan.yaml:1733-1783` — T-24 (deregister runner side)
- `plan.yaml:1786-1832` — T-25 (deregister config side)
- `plan.yaml:1833-1895` — T-26 (delete checker + test)
- `plan.yaml:1896-1945` — T-27 (delete 11 claim markers)
- `plan.yaml:1946-2008` — T-28 (repair DEC-205 prose, regenerate index)
- `plan.yaml:2009-2091` — T-29 (bin/ argv-class audit note)
- `plan.yaml:945-990` — T-11 ("Rewrite the index rulings freed by am-span removal and regenerate
  the index") — read as precedent for how this same plan handles a decision-body edit that makes
  an existing `DECISIONS-INDEX.md` ruling stale
- `.harness/harness/docs/DECISIONS.md:6240-6299` — full DEC-205 entry, verified as the file's last
  entry (no `## DEC-206`) and verified (via full-file grep for `two mechanical|mechanical check|
  executable claim|claim marker|check-decision-claims`) that no other entry references this
  mechanism
- `.harness/harness/docs/DECISIONS-INDEX.md:205` — the generated index row for DEC-205
- `.claude/skills/harness/bin/gen-decisions-index.py:1-15,81,171-217` — module docstring and
  `build_index`, to confirm how a row's ruling text (right of ` :: `) is produced on regeneration

## Findings

### F1 — HIGH, must-fix. T-28 will leave `DECISIONS-INDEX.md`'s DEC-205 row false, and its own verify cannot catch this.

`DECISIONS-INDEX.md:205` currently reads:

> `- DEC-205 @6240 [state,cost,skills,dispatch] refs: DEC-145 DEC-188 DEC-191 :: This file states
> current truth: no amendments, supersession is deletion, deleted numbers are never reused, and
> two mechanical checks — anchor rot and executable `claim:` markers — guard it.`

`gen-decisions-index.py:12-14,81,171-217` documents and implements that everything **right** of
` :: ` on a row — the "ruling" — is hand-written and is **preserved verbatim** across
regeneration (`ruling = prose`, sourced from `existing_rows[key]`, `gen-decisions-index.py:213`).
Regeneration never re-derives the ruling from the entry body. `plan.yaml:966-989` (T-11) is this
same plan's own precedent for the resulting workflow: when a decision body edit makes its existing
`DECISIONS-INDEX.md` ruling stale, the task explicitly says "hand-rewrite the rulings that need
it" — regeneration alone is called out there as insufficient.

`plan.yaml:1946-2008` (T-28) deletes DEC-205's rule 2 and rewrites the heading and two prose
sentences to say "one mechanical check," then only runs
`gen-decisions-index.py --stdout | diff -q - DECISIONS-INDEX.md`. It never touches the DEC-205
row's hand-written ruling. Because that text is preserved verbatim, the diff will pass while the
row still names "two mechanical checks" and "executable `claim:` markers" — a mechanism that, by
the time T-28 finishes, no longer exists anywhere in the tree. `DECISIONS-INDEX.md` is the compact
surface `BRIEF.md:16-27` (Problem) says a reader consults to avoid the layering cost the whole
feature exists to remove; landing T-28 as specified reintroduces exactly that failure mode — a
document stating what was true, not what is true — inside the artifact this feature is about.
SC-16 (`BRIEF.md:296-303`) doesn't save this either: its inspection scope is written as "DEC-205's
heading and the sentence introducing its enumeration," not the index.

**Recommendation for pm:** add an explicit step to T-28's intent, matching T-11's shape — hand
-rewrite the DEC-205 row's ruling in `DECISIONS-INDEX.md` to state one check (e.g. "...and one
mechanical check — anchor rot — guards it."), before the `diff -q` regeneration check — and add a
positive assertion to T-28's verify that the row no longer contains `claim` or `two mechanical`
(e.g. `grep -qE '^- DEC-205 ' "$I" | grep -qi 'claim\|two mechanical' && exit 1`, alongside the
existing diff-clean check). Word budget is not a blocker: the current ruling is ~26 words against
the 30-word cap noted at `plan.yaml:598,647-649`; a shortened one-check version fits.

### F2 — MED, non-blocking. T-28's verify under-checks the third false sentence it is also asked to repair.

`DECISIONS.md:6240` (heading) and `:6272` (enumeration-intro sentence) both currently assert "two
... checks," and T-28's verify (`plan.yaml:1962-1969`) positively asserts their exact replacement
text (`grep -qE '^## DEC-205 .*one mechanical check'`, absence of a stray `^2\. ` item). But
`DECISIONS.md:6297-6299` (closing paragraph) contains a *third* now-false sentence — "...that
openness is exactly why **the two that are in** are the mechanical ones" — which T-28's own intent
(`plan.yaml:1996-2000`, item 4) correctly identifies and asks the implementer to repair. The verify
only checks the stale phrase is *absent* (`grep -qiE '...the two that are in'`); it never
positively confirms the new sentence states the count correctly. SC-16 (`BRIEF.md:296-303`) also
never names this sentence — its prose covers only "the heading and the sentence introducing its
enumeration." An implementer could satisfy both the automated verify and a literal reading of SC-16
by deleting the count language from the closing sentence entirely rather than correctly restating
it, and nothing would catch that. This does not block signature on its own (the negative check
does prevent the worst case — leaving the old false count verbatim — and SC-13's operator
read-back is a backstop), but pm should tighten SC-16's wording and T-28's verify to name and
positively check this third sentence the same way the other two are checked.

## Not reported as findings (per dispatch's exclusions / settled ground)

- Loss of semantic citation-rot detection — accepted operator cost, not re-litigated.
- The declarative `contains`/`max_lines` redesign — rejected, not proposed here.
- `check-decision-anchors.py` — retained unchanged, out of the risk class, untouched by this review.
- BRIEF.md's REQ-08/SC-09 in-place tombstones — read in full (`BRIEF.md:150-158,230-245`); both are
  contiguous-numbered, bold-flagged "RETIRED," state why kept, and state what a live violation would
  look like ("a task still tracing to it is a plan defect"). Confirmed by grep that no `plan.yaml`
  task's `traces:` array cites REQ-08 or SC-09. This does not damage the operator's ability to read
  and sign the brief; no finding.

## Scope note

No `DESIGN.md` exists for this feature and none is warranted: the change is documentation and
tooling text, not a rendered UI. The two candidate surfaces the dispatch asked me to weigh —
`DECISIONS.md`'s DEC-205 prose repair and `BRIEF.md`'s own readability — were both examined
directly rather than declined by default. The first carries a real, checkable design contract
(what the heading/enumeration/closing-paragraph must say, and how many checks exist) that is
incomplete in the way F1 and F2 describe; the second holds up under inspection.
