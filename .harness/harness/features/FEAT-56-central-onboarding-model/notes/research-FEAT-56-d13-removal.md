# D-13 closed by the operator's ruling — three tasks, one new criterion

**BLUF.** The removal is planned as **three tasks split by lane, not by file count**: T-18 (`team`,
`harness-dev-ops`) for the live config, T-19 (`main-session-direct`) for the four NOBODY sites,
T-20 (`team`, `harness-documentor`) for the DEC-83/BUILD.md amendment. D-13 is amended from an open
question into the operator's settled ruling. `approval:` stays `pending`. Every new `verify:` was
run verbatim out of `plan.yaml` and observed **RED** at `97fe447f`.

## Lane resolution — measured, `check-domain.sh --resolve`, all exit 0

| path | resolve | task | mode |
|---|---|---|---|
| `.harness/harness.json` | `harness-dev-ops` | T-18 | `team` |
| `.harness/team-config.yaml` | `NOBODY` | T-19 | `main-session-direct` |
| `.claude/skills/harness/templates/harness.json` | `NOBODY` | T-19 | `main-session-direct` |
| `.claude/skills/harness/templates/team-config.yaml` | `NOBODY` | T-19 | `main-session-direct` |
| `.claude/skills/harness/templates/examples/harness.kaya-ai.json` | `NOBODY` | T-19 | `main-session-direct` |
| `.harness/harness/docs/DECISIONS.md` | `harness-documentor` | T-20 | `team` |
| `.harness/harness/docs/DECISIONS-INDEX.md` | `harness-documentor` | T-20 | `team` |
| `.harness/harness/docs/BUILD.md` | `harness-documentor` | T-20 | `team` |

`check-plan-routes.py` on this plan: `0 violation(s)`, exit 0; T-18 `granted to harness-dev-ops`,
T-19 the expected DEC-174 deviation-free `declared main-session-direct`, T-20 `granted to
harness-documentor`. Path spelling is `.claude/skills/...`, matching T-05/T-12 (`.agents` is a
symlink; `git show` of an `.agents` path prints nothing).

## D-13, in one sentence

The operator ruled on 2026-09-09 that `cli_min_version` is removed from all five config sites
(`.harness/harness.json:3`, `.harness/team-config.yaml:11`, `templates/harness.json:4`,
`templates/team-config.yaml:22`, `templates/examples/harness.kaya-ai.json:4`) and DEC-83 amended to
match, because D-12 severed the key from its only enforcement point and nothing reads it — no
reader, no schema entry, no reference under `.claude/skills/harness/bin/`; pm's contrary
recommendation to keep the key is recorded as **overridden**, not as the entry's conclusion.

## The amendment shape — I did NOT invent one, and the house form is not an "amendment note"

`DECISIONS.md:3-6` and **DEC-205** (`DECISIONS.md:6326-6335`) END the amendment convention: an entry
states current truth in its own voice, a correction **rewrites the sentence it corrects**, undated
and unattributed. The `**Amended by FEAT-41**` paragraph at `DECISIONS.md:5327` predates DEC-205 and
is not the form to copy. T-20's `intent` therefore says: rewrite `DECISIONS.md:977` and
`BUILD.md:96` in place, drop the key item from `BUILD.md:426`, write no new `DEC-NN`, and leave
`DECISIONS.md:957-969`, `BUILD.md:33/:78/:85-86/:88-94` and `BUILD.md:517/:521-522` untouched.
This is a deviation from the dispatch's wording ("an amendment note inside DEC-83") forced by the
file's own governing decision.

## The criterion — ADDED, plus one requirement

**Added SC-16** (`BRIEF.md:275-292`), not covered by anything existing: SC-14 asserts the absence of
the token `2.1.217` only inside `harness-init/SKILL.md`; no criterion touches config. SC-16 checks
**per file, two ways per file** — `git show <review_sha>:<path>` parsed with `json.load` /
`yaml.safe_load` and the loaded mapping asserted keyless, plus the token and (for the two YAMLs) the
trailing comment — because a single global grep is satisfied by four sites and blind to the fifth
(the SC-03/SC-14 failure mode). RED at `97fe447f`: five `KEY-PRESENT`, `BUILD.md` token count 1
(must be 0), `DECISIONS.md` count 0 (must be ≥1). Added **REQ-11** (`BRIEF.md:77-80`) as its source,
since no existing REQ covers a dead config key and a task must trace something real. SC-16 is also
added to the "names an exact command, not a file the runner discovers" gap bullet (`BRIEF.md:310`).

## Verify design — parse, not grep, and per file

Each config task loads its OWN files and asserts the key absent from the loaded mapping; the greps
are the second net (a key surviving inside a string), and the two YAML sites additionally assert the
trailing comment `# floor for the spawn env vars (DEC-83)` is gone with its line. T-18 also asserts
`check-state.sh` **still runs** (`| grep -c 'INV-'` > 0, 17s measured) rather than exits 0 — HEAD
already carries pre-existing VIOLATION lines (unapproved BRIEF, stale `review_sha`), so exit 0 is
unachievable and would be a verify nobody can pass. T-20's `2.1.172`/`2.1.219` greps are labelled in
its `intent` as **preservation guards, already green and non-discriminating**; its two discriminating
conjuncts are BUILD.md absence and DECISIONS.md presence of the token.

## Open questions

- Q1 (non-blocking): `BUILD.md:517` "Requires CLI ≥ 2.1.217" is a record of a verified doc fact, so
  T-20 keeps it and is told to repoint its framing only if it reads as an instruction to pin. A
  reviewer may prefer it rewritten; left to the doer with a receipt note rather than pinned here.
- Q2 (non-blocking): after this lands nothing machine-readable declares the compatibility floor, so
  a run under CLI < 2.1.217 is documented but ungated. Recorded as the accepted cost in D-13's
  `because:`; if the operator later wants it enforced, that is a gate, not a config key.
