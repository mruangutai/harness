# Code review — construct validator — `e527bca` (round 3 on the exit-2 contract)

**BLUF: closed by construction on the str-argument axis, not merely enumerated a third time.
The reordering opened no path. `must_fix: []`, PASS with two low advisory notes.**

Reviewed `78e87dc..e527bca` (never `..HEAD`). `git rev-parse HEAD` = `e527bca78a9e313bfff78bbfb00d070a7d4e54f5`,
confirmed. `git status --porcelain` clean for both named paths — working-tree reads of them match
HEAD. Source read via `git show <sha>:<path>` throughout (G-01). No `[harness:human]` commits in
range (`git log --oneline -5`: all five subjects carry a `[harness:*]` non-human tag) →
`human_commits_in_scope: []`.

## Probe A — construction, my own conclusion

For a `str` operand, `int()` raises **only `ValueError`** — confirmed empirically: reproduced the
4300-digit-cap message live on this repo's interpreter (`Python 3.14.5`, matches
`FEAT-05/PLAN.md:1144` and sibling notes — this repo's fleet is 3.11+, where the cap is native).
`TypeError` is unreachable **via the CLI entry point** — `sys.argv` elements are guaranteed `str`,
so `int(issue_arg)` at `board-station.py:73` never sees a non-str. `TypeError` is only reachable by
a direct in-process call `main([42, "Plan"])` bypassing `sys.argv`: `int(42)` succeeds, then
`issue_arg.isascii()` at line 77 raises `AttributeError` on an `int` — uncaught, non-2 exit.
Grepped the repo for any such caller: none exists (`board-station.py` is only ever invoked as a
subprocess — `harness-plan.md:11`, `test-board-station.py`'s `subprocess.run`). **Verdict: the
catch is total on the str-argument axis, and the CLI entry point is the only thing that supplies
that axis in this repo.** That is a structural claim, not "handles the cases we know about" — see
Probe C.2 for where the same boundary resurfaces in the docstring.

## Probe B — did the reordering open anything? (the question wanted most)

`int(' 42 ')` and `int('4_2')` both succeed. Established **by reading the code and confirming
empirically**: neither opens a path, because `issue_arg.isascii()` and `issue_arg.isdigit()` at
line 77 are applied to the **original string** `issue_arg`, unchanged by the diff (AST-confirmed,
Probe D.1) — `' 42 '.isdigit()` is `False` (whitespace), `'4_2'.isdigit()` is `False` (underscore).
Both rejected with exit 2 — verified both analytically (isolated Python) and by an actual
`board-station.py " 42 " Plan` / `"4_2" Plan` run from a directory with no harness root above it
(safe under the hard bound: `board-station.py:88-90` returns before reaching `gh_board`), rc=2
both times.

**The quoted phrase "the ASCII and positivity checks on the parsed value" does not exist anywhere
in this repository** — checked the commit message, the code and docstring at `e527bca`, and
`git log --all -S "positivity"` and a plain-text repo grep for both fragments, case-insensitive,
tracked and untracked. It is not "the commit's own description." The accurate statement, verified
against the code: **ASCII and `isdigit` apply to the original string `issue_arg`; only the
positivity check (`<= 0`) applies to the parsed value `issue_number`.** This split is load-bearing,
not stylistic, and it is nowhere stated explicitly in the comment at `:65-71`. I built the
hypothetical "corrected" variant a future reader would produce by taking the wrong description
literally — apply `isascii()`/`isdigit()` to `str(issue_number)` instead of `issue_arg` — and ran
it against case r5's input, `'٢'` (Arabic-Indic digit two, `int()` parses it to `2`): the
variant returns **0**, i.e. it silently proceeds to move issue #2's card — reintroducing the exact
round-1 regression. The shipped suite's `r5.returncode == 2` assertion is precisely what pins this
split against that "correction" (discriminating, per P-12/O-03) — but the comment doesn't say so,
so nothing stops a future edit from "simplifying" the two variables into one and changing the test
to match instead of noticing the regression.
**Finding (low, advisory — must_fix: no):** `board-station.py:65-79` — the comment states the ASCII
test's purpose but never states which variable (`issue_arg` vs `issue_number`) each conjunct
targets; propose one added sentence naming the split explicitly, since the test suite's protection
depends on a reader not "fixing" the code to match a plausible-sounding but wrong description.

## Probe C — are the two corrected statements true?

1. **Comment `:65-71`** — accurate as written: matches the AST-confirmed behavior (Probe D.1) and
   every enumerated test case (r4/r5/r6, all PASS). No discrepancy found.
2. **EXIT CONTRACT `:25`, untouched this commit** — **true only on the str-argument axis, not
   literally true of `main()`'s own signature.** `main([42, "Plan"])` (a direct, non-CLI call)
   parses fine (`int(42)`) then dies uncaught at `.isascii()` on an `int` — a non-zero exit that is
   not 2, contradicting "2 is the ONLY non-zero exit" literally. No such caller exists in this repo
   (verified above), so it is not live, but the paragraph makes an unconditional claim about the
   whole module. **Independently checked the one other unguarded call on this path,
   `gh_board.load_board(root)` at `board-station.py:122`** (per advisor direction) — read
   `gh_board.py:43-86` at `e527bca`: the file open/parse is wrapped (`except (OSError, ValueError):
   return None`), every other branch is a type-check returning `None`, and the one `int()` call
   (`int(number.strip())`) only runs after `number.strip().isdigit()` is already confirmed — no
   raise path. So the EXIT CONTRACT is **not** broken on the environmental axis; only on the
   direct-call/non-str-argv axis. **Proposed scoping clause:** *"...for the CLI entry point invoked
   on `sys.argv`-sourced string arguments; `main()` itself does not enforce that its `argv`
   elements are `str`."* The same unqualified sentence is echoed in the new comment at `:71`
   ("2 is this tool's only non-zero exit") — same gap, not fixed by this commit, worth folding into
   the same edit rather than filing twice next round.
3. **`harness-simplify/SKILL.md`** — the falsifiable defect is gone. History: `2cba9fb` had
   "...is a sign the fix is not deep enough. So is a methodology..." (clear antecedent); `78e87dc`'s
   dedup collapsed it to "...is **the same smell**" — dangling, because the deleted sentence never
   used the word "smell" at all. `e527bca` changes it to "...is **a sign of the same thing**" — no
   longer callbacks to a nonexistent noun. The antecedent is soft (leans on the paragraph's ALTITUDE
   theme rather than one crisp noun) but not factually broken. Info only — style never gates.

## Probe D — containment

1. **AST compare, `board-station.py` `main()`, `78e87dc` vs `e527bca`:** the `int(issue_arg)` call
   moved from an unguarded `Assign` after the boolean guard into a `Try/ExceptHandler(ValueError)`
   placed *before* it; inside the guard, the positivity comparison's left operand changed from a
   fresh `Call(int, [issue_arg])` to a `Name` reference to the already-parsed `issue_number`. The
   `isascii`/`isdigit` AST nodes are byte-for-byte unchanged (no diff lines touch them) — confirms
   Probe B: those two checks still run against the original string.
2. **`test-board-station.py`:** purely additive. `check(` count 12 → 13; the diff contains only
   `+` lines (no existing assertion removed, weakened, or relabelled). New case `r6` asserts
   `r6.returncode == 2` exactly, not `!= 1`.
3. **Full file list (3):** `board-station.py` (the fix), `test-board-station.py` (additive test),
   `harness-simplify/SKILL.md` (dangling-phrase correction). No scope creep, no missing file.
4. **Independently re-run, not trusted from the commit message:**
   - `python3 test-board-station.py` → all 13 PASS, exit 0.
   - Red-first claim reproduced in isolation (not by editing the shipped file): the pre-fix logic
     path for the 4301-digit case raises `ValueError` uncaught, matching "rc6=1."
   - `bash run-unit-tests.sh --kind unit` → exit 0. `--kind integration` → exit 0.
   - T-02, T-03, T-05 `verify:` clauses read from `plan.yaml` via `yaml.safe_load` and executed
     **verbatim** with `bash -c <exact string>` (no manual retyping, no abbreviation) — all three
     print their GREEN sentinel and exit 0.

## Dismissed candidates (recorded, not filed — P-15)

- **Pre-3.11 `MemoryError`/algorithmic-complexity on `int()` of a huge digit string:** true only on
  an unpatched pre-3.11 interpreter (the digit cap was backported to 3.9.14+/3.10.7+ and is native
  in 3.11+); this repo's interpreter is 3.14.5. Environment-dependent, pre-existing had it existed,
  not introduced by this diff. Not filed.
- **`' 42 '` / `'4_2'`:** analyzed as a possible reordering hole; both rejected by `issue_arg.isdigit()`
  on the original string, confirmed analytically and by a live, safely-bounded run. Not a finding.
- **The quoted phrase "ASCII and positivity checks on the parsed value":** does not exist in this
  repo (see Probe B). Reported as a discrepancy in the dispatch's characterization, not a code
  defect — the accurate split is stated in Probe B's finding.

## Already ruled — not re-filed

`ship-review-2026-08-17-13.md` B-1..B-26, `runs/2026-08-17-14-finalpass-validator/digest.md` Q1–Q6,
`runs/2026-08-17-15-refix-validator/digest.md` Q1–Q6 (including the `check-domain.sh`/`Bash`
workaround, Q2) — all confirmed present in `notes/`, none re-raised here.
