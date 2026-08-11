# Observations — harness-product-lead — FEAT-15-domain-product-base

- 2026-08-10: my dispatch relayed the carve-out marker grammar verbatim from the host as
  `execution_mode: main-session-direct — reason: carve-out (...)`. That is FEAT-07's pre-DEC-182
  markdown form and is unloadable in a `plan.yaml` — `templates/plan.yaml:7-8` documents that a
  second `": "` inside a plain scalar fails `safe_load`, and mandates sibling
  `execution_mode`/`execution_reason` keys. pm disobeyed the literal instruction and rendered the
  two keys; had it complied, the plan would not have loaded. Lesson shape: when a dispatch dictates
  a LITERAL field grammar, check it against the owning template before relaying — the host names
  the field, the template owns its syntax, and a verbatim-carry rule turns a stale precedent into a
  broken artifact.

- 2026-08-10: my send-back instrument was worse than pm's. I grepped `test-check-domain.py` for
  product-shaped path fragments and found three flipped expectations; pm resolved each in-root
  allow-assertion against the glob that GRANTS it and found five sites, because `FIXTURE_MANIFEST`
  grants `allowed/**` (line 66) — product-shaped, and invisible to any path grep. pm also bounded
  completeness structurally (in-root the applicable set narrows to `cp_globs ⊆ globs`, so `0 → 2` is
  the only possible flip) where my grep was a sample. Lesson shape: when enumerating what a
  permission change breaks, enumerate over the GRANTING RULE, never over the strings the tests
  happen to contain.

- 2026-08-10: the dispatch asserted the concurrent flows touch disjoint files ("FEAT-14 and this
  feature both care about `.harness/` layout but not the same files"). False by a mechanism no file
  list would show: FEAT-15 T-04 changes what `check-domain.sh --resolve` returns, and FEAT-12's
  APPROVED plan justifies its lane rows with the literal string "check-domain.sh --resolve returns
  harness-documentor". The collision is through a tool both plans consult, not through a shared
  path. Confirms P-08 and widens it: re-derive a disjointness claim over the TOOLS the other
  artifact cites, not only its file lists.
