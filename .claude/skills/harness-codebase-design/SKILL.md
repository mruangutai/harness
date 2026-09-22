---
name: harness-codebase-design
description: The design vocabulary — deep modules, seams, adapters, depth, leverage, locality — and the principles that turn "architecture review" into a checklist. Loaded by harness-eng-lead and harness-code-reviewer.
user-invocable: false
---

# Codebase design — the vocabulary and its tests

Design **deep modules**: a lot of behaviour behind a small interface, placed at a clean seam,
testable through that interface. Use this language exactly, in dispatches, findings and plans —
consistent language is the point. (Adapted from Matt Pocock's `codebase-design` skill, MIT, and
Lauren Tan's pstack principles, MIT.)

## Glossary

| Term | Means | Never say instead |
|---|---|---|
| **Module** | anything with an interface and an implementation — function, class, package, tier-spanning slice | unit, component, service |
| **Interface** | everything a caller must know: signature PLUS invariants, ordering, error modes, config, performance | API, signature |
| **Seam** | where behaviour can be altered without editing in place — the *location* of an interface. Placing it is its own decision | boundary |
| **Adapter** | a concrete thing satisfying an interface at a seam — a role, not a substance | — |
| **Depth** | leverage at the interface: behaviour exercised per unit of interface learned. Deep = small interface, lots behind it | — |
| **Leverage** | what callers get from depth: one implementation pays back across N call sites and M tests | — |
| **Locality** | what maintainers get: change, bugs and verification concentrate in one place | — |

## The five tests

1. **The deletion test.** Imagine deleting the module. Complexity vanishes → it was a pass-through.
   Complexity reappears across N callers → it was earning its keep. Apply to anything suspected
   shallow; `harness-simplify`'s SIMPLIFICATION reader applies the same test to the changed diff.
2. **The interface is the test surface.** Callers and tests cross the same seam. A test that
   reaches *past* the interface says the module is the wrong shape — and a negative assertion
   scoped past the seam passes vacuously.
3. **One adapter = hypothetical seam; two = real.** Do not introduce a seam until something
   actually varies across it.
4. **State the lifetime with the seam.** An adapter's construction constraint is incomplete
   without its lifetime — "not at import" alone permits a per-request pool; say "lazy on first
   call AND cached for the life of the process." Resource-lifetime defects at seams are invisible
   to gates that inject test doubles across the same seam, so READ the factory on any task wiring
   a pooled or persistent client.
5. **Guards at the boundary, logic pure.** Validate and narrow where data enters (CLI, config,
   network, external APIs); past that seam trust the types — no re-validation, no defensive nil
   checks deep in the chain — and keep business logic in pure functions the shell calls. Expose
   domain types across the seam, never the transport's. The tests: is this data crossing a system
   boundary right now? Can this be a pure function the shell just calls?

## Reader load — the two axes

Maintainability is the work a reader does, on two independent axes: **layers to trace** and
**state to hold**. A flat file with 50 globals is as hard as a six-layer adapter stack; guard both.
Collapse one-caller wrappers and pass-through layers; shrink state scope (returns over mutations,
locals over fields, fields over module state; derive instead of sync); name an invariant once at
the seam. `harness-code-risk-grading` is the measured proxy for the layers axis; every metric is a
proxy, reader load is the thing. **The 30-second test:** can a new reader answer "where does X
come from?" and "what can change X?" in 30 seconds? If not, cut layers or cut state.

## Applying it

- **eng-lead, at dispatch:** name the seam and the interface the task creates or reshapes; state
  adapter lifetimes; when the decision has no precedent in the tree or pm marked the task
  interface-defining, **design it twice** — spawn 2–3 parallel interface designs (a second flavour
  of the first shape does not count), compare on depth, locality and seam placement, then dispatch
  the winner. It does not apply to mechanical implementation of an established pattern, a bug fix
  or refactor with a clear target state, or a change whose constraints leave one viable approach.
- **eng-lead, at architecture review (the post-PASS diff read):** deletion test on new modules;
  no seam without variation; tests cross the interface, not bypass it; lifetimes explicit; guards
  at the boundary only; reader load not raised without a matching reduction elsewhere. Read
  `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-craft/SKILL.md` here (not preloaded, DEC-235)
  and judge the diff against the leaves tagged `eng-lead`.
- **code-reviewer, stage two:** shallow module (interface nearly as complex as its implementation),
  tests reaching past the interface, adapters nothing varies across — each is a finding shape with
  a concrete failure scenario attached, per `harness-code-review`.
