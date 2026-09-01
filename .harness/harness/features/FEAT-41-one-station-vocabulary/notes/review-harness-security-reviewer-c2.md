# Security review — FEAT-41-one-station-vocabulary — cycle 2 (gate bypass hunt)

**BLUF: FAIL, severity_max=high.** Both gates the dispatch names are still bypassable, each by
a route cycle 1 did not try. H-01's symlink fix (`_route_candidates`) never checks
`os.path.islink()` against a **hardlink** and computes each hop's relative target from the
**string dirname of the path as typed**, not the real filesystem location — a hardlink alias,
or a symlink reached through an intermediate symlinked *directory*, walks straight past it, PRE
and POST, confirmed live with the real `check-domain.sh` subprocess and a real corrupted
`plan.yaml`. H-02's `as_bash_reads_it` closes the one continuation form F-03/H-02 named and
nothing else — `plan-merge.py${IFS}sign-approval` (bash's classic filter-evasion idiom) evades
the tokenizer entirely and, confirmed end-to-end against a real `plan-merge.py` fixture,
**actually writes a forged `approval:` block**, exit 0, no stderr. All work is decision-only
subprocess measurement or throwaway `$TMPDIR`/tempdir fixtures; one real, git-tracked file was
never mutated except a single self-cleaning symlink probe against the real worktree/main-checkout
topology (created and removed by one atomic Python script; `git status --porcelain` confirmed
clean before and after — see §6).

## 1. H-01 — OPEN (regressed). New HIGH: hardlinks and directory-hop symlink chains bypass the
route-candidate walk entirely, PRE and POST.

Root cause, read at source (`check-domain.sh` `_route_candidates`, the `_MAX_HOPS=8` loop): it
resolves ONE hop at a time via `os.path.islink(cur)` / `os.readlink(cur)` /
`os.path.join(os.path.dirname(cur), target)`, where `cur` is always the **string form of the
path as originally written**, walked hop-by-hop — never a real filesystem `realpath`-style
resolution. Two consequences, both measured live:

- **`os.path.islink()` returns `False` for a hardlink.** A hardlink shares the target's inode
  but is a wholly separate directory entry with no "link" bit at all, so the walk's very first
  `islink()` check fails and the loop never starts — the hardlinked alias is reported back as
  its own (innocent) name, unconditionally, regardless of how many hardlinks alias the same
  bytes.
- **The per-hop relative-target join uses the AS-TYPED path's dirname, not the symlink's real
  physical location.** When an intermediate path *component* (not the final segment) is itself
  a directory symlink, the kernel correctly resolves it when performing the actual filesystem
  write, but `_route_candidates`'s `os.path.dirname(cur)` is pure string manipulation on the
  literal path handed to the hook — it has no idea the directory component was redirected, so a
  relative symlink's target (correctly interpreted by the OS as relative to its *real* parent
  directory) gets joined against the *wrong* (as-typed) parent by the walker, producing a
  candidate string that does not match `RE_PLAN_YAML` even though the real write lands on the
  real `plan.yaml`.

Every case below ran against the real `.claude/skills/harness/bin/check-domain.sh` via
subprocess, `agent_type=harness-orchestrator` (the wildcard-domain persona F-04/H-01 were both
about), fresh `tempfile.mkdtemp()` fixture root per case, decision-only unless noted. Script:
`local://feat41_h01_probe.py` is not persisted anywhere durable — re-run instructions are in
§7 if the fix needs re-verification.

