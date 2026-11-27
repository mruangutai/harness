# BUG-2566 — cycle-3 apply receipt (run 2026-11-27-03-plan-product)

**The four remedies from the cycle-2 reader are now in T-01.intent and mirrored in BRIEF SC-01, SC-02, SC-04 and SC-06. Panel cycle 3 is recorded, and all 16 findings are resolved by T-01, so 0 remain open at any severity. check exits 0. approval stays `{status: pending}`. No APPROVAL-RESET receipt was printed.**

## Fields changed

plan.yaml has one change, made with `plan-merge.py amend --key tasks --id T-01 --field intent --expect-sha256 7e678e27…` (exit 0, `AMENDED tasks:T-01.intent`, no `APPROVAL-RESET:`). I made no decision, task, verify, files or fingerprint change. T-01.verify is unchanged because none of the remedies alters a verify line.

Each remedy in T-01.intent, with the token that locates it:

- **PF-1cf493dc** (held JSON BLOCKED witness and stale data-less finalize)
  - Test (a) adds three refusals: the JSON text of a PASS object, the malformed text `not json`, and the data-less finalize `{type: "result"}` with no data property. Each expects reason P and no policy calls.
  - Test (b) now has four carve-out tests (started or held, object or JSON text). Each asserts exactly one new validate-digest.py call with `args equal ["--hook"]` and a payload `digest_object` that deep-equals the decoded BLOCKED object.
  - Main is initialized through its unmarked fixture `ompContext("/repo", "Main", undefined, "main-session")` plus `before_agent_start({ systemPrompt: ["project"] })`, and never through start. This applies in (a) and (c).
  - The fail-first paragraph now says the (b) cases are "preserved, never as failing first".
- **PF-3eb8320f** (bounded FIFO probe): the FIFO case runs `root/fifo-probe.ts` through `spawnSync(process.execPath, …, { timeout: 5000, killSignal: "SIGKILL" })` with a 15000 ms test timeout. It asserts signal null, error undefined, status 0 and that the reason appears in stdout.
- **PF-37c5f930** (one descriptor for stat and read): entryState keeps the statSync kind check for a path that is already non-regular. A regular path is opened with `openSync(path, constants.O_RDONLY | constants.O_NONBLOCK)` and checked with `fstatSync` on that descriptor. If the descriptor is not a regular file the result is not-a-file; otherwise it is hashed with `readFileSync(fd)` and closed with closeSync in a finally block. The import line gains closeSync, constants, fstatSync and openSync. The mtime mutant now reads `String(fstatSync(fd).mtimeMs)`.
- **PF-292338b0** (mtime scope)
  - staleTree pins H's load-time mtime to `M = 1800000000`.
  - Test (e) says "Controlled mtime offsets apply only to the three hook timestamp cases". The schema cases and the new digest-schema.ts sidecar are plain writes; the sidecar "has no load-time mtime".
  - Test (d) adds the reader's fixed-size, fixed-mtime byte change: H's last byte is changed and its mtime set back to M, with the size and mtime asserted equal. The mutant step now has to show that this case fails too.

BRIEF.md was edited with the edit tool:

- SC-01: adds the same-size fixed-mtime case and the killable, deadline-bounded FIFO process.
- SC-02: adds the JSON PASS, malformed and data-less finalize refusals, Main's unmarked fixture, the four carve-out combinations reaching `validate-digest.py --hook` once with the decoded `digest_object`, and the refused-first versus preserved wording.
- SC-04: the mutant must also fail the SC-01 fixed-mtime case. Controlled mtimes apply to the hook timestamp cases only.
- SC-06: a regular file is read only through the one nonblocking descriptor that fstat confirms is a regular file.

## Q-03

The suffix "While this process is stale, you may yield only a BLOCKED digest that names this cause." appears exactly once in D-02.choice and twice in T-01.intent (handler and P), and that text was not changed. SC-02 in BRIEF only paraphrased the sentence, so it now quotes it literally, after one space following the reason. Main gets no suffix (D-02, T-01, SC-02). T-02.intent describes the refusal in SPEC prose ("may yield only a BLOCKED digest") rather than quoting the suffix. That is outside Q-03's list, so I left it alone.

## Commands

| Command | Exit |
|---|---|
| `plan-merge.py amend … T-01 intent` | 0 |
| `plan-merge.py check --file plan.yaml --root <worktree>` (before panel) | 0 (2 tasks, 3 anchors, 0 failures, no OVERLAP) |
| `plan-merge.py record-panel --digest runs/2026-11-27-03-plan-product/panel-c3.md --cycle 3` | 0 (no findings added; readers scope, should-not-exist and design skipped, goalcheck ran) |
| `plan-merge.py set-panel` (6 dispositions flipped open → resolved, resolved_by T-01) | 0 |
| `plan-merge.py check …` (final) | 0 (2 tasks, 3 anchors, 0 failures) |

check-state side output shows the same VIOLATIONs as cycle 2, none caused by this run: the BRIEF is unapproved, INV-29 (FEAT-2557's worktree) and INV-37 (no Build-entry receipt).

## Final dispositions (16)

All 16 are `resolved` with `resolved_by: T-01`. Severity, kind and summary are untouched.

- **High:** PF-0050f59c, PF-6aff5405.
- **Med:** PF-7f61e5f4, PF-d5952f73, PF-96c39de9, PF-75ab68d5, PF-03296ef9, PF-1cf493dc, PF-3eb8320f, PF-37c5f930.
- **Low:** PF-8a3eeb1b, PF-8ddb5ea0, PF-45feecdf, PF-292338b0, PF-7f19ccf3, PF-298aabb8.

Open by severity: critical 0, high 0, med 0, low 0, unrated 0.

## Not done here

The goal-check runs in a separate dispatch.
