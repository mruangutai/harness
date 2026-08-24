# UI review — FEAT-33 board lifecycle native, Mode B — c0

## Scope

Full diff (`$(git merge-base main HEAD)..HEAD`, pinned `e8a6058`, 72 files) carries zero
html/css/scss/tsx/jsx/vue/svelte/less hits (measured, not inferred) and no `DESIGN.md` exists in
the feature dir (`git cat-file -e` confirms absent). Standard scope-out per repo Expertise P-01
would apply, **except** the dispatch explicitly hands me one adjacent surface: the CLI text an
operator reads to decide whether to apply a bulk board write, plus the 218 live title rewrites.
Reviewed that surface; declined the rest.

## Verdict: PASS, advisory notes only, nothing gates

Two legibility findings on operator-facing CLI/board text. Neither is an accessibility violation
(no colour-only state, no interactive widget, no focus/keyboard surface exists in batch CLI
output), and neither is a contract violation — there is no DESIGN.md to violate, and both design
decisions (`plan.yaml` D-19 for titles, the T-15 intent prose for STATUS findings) considered a
different dimension than the one I'm flagging, so this is a gap the contract left open, not a
breach of something it specified.

## Finding 1 — STATUS finding lines print a full absolute filesystem path; sibling classes don't

`board_lifecycle.py:401` builds every STATUS finding as
`f"STATUS: {feat_dir} records status {status!r} ..."` where `feat_dir` comes from
`_feature_dirs(root)` (`board_lifecycle.py:325-330`) and `root` is always
`os.path.abspath(...)` (`factory_config.py:44-56`) — never relativized. Measured on the captured
run, `audit-after.txt`:

```
board_lifecycle: STATUS: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-33-board-lifecycle-native/.harness/harness/features/FEAT-06-team-layer-inv6 records status 'Done' (column 'Done') but its parent #25 reads None
```

Compare the sibling LABEL/STATION classes on the same report: `LABEL: issue #358 is not_planned
...`, `STATION: issue #297 reads 'Building' ...` — both identify the subject in under 15
characters. The STATUS line makes an operator read past ~120 characters of a machine- and
worktree-specific path (in a worktree checkout — which CLAUDE.md makes mandatory — the feature-id
segment is effectively duplicated, once in the worktree path and once at the tail) before reaching
the feature id that is the actual subject. This is not a one-off artifact of this run: `harness_root()`
is unconditionally absolute, so every future STATUS line on any checkout will carry this shape.
`plan.yaml:1372` (T-15 intent) specifies the message must name "the feature directory" — that's
satisfied literally, but the intent never specified *which form*, and the form chosen is the least
scannable one on the report. Not gating: this doesn't block understanding (the id is present, just
buried), and T-11/T-12's verifies grep by substring so functional correctness is untouched.

## Finding 2 — the title backfill pushes most titles past scannable length, and the contract never checked that dimension

`retitle` (T-16/T-17/T-18) prefixes every task-ticket title with the full feature id
(`<feature-id> — T-NN — <title>`), per D-19 (`plan.yaml:133-135`) and T-16's intent
(`plan.yaml:1445-1456`). Measured directly from the captured live run
(`notes/retitle-harness-preview.txt`, 218 renames, before -> after strings parsed):

| | before | after |
|---|---|---|
| titles > 100 chars | 30 / 218 (14%) | 169 / 218 (78%) |
| max length | 189 | 226 |

The prefix adds 22–38 characters to every title (avg +32). D-19's own rationale measured length
only against GitHub's hard API cap ("worst existing combination is 226 characters ... inside
GitHub's title cap... fail loudly rather than truncate") — a correctness concern, and a reasonable
one. It never measured or weighed the readability cost on a board column that an operator scans
daily on a 539+ item board (the exact question this dispatch asked me to check). Post-backfill,
roughly 4 in 5 task cards on that board carry a title that will wrap to multiple lines or scroll in
a column view. This is a real, measured cost the contract didn't price in — not a defect in what
was built against what was specified, since nothing specified a readability bound. Advisory, not
gating: D-19's stated alternative (a short `FEAT-NN` form) was explicitly rejected for a
correctness reason (a fourth spelling of one name = drift) that the contract weighed and accepted;
I'm not overriding that trade, just naming the readability half of it that wasn't priced.

## What I did not check (rendered-pixel caveat)

I audit source and captured text, not a rendered board. Whether these titles actually wrap,
truncate with an ellipsis, or scroll in GitHub's Projects v2 card view is GitHub's own rendering
behavior and is **not verifiable from source** — human/UAT check required if the operator wants to
know precisely how bad the on-screen effect is, beyond "most titles are now long."

## Not reviewed (genuinely out of remit)

CLI wording correctness (refusal grammar, exit-code semantics), GraphQL correctness, decision
soundness of D-19/D-22/D-23, and the migration reports' narrative accuracy vs the raw captures —
those are lenses other panel seats own (backend-dev / qa / architecture-reviewer).