| # | Probe | Mode | Expected | Observed exit | Verdict |
|---|---|---|---|---|---|
| 1a | Hardlink to `plan.yaml`, innocent name, same dir | PRE Write | 2 | **0** | **BYPASS** |
| 1b | Hardlink to `plan.yaml`, innocent name, inside `notes/` | PRE Write | 2 | **0** | **BYPASS** |
| 1c | Same hardlink, forged `approval:` block landed via it | POST Write | 2 | **0** | **BYPASS** |
| 1d | Sanity: real `plan.yaml` bytes actually changed via the hardlink write | — | true | true (confirmed: `approval:`/`FORGED` landed in the real file, same inode) | evidence |
| 2a | Symlinked PARENT DIR (`notes/portal -> ../stash`) + HARDLINK inside `stash/` to `plan.yaml` | PRE Write | 2 | **0** | **BYPASS** |
| 2b | Symlinked PARENT DIR (`notes/portal2 -> ../stash`) + a **symlink** inside `stash/` (`-> ../plan.yaml`) — dir hop + file hop, both symlinks | PRE Write | 2 | **0** | **BYPASS** |
| 3 | Symlinked FEATURE DIRECTORY, write to `<link>/plan.yaml` | PRE Write | 2 | 2 | holds (shape alone denies — the *written* path still ends `…/plan.yaml`) |
| 4 | Dir hop (`notes/c -> a/b`) landing on a FILE symlink at the SAME depth the walker assumes | PRE Write | 2 | 2 | holds |
| 5a | Correctly-computed 3-level-deep relative symlink (`notes/x/y/correct.md -> ../../../plan.yaml`) | PRE Write | 2 | 2 | holds |
| 5b | Negative control: same relative string, one level shallower, legitimately overshoots to `features/plan.yaml` | PRE Write | 0 | 2 (denied for an unrelated reason — ordinary DOMAIN refusal, not the plan.yaml route rule; not a finding) | n/a |
| 6 | Symlink from the **real worktree's own granted `notes/`** to the **real main checkout's** `plan.yaml` (FEAT-40, present in both checkouts) — genuine git-worktree topology, not a synthetic fixture | PRE Write, decision-only | 2 | 2 | **holds** — `harness_boundary.checkout_relative` correctly recognises the cross-checkout hop and denies (see §6 for the self-cleaning method) |
| 6-fixture | Same shape with two UNRELATED (non-git-linked) tempdirs, both directions | PRE Write | 2 | 0 | not a finding — this reproduces only because unrelated tempdirs carry no git-worktree relationship for `checkout_relative` to recognise; superseded by the real-topology result above, which is authoritative |
| 7 | Symlink route inside a `.claude/worktrees/…` layout | PRE Write | 2 | 2 | holds |
| 8 | `./`, doubled slash, `..` traversal, UPPERCASE link name, case-folded address, NFC/NFD unicode link name — all addressing the SAME already-denied symlink | PRE Write | 2 | 2 (all) | holds |
| 8-trailing | Same symlink addressed with a **trailing slash** appended | PRE Write | 2 | **0** | **BYPASS at the gate** — `os.path.islink(path + "/")` returns `False` on this platform even for a real symlink, so the walker never starts. Separately confirmed at the OS level: `open(symlink_path + "/", "w")` **actually writes through to the real target** on this filesystem (macOS/APFS) — not merely a gate blind spot, a real write-through. Rated as part of the same H-01 class, not a separate line item; production-Write-tool-specific confirmation (as opposed to Python `open()`) not independently obtained — see §7 |
| 9a | Symlink chain of 10 hops (> `_MAX_HOPS=8`) to `plan.yaml` | PRE Write | 2 | **0** | **BYPASS — the hop cap fails OPEN, not closed.** Beyond the cap the walker simply stops with a candidate list that never reaches `plan.yaml`; a 1-hop symlink is already denied, so this only matters as an *additional* route when the direct route is blocked — lower severity than 1a/2a/2b but a genuine, no-cost-to-the-attacker gap (creating 9 trivial symlinks via unguarded `ln -s` costs nothing extra) |
| 9b | Chain of exactly 8 hops (at the cap) | PRE Write | 2 | 2 | holds (boundary control) |
| 9c | Symlink LOOP (A↔B) | PRE Write | 0 (must not hang, must not crash-open) | 0, 0.05s | holds — terminates promptly via the hop cap, no crash, no denial-of-service |
| 10 | Symlink created via a real `ln -s` subprocess (not `os.symlink`) | PRE Write | 2 | 2 | holds — creation method is irrelevant to the walker once the link exists |
| 10b | HARDLINK created via a real `ln` subprocess | PRE Write | 2 | **0** | **BYPASS** (same root cause as 1a/1b, confirmed via the real `ln` binary) |
| 11 | Edit tool (not Write) through an ordinary 1-hop symlink route | PRE Edit | 2 | 2 | holds |

