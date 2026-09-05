# Receipt — harness-documentor — distill c1

**One entry applied, repository tier; three relayed candidates rejected as already covered; one
craft candidate judged worth a displacement but UNAPPLIABLE — `expertise-merge.py` is union-only and
has no mechanism to displace at a full section.** Both my files pass `check-expertise.sh` at exit 0.

## Relayed candidates

1. **Pre-edit `grep -c` returned 0 so the verify clause was non-vacuous — REJECTED.** Covered twice
   over: craft G-03 mandates running the handed verify block before the first edit and re-deriving
   the baseline; craft P-11 mandates proving a section-body assertion was not already green. A third
   entry restating the same discipline for the `grep -c` special case is an instance, not a rule.
2. **Generated index's hand-written tail survives while the generated side recomputes — REJECTED as
   a new entry.** Repository P-03 already states it almost verbatim ("expect the regenerated index
   row's tags, refs and `@line` anchor to recompute, and report that as your edit's effect"), and
   craft O-02 carries the general form. What P-03 does **not** state is *where* the preserved region
   begins — see the accepted entry below, which is the residue, not a restatement.
3. **First pass landed in the MAIN checkout, not the worktree — REJECTED.** Craft G-18 as written
   ("make every edit target an absolute path and diff both trees … a content-derived snapshot tag
   still matches when the two copies are byte-identical") would have prevented this exactly; my own
   observations log records it as "G-18 confirmed again". Re-adding it is a story about a rule I
   already hold and ignored.

## Self-derived

4. **ACCEPTED, repository tier.** Verified against `.claude/skills/harness/bin/gen-decisions-index.py`
   (module docstring `:13`, `ROW_RE` `:81`, malformed-row branch `:283-293`), not from memory:
   `- P-05: WHEN hand-editing a row in .harness/harness/docs/DECISIONS-INDEX.md DO change only the
   text right of " :: ", keeping one space each side — that tail is the sole region preserved
   verbatim across regeneration, and a malformed separator makes the generator refuse the whole
   write.`
   One-question test — *true and useful in a repository I have never seen?* **No.** It turns on one
   repo's file, one generator and one row grammar. Repository tier.
5. **JUDGED ACCEPTED, NOT APPLIED — craft.** From the T-05 receipt's "patterns and extensions NOT
   re-listed" discipline: *WHEN documenting behaviour driven by a list in code — globs, extensions,
   status values — DO name the constant and state the consequence per group, never transcribe its
   members; a transcribed list rots silently while the named constant stays true.* One-question
   answer: **yes**, craft. Displacement named: **P-06** (task intent mandates a token its own verify
   clause forbids) — weakest live Pattern, near-duplicate of P-05's prose-vs-verify-clause shape,
   and describes a self-contradicting task that would be raised as an open question anyway.
   **Blocked by tooling, not by judgement** — see Q1.

## Why the displacement could not be applied

`expertise-merge.py apply` computes a UNION only (`compute_union` `:113-139`). Reusing id `P-06` with
new text is exit 7 CONFLICT and writes nothing; a fresh id makes Patterns 16 > cap 15, exit 8. The
only paths that would land it — a whole-file Write or an Edit — are prohibited for Expertise files
(DEC-125). So a full craft section is currently **append-impossible by any sanctioned route**, which
makes "displace a weaker entry" unexecutable doctrine rather than a choice I declined.

## Applied

- `.harness/harness/expertise/harness-documentor.md` — `ADDED P-05`, 11 ids PRESERVED, exit 0. File
  16 → 17 lines of a 40-line budget. Patterns 4 → 5; Gotchas 7 → 7; Outcomes 0 → 0; Open 0 → 0.
- `.harness/expertise/harness-documentor.md` — untouched. Patterns 15/15, Gotchas 15/15,
  Outcomes 10/10, Open 0/5, before and after.
- `check-expertise.sh`: `OK` exit **0** on each of my two files. Nothing staged, nothing committed,
  no worktree removed, no suite run.
