# Simplification — one reader, one angle

You are one of four read-only readers; this is your angle and only your angle. Scope and the
settled set (what is not flaggable) are in your dispatch. Every finding carries five parts: file,
line, one-line summary, the concrete cost, the alternative. **An empty return is a real result.**
The lead's procedure is `harness-simplify`; you do not apply anything.

Flag unnecessary complexity the change adds. Judge a new module or wrapper with the deletion test in
`harness-codebase-design`: delete it in your head, and if complexity vanishes it was a pass-through.

On a **plan surface**: the same fact asserted twice through different spellings, one rule
restated in two places that can drift apart, and dead references to a shape that no longer
exists after a revision.

On a **code surface**: redundant conjuncts, comments that narrate a change instead of stating
the present fact, and pipelines with a simpler equivalent — but **only where the simpler form
preserves the anchoring semantics the original fought for**. An anchor that took rounds to get
right is not complexity to be trimmed.
