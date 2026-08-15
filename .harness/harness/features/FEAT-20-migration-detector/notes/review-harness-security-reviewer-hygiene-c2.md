# Security review c2 — PR #385 fix commits, a714bd0..6296149 (base 3c75aa6)

**Verdict: PASS.** Own census run first (`git diff --name-status a714bd0..6296149`,
12 paths, matches the dispatch's expected delta). Scoped IN on the two code paths;
zero findings, severity info.

**Provenance:** `git rev-parse HEAD` = `6296149238a71f55b0047d760fa5d65c9284db3f` —
working tree already sits exactly at the pinned SHA, and
`git diff 6296149 --name-only -- <every file Read below>` returns empty. All Read/
grep results in this artifact are valid for the pinned SHA, not a stale checkout.

## 1. `check-state.sh` INV-27 cause-table restructure (:1298-1319)
Diff confirmed via `git diff a714bd0..6296149 -- .../check-state.sh`: table values
became a mix of plain strings and lambdas; `blame()` is now computed once (:1318) and
appended to every cause's text (:1319), replacing the old per-lambda `+ blame(...)`
inlining for only `unreadable`/`neither`.

- `no-evidence` lambda: unchanged, interpolates only `root` (the scan root path) — no
  new field.
- `undeclared-segment` lambda (unchanged bytes, confirmed same in both SHAs): still
  `", ".join(_srep.detail or ())`. Traced `_srep.detail`'s origin in
  `layout_migration.py` (untouched by this diff, not in the 12-path census):
  `_evidence()` (`layout_migration.py:164-186`) builds it from
  `os.path.relpath(p, root)` where `p` is a `glob.glob(".harness/*/features/*/feature.json")`
  match whose `*` segment is not in the fleet-declared set. **This is genuinely
  filesystem-derived**: whoever creates a directory under `.harness/` in the working
  tree names that segment, and it flows unescaped into the printed finding. Not new —
  `render()` (`layout_migration.py:315-317`) has done the identical join since before
  a714bd0, and the check-state.sh side of this specific lambda is byte-identical
  across a714bd0→6296149. Recording per P-12 rather than dropping: whoever can create
  that directory already has write access to the repo tree (P-02, no privilege
  gained), and the string is displayed as plain CLI text, never eval'd or
  shell-interpolated — worst case is misleading/spoofed text in an operator-read
  finding (or a log line, if the directory name carries a newline), not code
  execution. Pre-existing, unchanged by this diff, out of scope for a c2 verdict.
- The one behavioral change (blame() now appended to *every* cause, not just
  `unreadable`/`neither`) only widens which of the already-static `READER_TABLE`
  paths get named — same closed, hardcoded set assessed clean in c1. No new
  attacker-influenced content enters that append.

## 2. `test-check-state.py` -1148 lines
Census: at a714bd0, `case_m` through `case_x` (14 names) were each **defined twice**
— Python's last-def-wins means only the second (later, lines 1662-2899) body was ever
executed via `main()`; the first occurrence (lines 528-1661) was dead code shadowed
before any test ran. Programmatically diffed every duplicated name's *live* (second)
body against the sole 6296149 body:

| Result | Names |
|---|---|
| byte-identical | case_m, case_m2, case_m3, case_n, case_p, case_q, case_t, case_r, case_s, case_o, case_u, case_v, case_w (13/14) |
| differs, verified equivalent | case_x |

`case_x` shrank from 138 to 124 lines because it now imports `layout_fixtures.MARKER`/
`FLEET_TEXT`/`STUB` instead of restating the same literals inline — confirmed the
fixture module's values (`layout_fixtures.py:20,26`, `layout_migration.py:115`) match
the old hardcoded strings exactly. Its five assertions (x.1-x.5, INV-27
mixed/cannot-verify/clean/no-marker/unimportable) are unchanged in substance. Also
confirmed `case_l`'s budget/INV-22 assertions (l1-l8, referencing the HIGH-2 PR #142
regression) are the sole `case_l` definition, untouched — a separate, correctly-named
copy that the dead first `case_x` had mistakenly duplicated verbatim under the wrong
name. `main()` still calls all 26 case functions plus the exit-code-unchanged check,
identical to a714bd0's live `main()`.

**Ran the suite (P-04 — static byte-diff alone does not catch a NameError, and
retained `case_x` is a composition that never existed as a unit at a714bd0):**
`python3 .claude/skills/harness/bin/test-check-state.py` at HEAD (=6296149) —
exit 0, every case including `(x.1)`-`(x.5)` and the `exit code unchanged by INV-21`
check printed `ok`, none FAILed. **No security-relevant assertion was removed; the
deletion is exactly the dead-code cleanup it claims to be, and the suite proves the
retained composition actually runs.**

## 3. Two deletions in `.harness/members/backend-dev/`
`FEAT-02-t01.md`/`t02.md` are historical implementation notes (RED/GREEN task
receipts for an unrelated prior fix, `validate-digest.py` echo-shadowing) — no
credentials, no secrets, confirmed by reading the diff content in full. Grepped
`.harness/team-config.yaml` and `check-domain.sh` for `members/`: zero references to
this path (the `members:` hits in both are unrelated YAML/comment usages — squad
roster keys, not path grants). One dangling reference found:
`.harness/features/FEAT-02/runs/2026-07-27-03-eng/state.yaml:19,36` still points at
the now-deleted paths — a historical audit-trail artifact pointer, not an
access-control mechanism, so a broken link here doesn't affect any permission or
domain grant. Confirmed no gate depends on it. Advisory only, not an open question.

## 4. Routine sweeps
- Secrets: `grep -inE 'api[_-]?key|secret|token|password|BEGIN (RSA|OPENSSH|PGP)|Authorization:|Bearer '`
  over the full `a714bd0..6296149` diff — only self-referential hits are the grep
  pattern quoted inside this diff's own new review-artifact text and the word
  "tokens" inside "PREDICATES tokens" (test-suite prose); no real credential-shaped
  string.
- CI/hooks/settings: `git diff --name-only a714bd0..6296149 | grep -E '^\.github/|settings\.json|hooks'`
  — zero matches. Confirmed against the full 12-path census, not just the named
  files.

## Scope reasoning
Both surfaces named in the dispatch were traced to their data origin and verified by
measurement (byte-diff of duplicate function bodies + a green execution of the
retained suite, grep of consumer files, read of the fixture-module values) rather
than argued from structure alone. Zero findings — severity info per G-07, not n/a,
since this was scoped in and actually assessed.

Pre-briefed items (#365, #367, #368-375, #377, #378, #380, #381, #384, #279) not re-filed.
