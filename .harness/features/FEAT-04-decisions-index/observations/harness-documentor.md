# Observations — harness-documentor — FEAT-04-decisions-index

- 2026-08-02 (T-03): `gen-decisions-index.py` ignores argv entirely — invoking it with `--help` as a
  usage probe silently generated `docs/harness/DECISIONS-INDEX.md`. Probe a generator with
  `head -40 <script>` instead; a no-arg-parsing script treats any probe as a run.
- 2026-08-02 (T-03): measured output matched the orchestrator's dry-run exactly — 189 lines,
  169 `^- DEC-` rows, 169 `RULING PENDING`. Amendment-span rows are exactly three: DEC-137 @3184
  (`am.1-am.2`), DEC-138 @3238 (`am.1-am.7`), DEC-145 @3493 (`am.1-am.2`), at index lines 157/158/165.
- 2026-08-02 (T-03): cross-check grep trap — every row carries a `DEC-NN @<line>` token, so
  `grep -o 'DEC-[0-9]* @[0-9]*'` returns all 169. The amendment-span discriminator is `am\.`, i.e.
  `grep -n '^- DEC-.* am\.'`.
- 2026-08-02 (T-03): `check-docs.sh` exits 0 with the sentinel-bearing index present — 45 patterns
  across 98 files. Adding `DECISIONS-INDEX.md` and this log did not put it red.
- 2026-08-02 (T-03): `bash-write-guard.sh` misattributes the target of `rm` in a compound command.
  `rm docs/harness/DECISIONS-INDEX.md; python3 <script>` was blocked with "`rm` targets python3,
  outside your domain" — it appears to scan the whole command line for rm arguments rather than the
  single statement. Splitting into two Bash calls worked. Raised upward as an open_question.
- 2026-08-02 (T-04): backfilling N rows is one scripted read-modify-write with `replaced == 88` and
  line-count assertions inside the script, not N `Edit` calls — the sentinel is identical on 169 rows
  so `Edit` needs the whole row prefix each time, and the assertions produce the DIGEST's measured
  numbers as a side effect.
- 2026-08-02 (T-04): `check-domain.sh` blocks `Write` to `/tmp` for this agent (domain is `docs/**`
  plus the observations log), so a throwaway helper script has no legal home — pipe the program to
  `python3 - <<'EOF'` on stdin instead, which creates no file.
- 2026-08-02 (T-04): `bash-write-guard.sh` reads a Python comparison as a shell redirect —
  `if n>88:` inside a heredoc was blocked as "`redirect` targets 88:". A read-only verification
  command was refused. Workaround: express bounds as `n in range(1,89)`. Raised as an open_question.
- 2026-08-02 (T-04): the register trap in the corrections cluster (DEC-81, DEC-83..DEC-87) is that
  the entries are *about* a wrong prior claim, so the natural sentence narrates the correction —
  which `check-docs.sh` exempts via its "corrected"/"was wrong" keyword skip and therefore cannot
  catch. Only D-07 catches it; state the current rule and nothing about its predecessor.
- 2026-08-02 (T-05): `docs/harness/DECISIONS-INDEX.md` is itself a `check-docs.sh` scan target, so a
  ruling I write can trip a marker declared in a part of `DECISIONS.md` I deliberately never read.
  `grep -n 'stale:' docs/harness/DECISIONS.md` is a cheap whole-file marker census (49 hits) that
  stays inside the read budget — run it before writing index rows, not after.
- 2026-08-02 (T-05): the marker match is case-insensitive substring (`check-docs.sh:140`), and
  `DECISIONS.md` itself is excluded by basename plus any path containing `/runs/`
  (`check-docs.sh:93-95`). So phrasing that merely counts differently from a declared pattern
  ("writes the domain-hook entry" vs a declared count phrase) clears it, while a near-quote does not.
- 2026-08-02 (T-05): `Write` to `/tmp/*.py` was permitted for this agent this run, unlike the T-04
  observation above — so the heredoc workaround is not always necessary; test the cheap path first.
- 2026-08-02 (T-06): ordinal counts of the mandatory hook set are declared stale twice over in
  `DECISIONS.md` (:2653-2655 and :3487-3489), so a ruling naming the digest hook must state no
  ordinal and no count at all — "a `SubagentStop` hook registered in `settings.json`", never an
  Nth-prerequisite phrasing. Same class: `DECISIONS.md:2487` and `:3526-3528`.