**Does anything intercept link CREATION at all?** No. `ln`/`ln -s` do not appear anywhere in
`bash-write-guard.sh`'s command classifier (`sed`/`perl -i`, `tee`, `mv`/`cp`, `rm`, `sponge`,
`awk -i`, and a generic `>`/`>>` redirect scan are the entire set) — confirmed both by reading
the source and, incidentally, by my own session: as `harness-security-reviewer` I am READ-ONLY
under `bash-write-guard.sh`'s reviewer carve-out, and a Bash command containing `rm` in the same
call was correctly denied outright, while an `ln -s`-only command (no `rm`) executed with no
denial at all. This is consistent with the gate's own documented scope ("truly arbitrary shell
remains unwinnable and is caught post-hoc, not pre") and is not itself a new finding — it is the
precondition that makes 1a/1b/1c/2a/2b/10b reachable via ordinary Bash with zero setup friction.

**H-01 verdict: OPEN.** The symlink-by-name gap F-04/H-01 closed is real and stays closed
(cases 3, 4, 5a, 6, 7, 8, 9b, 10, 11 all hold). But the fix's mechanism — `os.path.islink` plus
string-dirname hop-walking — has a materially identical blast radius to the original hole: any
governed agent with an ordinary Bash tool (unguarded `ln`, no domain check on link creation) can
still land a forged `approval:` block or an illegal station word in the real `plan.yaml`, PRE and
POST, via a hardlink or a directory-hop symlink chain, exactly the threat class F-04/H-01 exists
to close. **HIGH, blocks ship**, same bar as the original H-01 (reachable by every governed agent
via a path they are already granted, zero detection pre- or post-hoc).

## 2. H-02 — OPEN (regressed). New HIGH: `${IFS}` word-splitting bypasses `plan-sign-gate.py`
and reaches real execution.

