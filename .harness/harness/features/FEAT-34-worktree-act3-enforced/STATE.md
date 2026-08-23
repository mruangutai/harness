# STATE

## Current

- feature: FEAT-34-worktree-act3-enforced
- run: none
- squad: product
- status: in-flight

## Open Questions

- Where the tracked hooks directory lives and how `core.hooksPath` is set per clone — the harness
  and a fleet repository both need it, and whether that is one mechanism or two is undecided. Fog
  in the grilling artifact; pm may sharpen it into a REQ or leave it.
- Whether one `post-merge` firing removes every eligible worktree it finds, or only the feature
  whose merge triggered it. Fog; not sharp enough to be a requirement yet.
