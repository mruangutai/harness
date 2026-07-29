---
name: harness-codebase-design
description: The design vocabulary — deep modules, seams, adapters, depth, leverage, locality — and the principles that turn "architecture review" into a checklist. Loaded by harness-eng-lead and harness-code-reviewer.
---

# Codebase design — the vocabulary and its tests

Design **deep modules**: a lot of behaviour behind a small interface, placed at a clean seam,
testable through that interface. Use this language exactly, in dispatches, findings and plans —
consistent language is the point. (Adapted from Matt Pocock's `codebase-design` skill, MIT.)

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

## The four tests

1. **The deletion test.** Imagine deleting the module. Complexity vanishes → it was a pass-through.
   Complexity reappears across N callers → it was earning its keep. Apply to anything suspected
   shallow.
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

## Applying it

- **eng-lead, at dispatch:** name the seam and the interface the task creates or reshapes; state
  adapter lifetimes; for a task pm marked interface-defining, consider **design-it-twice** — spawn
  2–3 parallel interface designs, compare on depth, locality and seam placement, then dispatch the
  winner.
- **eng-lead, at architecture review (the post-PASS diff read):** deletion test on new modules;
  no seam without variation; tests cross the interface, not bypass it; lifetimes explicit.
- **code-reviewer, stage two:** shallow module (interface nearly as complex as its implementation),
  tests reaching past the interface, adapters nothing varies across — each is a finding shape with
  a concrete failure scenario attached, per `harness-code-review`.

Depth is a property of the **interface**, not the implementation — a deep module may be internally
composed of small swappable parts with **internal seams** its own tests use; they are just not part
of the interface.