`as_bash_reads_it`'s `CONTINUATION` regex closes exactly the one bash mechanism it names
(`\<newline>` line continuation) and nothing else. The gate's own docstring already discloses
one class as permanently out of scope ("a tool name produced only by shell expansion… is
invisible here") — `${IFS}` is a **different** class: the literal substrings `plan-merge.py` and
`sign-approval` are directly present and adjacent in the command text; only the WHITESPACE
between them is produced by shell variable expansion (`$IFS` defaults to space/tab/newline, and
an unquoted `${IFS}` expansion between two words is bash's textbook idiom for defeating
naive-separator filters). This is squarely the adjacency-testing gap the gate exists to close
(the same class as bare `--` and the backslash-newline it already fixed), not the
tool-name-obscured-by-a-variable class the docstring disclaims.

Every gate row below fired the real `plan-sign-gate.sh` (decision-only, `agent_type` set) via
subprocess. Every row marked "actually-signed" additionally ran the exact command through **real
bash** against a disposable, correctly-shaped `plan.yaml` fixture (`.harness/<repo>/features/
<slug>/plan.yaml`, carrying a pre-existing `approval:` scaffold so `cmd_sign_approval`'s own
precondition is met) and read the file back afterward.

| # | Probe | Gate exit | Denied? | Real execution reached `sign-approval`? | Approval block actually written? |
|---|---|---|---|---|---|
| 1a | `plan-merge.py${IFS}sign-approval …` (verb, and every subsequent arg, IFS-joined) | **0** | **NO** | yes | **YES — forged, signer "Adversary"** |
| 1b | `IFS=$'\t'; plan-merge.py<TAB>sign-approval …` | 2 | yes | — | — |
| 1c | `plan-merge.py${IFS,}sign-approval …` | **0** | **NO** | yes | **YES — forged** |
| 2 | Real embedded newline inside a bash -c string (not backslash-continued) | 2 | yes | — | — |
| 3 | `;` inside a quoted, unrelated string (negative control) | 0 | correctly allowed | — | — |
| 4 | Backslash-TAB-newline (not a real bash continuation) | 0 | correctly allowed (bash doesn't continue here either — no mismatch) | — | — |
| 5 | Backslash-CR-LF continuation | 2 | yes | — | — |
| 6 | Doubled backslash before newline (escaped backslash; bash does NOT continue) | 0 | correctly allowed (matches real bash) | — | — |
| 7 | `bash <<'EOF' … EOF` heredoc | 2 | yes | — | — |
| 8 | `eval "…"` | 2 | yes | — | — |
| 9 | `sh -c '…'` | 2 | yes | — | — |
| 10 | `echo sign-approval \| xargs -I{} plan-merge.py {} --file … ` | **0** | **NO** | yes | **YES — forged** (upgrades cycle 0's "confirmed reachable and executable, rated lower" to a full E2E proof; still the disclosed `xargs` residual class, not new) |
| 11 | `$(printf "…")` command substitution at command position | 2 | yes (shlex's `punctuation_chars` mode tokenizes `$`/`(`/`)` separately, leaving `plan-merge.py`/`sign-approval` coincidentally adjacent in the token stream) | — | — |
| 12 | Comment line, then the ordinary unobfuscated call | 2 | yes | — | — |
| 13 | `--`, `-- --`, `-- -- --` runs before the verb (F-03 regression control) | 2 (all three) | yes | — | — |
| 14/14b | Absolute path / `./`-relative tool name | 2 | yes | — | — |
| 15 | `env` wrapper before `python3` | 2 | yes | — | — |
| 16 | Shell function defined+called in ONE payload, verb passed as a literal argument | 2 | yes (the literal tokens are still adjacent in this call's own text) | — | — |
| 17 | `--file=path` long-option-equals form (plain, unobfuscated) | 2 | yes | — | — |

**H-02 verdict: OPEN.** Cases 1a/1c are a live, end-to-end confirmed forged operator signature —
`plan-merge.py${IFS}sign-approval --file${IFS}<plan> --by${IFS}Adversary --date${IFS}2026-08-31`
reaches `cmd_sign_approval`, passes `_verify_signature`, and writes `approval: {status: approved,
approved_by: Adversary, date: 2026-08-31}` to the real file, exit 0, no stderr from either gate.
**HIGH, blocks ship** — identical threat class and reachability bar to F-03/H-02
("a forged main-session-only approval signature, reachable by any agent with ordinary Bash
access"). Case 10 (`xargs`) is the same disclosed-but-now-fully-proven class from cycle 0; I do
not double-count it as a second HIGH, since it shares the gate's own root cause and remedy with
1a/1c and cycle 0 already named it (at lower confidence) as real.

## 3. Carried third finding — set-feature-station/set-task-station identity binding — REPRODUCES,
and is a signed, disclosed residual, not a new must-fix.

Reproduced cleanly at this pin, both ways:

- **Synthetic fixture**: an agent granted domain ONLY over `FEAT-MINE-fixture` ran
  `plan-merge.py set-feature-station --file <FEAT-VICTIM-fixture>/plan.yaml --station done`
  directly — exit 0, no stderr, the victim's station flipped. The identical command, run as a
  **Bash** tool call through `bash-write-guard.sh` with `agent_type=harness-backend-dev` and
  **zero** domain grant over the victim feature, also exited 0 with **zero findings** — the
  command isn't merely "in domain," it is **invisible to the domain classifier entirely**,
  because `bash-write-guard.sh`'s command-pattern scanner has no entry for `plan-merge.py` CLI
  invocations at all (same absent-pattern class as the `ln`/`ln -s` gap in §1).
- **Real repository history, not hypothetical**: commit `01051eb` ("finish the migration for
  FEAT-45") in THIS feature's own branch used exactly this mechanism —
  `set-feature-station --station done` — to write into **FEAT-45-adversarial-plan-panel's**
  `plan.yaml` (`+status: done`), a different, already-shipped feature FEAT-41 has no other
  standing over, confirmed by `git log` and the diff (`.harness/harness/features/
  FEAT-45-adversarial-plan-panel/plan.yaml`). `handoff-build.md` corroborates: "FEAT-45's records
  were migrated by THIS feature, not by FEAT-45." This is not evidence of misuse in this
  instance — it is evidence that the mechanism the finding describes is exactly the one the
  build itself relied on, which is the strongest possible confirmation that it is real and load-
  bearing, not theoretical.

**Disposition.** `BRIEF.md`'s signed Approval block (`status: approved, approved-by: Mike
Ruangutai, 2026-08-30`) carries the disclosure verbatim: "After REQ-05 lands, a shell command
that writes a *legal* station value into `plan.yaml` is still not attributable to its author…
Closing that would need write attribution the platform does not offer" — explicitly labelled "A
disclosure, not a decision." No entry among D-01..D-16 in `plan.yaml` separately records this;
the BRIEF disclosure is the only place it is written down, and it is the operator-signed one. I
concur with cycle 1's own reconciliation (same role, same reasoning) that this is the disclosed
residual, not a new gap — REQ-05 promises no per-feature scoping. **Not added to must_fix**,
per this review's own precedent for a signed, disclosed risk. One advisory note for the record:
the disclosure's wording ("not attributable to its author") undersells the measured mechanism —
it is not merely unattributable, it is **completely unchecked by the domain layer**, for any
feature, not only the caller's own. Worth tightening the disclosure's wording at the next
revision; not a blocking ask.

## 4. Fail-open sweep

No new fail-open branch found beyond H-01/H-02 themselves (which ARE the fail-open branches this
cycle). Swept the full `git diff 7c4f0bd..39477a5 -- '*.py' '*.sh'` for `shell=True`,
`os.system`, `eval(`/`exec(` outside the two gates' own documented re-scan, and credential-shaped
strings: clean, matching cycle 0/1's own clean sweeps of the same files. The ~88 added/changed
`except` clauses are, on inspection, either narrow (`OSError` around a single filesystem probe,
absorbing by design and commented as such) or already reviewed at source in cycles 0/1
(`domain_check`'s manifest-parse handling, `harness_yaml.require_or_bootstrap`'s bootstrap grant).
I did not re-derive every one of the ~88 individually this cycle — see §5, unexamined.

## 5. Unexamined, named rather than omitted

- **Reverse direction of the cross-checkout symlink test** (main checkout → worktree). Testing
  it for real would require writing into the MAIN checkout, which is out of the WORKTREE
  constraint this dispatch sets; I inferred symmetry from `harness_boundary.checkout_relative`
  being a general "which checkout is this in" resolver rather than a worktree-specific one, but
  did not independently measure it. `[INFERENCE]`.
- **Production Write-tool byte-level confirmation of the trailing-slash bypass** (§1, row
  8-trailing). Confirmed at the `check-domain.sh` decision layer and at the raw-`open()` OS
  layer; not independently re-confirmed against the actual Claude Code/OMP Write tool binary the
  way cycle 1 confirmed the base symlink case. Given the settled base case (Write follows a
  symlink) and the measured OS-level write-through, I rate this reachable but flag the gap.
- **Full line-by-line audit of `gh-sync.py` (545 lines changed), `board_lifecycle.py` (118),
  `worktree_terminal.py` (302), `check-plan-routes.py` (152), `check-state.sh` (348)** beyond the
  injection/secrets/shell-metacharacter sweep in §4. Time-boxed toward the two named gates, which
  the dispatch marks as the point. No `subprocess` call in any of these uses `shell=True`; all
  use list-form argv (confirmed by grep, not by reading every call site).
- **SC-08's re-measured planned/plan-less counts** ("35 planned dirs and 10 plan-less terminal
  ones all carry no `status`, BUG-1071 alone does") — this is a code-reviewer/QA-lens data
  question, not a security one; not independently re-counted here.
- The other ~86 `except` clauses in the diff not individually re-derived (§4).

## 6. Worktree hygiene

`git status --porcelain` was clean of any change attributable to me before I began (confirmed
`pwd`/`git rev-parse --show-toplevel` at the start) and remains clean now. The one probe that
touched the real worktree/main-checkout topology (§1, row 6) created a symlink under my own
granted `notes/` pattern via a single self-contained Python script (`os.symlink` → subprocess
decision test → `os.remove` in a `finally:` block, no shell `rm`), confirmed removed
(`os.path.exists`/`os.path.islink` both `False` afterward) and `git status --porcelain` re-ran
clean immediately after. No tracked file was ever mutated by me at any point — all corruption
proofs (H-01 §1c/1d, H-02 §2) ran against disposable `tempfile.mkdtemp()` fixtures, never against
this worktree's own tracked files.

## 7. Re-verification notes for whoever fixes this

- H-01's fix needs to either (a) treat `os.path.islink` as necessary-but-not-sufficient and also
  compare `os.stat(cur).st_ino`/`st_dev` against the eventual resolved plan.yaml's inode (catches
  hardlinks the walker's readlink-chase cannot see at all), or (b) resolve each hop against the
  real filesystem location of the *previous* hop (e.g. track the physically-resolved parent
  directory alongside the as-typed one) rather than the as-typed string's dirname. Both closures
  need the hop cap to also change from "stop silently and return what's found" to a decision
  about what an exhausted cap MEANS (currently: unresolved tail is treated as safe — fails open).
- H-02's fix needs the same treatment `--` and the backslash-newline both got: normalise `$IFS`
  (and, generalizing, any unquoted-variable-expands-to-whitespace shape) before tokenizing, not
  merely one literal continuation form. The docstring's own framing ("a guardrail… NOT a security
  boundary") may be worth revisiting given `${IFS}` reaches real execution with the same ease and
  no more obfuscation effort than the `--` and backslash-newline cases already rated HIGH.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "H-01 and H-02 are both regressed, not closed — hardlinks/directory-hop symlink chains bypass the plan.yaml route denial, and ${IFS} word-splitting bypasses the sign-approval gate with a live, end-to-end forged signature."
  in_scope: true
  scope_reason: "Both gates named in the dispatch are the review's whole point; every probe targeted their enforcement mechanism directly."
  severity_max: high
  findings: 4
  must_fix:
    - "check-domain.sh _route_candidates: hardlink aliases of plan.yaml (os.path.islink is False for a hardlink) bypass the PRE and POST route denial entirely — confirmed live, real bytes corrupted in a disposable fixture (H-01, HIGH)."
    - "check-domain.sh _route_candidates: a symlink reached through an intermediate SYMLINKED DIRECTORY component resolves against the as-typed string dirname, not the real physical location, and misses the route — confirmed live with both a hardlink and an all-symlink chain (H-01, HIGH)."
    - "plan-sign-gate.py denies()/as_bash_reads_it: ${IFS} (and ${IFS,}) word-splitting between plan-merge.py and sign-approval evades the tokenizer; confirmed end-to-end against a real plan-merge.py fixture — a forged approval: block actually lands, exit 0, no stderr from either gate (H-02, HIGH)."
    - "check-domain.sh _route_candidates hop cap (_MAX_HOPS=8) fails OPEN on a chain longer than 8 hops — lower severity (a 1-hop symlink is already denied) but zero additional cost to an attacker via unguarded ln -s (H-01, secondary)."
  threat_model:
    - { boundary: "PreToolUse Write/Edit/NotebookEdit -> check-domain.sh plan.yaml route denial", stride: "T", mitigated: false }
    - { boundary: "PreToolUse Bash -> plan-sign-gate.py sign-approval refusal", stride: "S", mitigated: false }
    - { boundary: "PreToolUse Bash -> bash-write-guard.sh domain check on plan-merge.py CLI invocations (set-feature-station/set-task-station)", stride: "E", mitigated: false, precondition: "disclosed and operator-signed in BRIEF.md; not a gap this review adds to must_fix" }
    - { boundary: "PostToolUse Write/Edit sweep and Bash glob sweep -> vocabulary-only net", stride: "T", mitigated: false, precondition: "documented, unchanged residual: catches an illegal station word, never a well-formed forged approval" }
  open_questions:
    - { id: Q1, question: "Should plan-sign-gate.py's docstring framing ('a guardrail, NOT a security boundary') be revisited now that ${IFS} reaches real execution as easily as the already-HIGH -- and backslash-newline cases?", blocking: false }
    - { id: Q2, question: "Does the reverse cross-checkout direction (main checkout -> worktree) hold the same way the forward direction (measured, held) does? Not independently tested; inferred by symmetry of harness_boundary.checkout_relative.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-41-one-station-vocabulary/notes/review-harness-security-reviewer-c2.md
```
