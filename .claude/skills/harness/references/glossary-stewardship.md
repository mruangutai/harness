# The glossary — keeping the domain's language sharp

Read this when a feature's vocabulary is in play: a term is overloaded, a phrase in the grilling
artifact conflicts with a recorded meaning, or you are about to name something. The rule lives in
`harness-spec-driven` § The glossary (challenge drift before it lands in a perspective; code wins
over a stated meaning); this is the practice. Evidence and history: DEC-149.

`<HARNESS_CONTROL_PLANE_ROOT>/.harness/glossary.md` is the domain's **ubiquitous language**: one
canonical term per concept, no implementation detail — a glossary, never a spec.

- **Challenge drift** — a phrase that conflicts with a recorded term is called out before it
  lands in a perspective, not after the build has guessed which meaning was meant.
- **Sharpen fuzz** — an overloaded term gets a canonical name before an SC is written against it;
  an SC on a fuzzy term is not falsifiable.
- **Code wins** — a stated meaning that contradicts the code is surfaced, not adopted.
- **Update inline** when a term is settled, in the same run. Create the file lazily, on the first
  settled term; an empty glossary is worse than an absent one.
