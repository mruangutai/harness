# Observations — harness-backend-dev — FEAT-04-decisions-index

- 2026-08-02: check-docs.sh reports STALE hit paths relative to CLAUDE_PROJECT_DIR (it `cd`s in first),
  not absolute — a test asserting on the absolute path string will FAIL for the wrong reason even
  though the checker correctly flagged the row. Assert on the relative `docs/harness/...` form.
- 2026-08-02: bash-write-guard's command parser is naive about heredocs/multi-statement lines —
  a heredoc body containing `<!--`-style markup, or two commands joined with `&&`/`;` where the
  second looks like a redirect target, gets misread as a write outside domain. Prefer the Write
  tool for scratch scripts and single simple Bash invocations over heredocs when domain-gated.
- 2026-08-02: real docs/harness/DECISIONS.md: raw `re.findall(r'^## (DEC-\d+)')` (undeduped) = 170
  matches; the fence-guarded parse (mirroring check-docs.sh:44-48) yields 169 distinct DEC numbers.
  Confirmed empirically, not just from the plan text.
- 2026-08-02: T-02 built gen-decisions-index.py. The plan's row grammar in the generator-emitted
  header (`- DEC-NN @<line> [tags] refs: <graph> :: <ruling>`) has no field for the amendment span
  it separately mandates computing (am.1-am.N etc.) — none of the six T-01 tests assert on it either.
  I placed it as an optional token right after `@<line>` (e.g. `@3217 am.1-am.2 [tags] refs: ...`),
  omitted entirely when a decision has no amendments. Raised as open_questions (placement only, not
  existence) rather than guessed silently.
- 2026-08-02: TOPIC_VOCAB seed words are single-word substrings only (each tag maps to `(tag,)`);
  the plan names the seed list but not synonym expansions. Bare substrings over-match (e.g. `map`
  inside `mapping`, `state` inside `statement`) — worth tightening with word boundaries if tag
  precision ever matters downstream; not gated by any current test.
- 2026-08-02: idempotency (DEC-19 double `SUPERSEDED BY` clause growth, MF-4b) is untested by the six
  T-01 tests — verified manually in /tmp by running the generator twice against a copy of the real
  DECISIONS.md and diffing; identical both times. `rm -rf` outside the repo is blocked by
  bash-write-guard even under /tmp — use `mkdir -p` onto a fresh path instead of removing first.
- 2026-08-02: T-02 follow-up: widened the header `Row:` grammar to `[am-span] [tags]` (was `[tags]`
  only, per open_questions above) — `gen-decisions-index.py:68-70`. Dry-ran `--stdout` against the
  real `docs/harness/DECISIONS.md`: exit 0, stderr 0 bytes, 169 rows, 169 RULING PENDING, 189 lines
  (19 header + 1 blank + 169 rows, identity closes exactly), every row has exactly one ` :: ` on one
  physical line. No generator defect found on the real authority. check-domain.sh blocks
  harness-backend-dev from writing `.harness/features/*/runs/**/digest.md` — only
  `.harness/features/*/observations/harness-backend-dev.md` is permitted; the digest for this step
  lives in the conversation return, not a run-dir file.
- 2026-08-02: T-11 re-pinned the two authority-count literals (170→171, 169→170, both message
  strings) after DEC-170 landed at DECISIONS.md:4415, and added the 30-word ruling cap inside the
  existing thin-prose loop in `test_committed_index_is_complete_and_within_budget`, sharing the same
  `stripped` variable so the char floor and word cap can never disagree about what a ruling is.
  Placed both `thin` and `over_cap` returns together after the loop (not after `thin` alone) so a
  future remediation pass that shortens rulings can't blank the over-cap list mid-flight by tripping
  the char floor first. Result against the real committed index: 83 rows over cap (task prompt's
  own estimate said ~82 — off by one, immaterial), worst DEC-167 (165 words).
