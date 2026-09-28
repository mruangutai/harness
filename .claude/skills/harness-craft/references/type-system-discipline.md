---
name: type-system-discipline
title: Type System Discipline
description: "Apply when designing types, reviewing a function signature, or writing code in any statically typed language. Make illegal states unrepresentable, brand semantic primitives, parse external data at boundaries, refuse to lie to the compiler, exhaust variants, and derive from authoritative schemas."
seats: [harness-frontend-dev, harness-backend-dev, harness-ai-dev, harness-data-engineer, harness-code-reviewer]
---
# Type System Discipline

The type checker is a proof assistant. Use it to eliminate impossible states, mismatched primitives, and unhandled variants at compile time.

**Why:** A case the types let you ignore becomes a runtime failure the compiler could have stopped. Defining errors and special cases out of existence beats proliferating handlers.

**The patterns:**
- **Make illegal states unrepresentable.** Model variants as sum types (discriminated unions, enums with payloads, sealed classes), not a bag of optional fields where contradictory combinations compile. `{ completed: boolean; completedAt?: Date }` admits `completed: true` with no date; derive the boolean from `completedAt !== null` or model `{ kind: 'open' } | { kind: 'done'; at: Date }`. If a bug forces the question "can this combination actually happen?", the type is too loose.
- **Types are constructions, not restrictions.** Build the type up from the values you want instead of carving them out of a looser type with checks. A non-empty list is a head plus a rest, not a list with a length check; a valid time range is a start plus a duration, not two timestamps you must keep ordered. Choose the shape that cannot build the illegal value and expose the interface callers need on top.
- **Brand semantic primitives.** `UserId` and `OrderId` are strings underneath but must not be interchangeable: newtypes, opaque types, branded intersections. Validate once at creation, trust the type downstream.
- **External data is untyped until parsed.** RPC payloads, JSON, IPC messages, CLI args, config files, environment variables, database rows: a parse function at every boundary turns unstructured input into the typed model.
- **Don't lie to the type system.** Casts, unsafe coercions, and assertion functions that bypass the compiler are latent runtime crashes. If the compiler cannot prove a fact, prove it (validate, narrow, refine the model) or accept that the cast is a hazard.
- **Exhaustive matching is the compiler's job.** A match on a sum type must fail compilation when a variant is added without handling; use the language's idiom (`never`-typed binding, unannotated `match`, incomplete-pattern warnings promoted to errors).
- **Derive types from authoritative schemas.** When a protocol buffer, OpenAPI spec, GraphQL schema, database migration, or design-token file defines a shape, derive from it instead of hand-rolling a parallel type; the generator is the tool that keeps them aligned (`docs/PRINCIPLES.md` rule 13).
- **Strengthen a type only where partiality appears.** A runtime assertion, null check, or "this should never happen" throw marks where a type is too weak. Push that check up into the type, then stop; the type's job is to track the cases each use site must handle, not to describe the data as precisely as possible. Prefer total functions: `sum` of an empty list is 0, so it takes the plain list; `head` of an empty list has no answer, so it demands the non-empty one.

**The tests:**
- "Can I write a comment explaining when this combination of fields is valid?" If yes, the type is too loose; split it into a sum type.
- "Do two of my function arguments share a primitive type but mean different things?" Brand them.
- "Where did this `any`, this `as`, this `assertNotNull` come from?" Trace it to the boundary and validate there instead.
- "If a new variant is added next month, will the compiler tell the next reader where to add a case?" If no, the match is not exhaustive.
- "Is this type duplicating a shape another file owns?" Derive instead.
- "Am I strengthening this type to keep an operation total, or just to be more precise?" If nothing would otherwise panic, keep the plain type.

The structure the types encode comes from `references/model-the-domain.md`.
