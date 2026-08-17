# Observations — harness-visual-designer — FEAT-22-docs-layout-migration

- 2026-08-15: scoped out of FEAT-22 (`needs_prototype: false`, no DESIGN.md). Verified the one
  rendered artifact in the move, `docs/harness/org.html`, is relocation-safe: zero `href`, `src`,
  `<script>`, `<img>`, `<link>`, `<iframe>`, zero `url()`/`@import`/`../`/`window.location`, all CSS
  inline with its own `prefers-color-scheme` + `data-theme` blocks, and zero path-shaped strings
  (`grep -oE '(\.harness|docs/|\.claude)[A-Za-z0-9_./*-]*'` → empty). Also zero live inbound links:
  `git grep 'org\.html'` outside `.harness/harness/features/**` returns nothing, so it is opened by
  hand and the move only changes the path a human types.
- 2026-08-15: checked the four moving `.md` siblings for relative links that a depth change from 2 to
  3 would break — `grep -nE '\]\((\./|\.\./)|\.\./' docs/harness/*.md` is empty. The
  `docs/PRINCIPLES.md` mentions inside `DECISIONS.md` are repo-root-relative prose, not markdown
  relative links, so PRINCIPLES staying behind breaks nothing. Worth remembering: SC-10's sweep hunts
  the `docs/harness` literal, so a relative link would have been invisible to it.
- 2026-08-15: `org.html` names `PLAN.md`, `STATE.md` and `DESIGN.md` as bare filenames. `PLAN.md` is
  stale under DEC-182 (plans are `plan.yaml`) and `DESIGN.md`'s home moved under DEC-129. Pre-existing
  content drift, NOT introduced by the move — same defect class as FEAT-08's MF-2, where `org.html`
  advertised a deleted subsystem because it is hand-maintained with no generator and therefore falls
  outside every task's scope by default. Raised as a non-blocking open question rather than fixed here;
  the dispatch scoped it relocated, not redesigned.
- 2026-08-15: the operator-facing text this feature edits (two gate diagnostic strings, the generated
  index header, `CLAUDE.md` and skill instruction prose) is terminal and instruction text. It carries
  no palette, type scale, spacing or component decision, so nothing in it is gradeable against a design
  contract. Correctness of those strings is pinned by T-06's per-file check and SC-06 — a code concern,
  not mine.