- 2026-08-02 (T-06): a decision's own row must be written as amended, and an amendment can sit
  ~1000 lines below its parent (DEC-138's am.5-am.7 live at `DECISIONS.md:4244-4375` while the entry
  starts at `:3238`). `grep -n '^### DEC-NN amendment' docs/harness/DECISIONS.md` before writing any
  row whose index token shows an `am.` span; the burn-down count cannot detect an under-stated row.
- 2026-08-02 (T-06): amendment headings are keyed by their captured DEC number, not by position, so
  a `### DEC-137 amendment 2` heading physically inside DEC-138's body (`:3327`) belongs to DEC-137's
  ruling. Trust the captured number over the surrounding text.
- 2026-08-02 (T-07): the committed-index assertion's budget is a **whole-file 260-line cap** with no
  per-row length cap (`test-gen-decisions-index.py:353`), so long multi-clause rulings are legal;
  its skip predicate is file-absence only (`:343`), and thin rows fail at `<20` non-whitespace
  characters after stripping (`:378`). Read the predicate before rewriting rulings for length.
- 2026-08-02 (T-07): a heading's *body region* (heading → next `^## `) is not the same as the
  decision's own prose. `## DEC-168` at `DECISIONS.md:4221` ends at `:4243`, and `:4244-4375` is
  DEC-138 amendment text physically inside that region — 132 of 155 lines. Bound a ruling by the
  next heading of ANY level, not the next same-level one.
- 2026-08-02 (T-07): two inline `**Amendment …**` paragraphs can carry no DEC number and key
  positionally to the enclosing heading (`DECISIONS.md:3530`, `:3536` → DEC-145). So the numbered
  `### DEC-NN amendment` grep is necessary but not sufficient; also grep `^\*\*Amendment` in-range.
- 2026-08-02 (T-07): 31 `Edit` calls with the full unique row prefix worked cleanly and needed no
  script, no heredoc and no temp file — the row prefixes are unique once the DEC number is included,
  so the earlier scripted approach is optional rather than required at this batch size.
- 2026-08-02 (T-07): `EXIT=$?` after a pipeline reports the LAST element's status, so
  `check-docs.sh | tail -15; echo $?` measures `tail`. Run a gate unpiped and read the full result
  when the exit code is a reported field.
- 2026-08-02 (T-08): the residual marker pass was a **no-op — 0 rows flagged**. `check-docs.sh` exits
  0 with all 169 rulings written (45 patterns, 100 files), so the T-05/T-06 practice of censusing
  markers *before* writing each row is what drove the residual to zero. Marker discipline up front
  costs less than an escape pass afterwards.
- 2026-08-02 (T-08): a row that *documents* the escape-marker syntax exempts itself, because the
  checker's test is plain substring containment (`check-docs.sh:133`). DEC-104's ruling at
  `DECISIONS-INDEX.md:124` is the only `grep -c 'ok-stale'` hit in the file and nobody added it as an
  escape — so the file's marker grep overstates the true residual by one. When a doc must name a
  suppression token, expect the naming to trigger the suppression, and report the grep with that
  caveat rather than as a count of deliberate escapes.
- 2026-08-02 (T-08): to prove a file is genuinely watched by `check-docs.sh` without touching it,
  replicate its target glob read-only in `python3 -c` and check the path is in the list plus that your
  target count equals the count the checker printed (100 == 100). That beats a probe edit to a
  finished deliverable, which risks leaving a flagged phrase behind if the run dies mid-restore.
- 2026-08-02 (T-08): `bash-write-guard.sh` again misattributed a compound command —
  `... > file && check-docs.sh; echo $?; rm -f file` was blocked as "`rm` targets echo". Same class as
  the T-03 and T-04 observations; the guard scans the whole command line rather than the statement.
- 2026-08-02 (T-06): the scripted read-modify-write should assert the row's right-hand side equals
  the sentinel before replacing and count `>= 20` non-whitespace characters per new ruling — both
  assertions inside the script, so a mis-keyed id fails loudly instead of silently editing a row
  belonging to another batch.
